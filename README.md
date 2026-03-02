# Competitive Positioning Map

An embeddings-based analysis layer that sits on top of a competitive intelligence monitor and turns raw competitor website copy into a visual map of how companies cluster in a market — plus a written brief that tells you what to actually do about it.

This isn't just LLM prompt engineering. It uses real ML infrastructure: sentence embeddings, cosine similarity, and UMAP dimensionality reduction to compute genuine geometric relationships between company positions in high-dimensional space.

---

## What it does

Given a set of competitor websites, the pipeline:

1. **Extracts structured positioning data** — Claude reads each company's homepage and returns a JSON schema with value propositions, target audience, key claims, differentiators, brand tone, and a two-sentence positioning summary.
2. **Builds semantic embeddings** — the structured data is flattened into a single positioning string per company and encoded with `all-MiniLM-L6-v2` into a 384-dimensional vector. Companies that say similar things end up close together in this space.
3. **Computes cosine similarity** — every competitor is scored against your company. A score of 1.0 means identical positioning; 0.0 means totally different.
4. **Reduces to 2D with UMAP** — the high-dimensional embeddings are projected into two dimensions so clusters become visually obvious without losing the relative geometry.
5. **Renders an interactive map** — a Plotly HTML scatter plot where proximity means positioning similarity. Your company appears as a star; hover over any point to see the positioning summary and similarity score.
6. **Tracks positioning shifts over time** — every run stores a snapshot in SQLite. Once you have multiple runs, a second timeline map draws dotted trajectories showing where each company has moved.
7. **Writes a competitive intelligence brief** — Claude synthesises the structured data and similarity scores into a 300–400 word analysis covering positioning clusters, specific threats, white space, and concrete recommendations.

---

## How it works

```
competitive-intel-monitor/
  snapshots/
    competitor.com.json   ←── scraped website text + timestamp
    ...

         │
         ▼ connect_to_project2()

[1] Raw text per company
         │
         ▼ messaging_extractor.py  (Claude claude-opus-4-6)

[2] Structured positioning dict
    { value_propositions, target_audience,
      key_claims, differentiators, tone,
      positioning_summary }
         │
         ▼ create_embedding_text()

[3] Flat positioning string
    "value prop 1 value prop 2 | audience | claims | ..."
         │
         ▼ embedding_engine.py  (sentence-transformers all-MiniLM-L6-v2)

[4] 384-dimensional unit-normalised vector per company
         │
         ├──▶ cosine similarity vs. your company (dot product)
         │
         ▼ visualization.py  (UMAP n_components=2, metric=cosine)

[5] 2D coordinates
         │
         ├──▶ outputs/positioning_map.html       (Plotly scatter)
         ├──▶ outputs/positioning_timeline.html  (if historical data exists)
         │
         ▼ database.py  (SQLite)

[6] Snapshot stored → feeds future timeline maps
         │
         ▼ narrative_analysis.py  (Claude claude-opus-4-6)

[7] outputs/competitive_analysis.md
```

---

## Tech stack

| Layer | Tool |
|---|---|
| Structured extraction | Anthropic Claude (`claude-opus-4-6`) via `anthropic` SDK |
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` (384 dims) |
| Dimensionality reduction | `umap-learn` — cosine metric, 2D projection |
| Similarity | Cosine similarity via numpy dot product (unit-normalised vectors) |
| Storage | SQLite via Python `sqlite3` — snapshots with embedded vectors |
| Visualisation | `plotly` — interactive HTML, no server required |
| Narrative analysis | Anthropic Claude (`claude-opus-4-6`) |
| Config | `python-dotenv` |

Python 3.11+.

---

## Setup

```bash
# Clone and enter the project
git clone <repo-url>
cd competitive-positioning-map

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install anthropic sentence-transformers umap-learn plotly numpy python-dotenv
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_key_here
```

---

## Running it

### Demo mode (no API calls, no cost)

Good for testing the pipeline and visualisations with pre-baked sample data:

```bash
python pipeline.py --demo
```

### Demo + simulate historical data

Seeds 6 weeks of synthetic position snapshots so the timeline map works immediately:

```bash
python pipeline.py --simulate
```

(`--simulate` implies `--demo` — it won't burn API credits.)

### Live mode

Calls Claude to extract real positioning from competitor text and generates a real analysis brief:

```bash
python pipeline.py
```

This makes one Claude API call per competitor (extraction) plus one for the final brief. With 6 competitors that's 7 calls total.

### Outputs

After a run you'll find:

```
outputs/
  positioning_map.html       # interactive 2D positioning scatter
  positioning_timeline.html  # positioning drift over time (if snapshots exist)
  competitive_analysis.md    # written competitive intelligence brief
data/
  positioning.db             # SQLite snapshot store
```

Open the HTML files directly in a browser — no server needed.

---

## Connecting to the competitive intel monitor

This project is designed to plug into a companion scraper project (`competitive-intel-monitor`) as a shared data layer. The scraper's job is fetching and storing raw website text; this project's job is turning that text into positioning intelligence.

**Expected directory layout:**

```
parent-folder/
  competitive-intel-monitor/
    snapshots/
      trustandwill.com.json
      wealth.com.json
      ...
  competitive-positioning-map/   ← you are here
```

**Snapshot file format** (what the monitor should write):

```json
{ "text": "full scraped homepage text...", "timestamp": "2025-03-01T14:22:00" }
```

Or a list if the monitor stores multiple snapshots per file:

```json
[
  { "text": "...", "timestamp": "2025-02-01T09:00:00" },
  { "text": "...", "timestamp": "2025-03-01T14:22:00" }
]
```

When a list is present, the pipeline picks the entry with the most recent timestamp. The snapshot path is configured in `config.py`:

```python
SNAPSHOTS_PATH = "../competitive-intel-monitor/snapshots"
```

Change this to point anywhere. If the path doesn't exist or a file is missing for a competitor, the pipeline falls back to built-in sample data and logs a warning — so partial integration works fine while you're getting set up.

**Adding or changing competitors** is done in `config.py` under `COMPETITORS`. Each entry needs a `name`, `url`, `color` (hex, used in the map), and `is_you: True` for the company you're benchmarking against. Everything else derives from that config.

---

## What's actually ML here

To be specific about what's happening under the hood vs. what's just prompting:

- **`all-MiniLM-L6-v2`** is a fine-tuned BERT-based model that maps text into a 384-dimensional semantic space. It runs locally — no API call, no cost per run.
- **Unit normalisation** means cosine similarity reduces to a dot product, which is how the similarity scores are computed in `embedding_engine.py`.
- **UMAP** (Uniform Manifold Approximation and Projection) is a nonlinear dimensionality reduction algorithm. It preserves local neighborhood structure, so companies that are genuinely similar in the full 384D space end up near each other in the 2D projection — not just arbitrarily placed.
- **The timeline map** embeds all snapshots (across all companies, all time) in a single UMAP pass so historical and current positions share the same coordinate space and drift is geometrically meaningful.

Claude handles two things that are genuinely hard to do with embeddings alone: extracting structured signal from messy marketing copy, and synthesising similarity scores into a readable strategic brief. The rest is math.
