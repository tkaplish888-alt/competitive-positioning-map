"""
Main orchestrator for the competitive positioning pipeline.

Usage:
    python pipeline.py            # live mode  — calls Claude APIs
    python pipeline.py --demo     # demo mode  — skips all Claude API calls
    python pipeline.py --simulate # seeds historical snapshots with synthetic noise,
                                  # then runs in demo mode (enables time-series map)
    python pipeline.py --demo --simulate
"""

import sys
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from config import COMPETITORS, SNAPSHOTS_PATH
from messaging_extractor import extract_messaging, create_embedding_text
from embedding_engine import batch_embed, compute_similarity
from database import (
    init_db,
    store_snapshot,
    get_latest_snapshots,
    get_historical_snapshots,
    get_snapshot_count,
)
from visualization import reduce_dimensions, create_positioning_map, create_time_series_map
from narrative_analysis import generate_analysis
import sample_data


# ── Scraper bridge ────────────────────────────────────────────────────────────

def connect_to_project2() -> dict[str, str]:
    """Return a mapping of company_key → raw homepage text.

    Reads competitor snapshot JSON files from SNAPSHOTS_PATH (configured in
    config.py).  Each JSON file must contain either:
      - A single object: {"text": "...", "timestamp": "..."}
      - A list of objects: [{"text": "...", "timestamp": "..."}, ...]
    When a list is present the entry with the most recent timestamp is used.

    The matching snapshot file is located by searching for a filename that
    contains the competitor's domain (e.g. "valur.com" matches "valur.com.json").

    Falls back to sample_data.SAMPLE_PAGES per company if:
      - SNAPSHOTS_PATH does not exist
      - No matching file is found for a competitor
      - The file cannot be parsed or contains no text
    """
    from urllib.parse import urlparse

    snapshots_dir = Path(SNAPSHOTS_PATH)

    if not snapshots_dir.exists():
        print(f"[connect_to_project2] Snapshots folder '{SNAPSHOTS_PATH}' not found — using sample data for all companies.")
        return dict(sample_data.SAMPLE_PAGES)

    pages: dict[str, str] = {}

    for key, cfg in COMPETITORS.items():
        domain = urlparse(cfg["url"]).netloc.removeprefix("www.")
        matching = list(snapshots_dir.glob(f"*{domain}*.json"))

        if not matching:
            print(f"[connect_to_project2] No snapshot file found for {cfg['name']} ({domain}) — falling back to sample data.")
            pages[key] = sample_data.SAMPLE_PAGES.get(key, "")
            continue

        snapshot_path = matching[0]
        try:
            data = json.loads(snapshot_path.read_text(encoding="utf-8"))

            # Support both a list of snapshots and a single snapshot object.
            if isinstance(data, list):
                if not data:
                    raise ValueError("snapshot list is empty")
                data = max(data, key=lambda e: e.get("timestamp", ""))

            text = data.get("text", "").strip()
            if not text:
                raise ValueError("'text' field is empty")

            pages[key] = text

        except Exception as exc:
            print(f"[connect_to_project2] Could not read snapshot for {cfg['name']} ({snapshot_path.name}): {exc} — falling back to sample data.")
            pages[key] = sample_data.SAMPLE_PAGES.get(key, "")

    return pages


# ── Demo analysis (no Claude call) ───────────────────────────────────────────

_DEMO_ANALYSIS = """\
# Competitive Intelligence Brief — Valur (Demo)

**Positioning Clusters**

The market divides into two clear groups. Trust & Will and Gentreo cluster together at the
accessibility end, both relying on speed, low cost, and ease-of-use language — phrases like
"every family deserves" and "under 15 minutes" signal that their primary job is converting
the unplanned majority. Wealth.com and Vanilla form a second cluster aimed squarely at
financial advisors, framing estate planning as a practice-management and retention tool
rather than a consumer product. Holistiplan sits adjacent to this advisor cluster but pivots
toward tax planning rather than estate documents, giving it a distinct niche.

**Threat Assessment**

Wealth.com represents the highest near-term positioning risk to Valur. Its language around
"sophisticated" clients, advisor integration, and "turning estate planning into a retention
advantage" overlaps with Valur's affluent-family target segment — the advisors who serve
Valur's customers are the same advisors Wealth.com is actively recruiting as channel partners.
If Wealth.com succeeds in owning that advisor relationship, it could disintermediate Valur
before a prospect ever reaches valur.com.

**White Space**

Nobody in this competitive set is explicitly claiming the intergenerational wealth *conversation*
— the emotional and relational side of transferring assets, values, and intentions alongside
legal documents. The market is saturated with execution language (documents, strategies, tools)
but silent on the human dimensions of legacy planning. This is an open lane.

**Recommendations**

First, Valur should sharpen its language around the advisor channel before Wealth.com locks it
in. Positioning as the platform advisors recommend to their $2M–$15M clients — rather than a
direct competitor to advisory services — would neutralise the disintermediation risk and create
a referral flywheel. Second, piloting messaging around "legacy conversations" or "family wealth
narrative" would stake a claim in the emotional white space no competitor is currently occupying,
differentiating Valur from the document-and-strategy framing everyone else uses.
"""


# ── Simulation helpers ────────────────────────────────────────────────────────

def _add_noise(embedding: np.ndarray, scale: float = 0.04) -> np.ndarray:
    """Return a unit-normalised copy of embedding with small Gaussian noise added."""
    noisy = embedding + np.random.normal(0, scale, embedding.shape).astype(np.float32)
    return (noisy / np.linalg.norm(noisy)).astype(np.float32)


def _simulate_history(
    messaging_data: dict[str, dict],
    embedding_texts: dict[str, str],
    embeddings: dict[str, np.ndarray],
    weeks: int = 6,
) -> None:
    """Store synthetic historical snapshots going back `weeks` weeks.

    Each week's embeddings are a slightly noisy version of the current ones,
    creating a plausible drift trajectory that makes the time-series map useful
    before real historical data has accumulated.
    """
    now = datetime.now()
    print(f"\n[simulate] Writing {weeks} weeks of synthetic history...")

    for week in range(weeks, 0, -1):
        ts = (now - timedelta(weeks=week)).isoformat()
        for key, cfg in COMPETITORS.items():
            if key not in embeddings:
                continue
            noisy_emb = _add_noise(embeddings[key])
            store_snapshot(
                company_key=key,
                company_name=cfg["name"],
                messaging=messaging_data[key],
                embedding_text=embedding_texts[key],
                embedding=noisy_emb,
                timestamp=ts,
            )

    print(f"[simulate] Done — {weeks * len(COMPETITORS)} synthetic rows inserted.\n")


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_pipeline(demo_mode: bool = False, simulate: bool = False) -> None:
    mode_label = "DEMO" if demo_mode else "LIVE"
    print(f"\n{'='*60}")
    print(f"  Competitive Positioning Pipeline  [{mode_label}]")
    print(f"{'='*60}\n")

    # ── 1. Initialise database ────────────────────────────────────────────────
    print("[1/8] Initialising database...")
    init_db()

    # ── 2. Fetch raw text ─────────────────────────────────────────────────────
    print("[2/8] Fetching competitor pages...")
    raw_texts = connect_to_project2()

    # ── 3. Extract structured messaging ──────────────────────────────────────
    print("[3/8] Extracting messaging...")
    messaging_data: dict[str, dict] = {}

    for key, cfg in COMPETITORS.items():
        if demo_mode:
            messaging_data[key] = sample_data.SAMPLE_MESSAGING[key]
            print(f"      {cfg['name']:20s}  [sample]")
        else:
            raw = raw_texts.get(key, "")
            if not raw:
                print(f"      {cfg['name']:20s}  [SKIPPED — no text]")
                continue
            print(f"      {cfg['name']:20s}  [calling Claude...]", end="", flush=True)
            messaging_data[key] = extract_messaging(cfg["name"], raw)
            print(" done")

    # ── 4. Build embedding texts ──────────────────────────────────────────────
    print("[4/8] Building embedding strings...")
    embedding_texts: dict[str, str] = {
        key: create_embedding_text(msg)
        for key, msg in messaging_data.items()
    }

    # ── 5. Batch embed ────────────────────────────────────────────────────────
    print("[5/8] Embedding positioning texts (batch)...")
    embeddings = batch_embed(embedding_texts)

    # ── 6. Compute similarities & print ──────────────────────────────────────
    print("[6/8] Computing cosine similarities vs. Valur...\n")
    your_key = next(k for k, v in COMPETITORS.items() if v.get("is_you"))
    your_embedding = embeddings[your_key]

    similarities: dict[str, float] = {}
    for key, emb in embeddings.items():
        if key == your_key:
            continue
        score = compute_similarity(your_embedding, emb)
        similarities[key] = score
        name = COMPETITORS[key]["name"]
        bar = "█" * int(score * 30)
        print(f"      {name:20s}  {score:.3f}  {bar}")
    print()

    # ── 7. Store current snapshots ────────────────────────────────────────────
    print("[7/8] Storing snapshots...")
    ts_now = datetime.now().isoformat()
    for key, msg in messaging_data.items():
        store_snapshot(
            company_key=key,
            company_name=COMPETITORS[key]["name"],
            messaging=msg,
            embedding_text=embedding_texts[key],
            embedding=embeddings[key],
            timestamp=ts_now,
        )

    # Optionally seed synthetic history so the time-series map works immediately
    if simulate:
        _simulate_history(messaging_data, embedding_texts, embeddings)

    total_rows = get_snapshot_count()
    print(f"      Database now contains {total_rows} snapshot(s).\n")

    # ── 8. Visualise ──────────────────────────────────────────────────────────
    print("[8/8] Generating visualisations...")

    coords = reduce_dimensions(embeddings)
    map_path = create_positioning_map(
        coords=coords,
        messaging_data=messaging_data,
        similarities=similarities,
    )
    print(f"      Positioning map  → {map_path}")

    timeline_path = None
    all_snapshots = get_historical_snapshots()
    if len(all_snapshots) > len(COMPETITORS):
        timeline_path = create_time_series_map(all_snapshots)
        if timeline_path:
            print(f"      Timeline map     → {timeline_path}")
    else:
        print(
            f"      Timeline map     [skipped — need >{len(COMPETITORS)} snapshots, "
            f"have {len(all_snapshots)}; run with --simulate to seed history]"
        )

    # ── Analysis ──────────────────────────────────────────────────────────────
    your_name = COMPETITORS[your_key]["name"]
    if demo_mode:
        analysis_text = _DEMO_ANALYSIS
        print("\n      Analysis         [demo text used]")
    else:
        print("\n      Generating narrative analysis (Claude)...", end="", flush=True)
        analysis_text = generate_analysis(
            your_company=your_name,
            messaging_data=messaging_data,
            similarities=similarities,
        )
        print(" done")

    analysis_path = Path("outputs/competitive_analysis.md")
    analysis_path.parent.mkdir(parents=True, exist_ok=True)
    analysis_path.write_text(
        f"# Competitive Analysis — {your_name}\n"
        f"_Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n"
        + analysis_text,
        encoding="utf-8",
    )

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  Output files")
    print(f"{'='*60}")
    print(f"  Positioning map   {map_path}")
    if timeline_path:
        print(f"  Timeline map      {timeline_path}")
    print(f"  Analysis brief    {analysis_path.resolve()}")
    print(f"  Database          {Path('data/positioning.db').resolve()}")
    print(f"{'='*60}\n")


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    demo_mode = "--demo" in args
    simulate = "--simulate" in args

    if simulate and not demo_mode:
        # --simulate implies demo so we don't burn API credits on synthetic runs
        demo_mode = True

    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    run_pipeline(demo_mode=demo_mode, simulate=simulate)
