import textwrap
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import umap

from config import COMPETITORS


def reduce_dimensions(embeddings: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Project high-dimensional embeddings down to 2D using UMAP.

    Args:
        embeddings: Dict mapping company_key to normalised embedding array.

    Returns:
        Dict mapping company_key to a 2-element numpy array [x, y].
    """
    keys = list(embeddings.keys())
    matrix = np.stack([embeddings[k] for k in keys])

    n_neighbors = min(3, len(keys) - 1)

    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=n_neighbors,
        min_dist=0.3,
        metric="cosine",
        random_state=42,
    )
    coords = reducer.fit_transform(matrix)

    return {key: coords[i] for i, key in enumerate(keys)}


def create_positioning_map(
    coords: dict[str, np.ndarray],
    messaging_data: dict[str, dict],
    similarities: dict[str, float] | None = None,
    output_path: str = "outputs/positioning_map.html",
) -> str:
    """Build an interactive Plotly scatter map of competitive positioning.

    Each company is one trace so legend entries are labelled. Valur (is_you=True)
    appears as a star; competitors appear as circles.

    Args:
        coords:        Dict of company_key → 2D coordinate array from reduce_dimensions.
        messaging_data: Dict of company_key → messaging dict from extract_messaging.
        similarities:  Optional dict of company_key → cosine similarity score vs. Valur.
        output_path:   Destination HTML file path.

    Returns:
        Absolute path of the written HTML file.
    """
    fig = go.Figure()

    for key, xy in coords.items():
        competitor = COMPETITORS.get(key, {})
        name = competitor.get("name", key)
        color = competitor.get("color", "#888888")
        is_you = competitor.get("is_you", False)

        messaging = messaging_data.get(key, {})
        summary = messaging.get("positioning_summary", "")
        tone = messaging.get("tone", "")

        wrapped_summary = "<br>".join(textwrap.wrap(summary, width=60))

        hover_parts = [f"<b>{name}</b>", wrapped_summary]
        if tone:
            hover_parts.append(f"Tone: {tone}")
        if similarities and key in similarities:
            hover_parts.append(f"Similarity to Valur: {similarities[key]:.2f}")
        hover_text = "<br>".join(hover_parts)

        if is_you:
            marker_symbol = "star"
            marker_size = 20
        else:
            marker_symbol = "circle"
            marker_size = 14

        fig.add_trace(go.Scatter(
            x=[xy[0]],
            y=[xy[1]],
            mode="markers+text",
            name=name,
            text=[name],
            textposition="top center",
            hovertemplate=hover_text + "<extra></extra>",
            marker=dict(
                symbol=marker_symbol,
                size=marker_size,
                color=color,
                line=dict(width=1.5, color="white"),
            ),
        ))

    fig.update_layout(
        title=dict(
            text="Competitive Positioning Map",
            font=dict(size=20),
        ),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title=""),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title=""),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="v", x=1.02, y=1),
        annotations=[
            dict(
                text="★ = your company (Valur) · proximity indicates positioning similarity",
                xref="paper",
                yref="paper",
                x=0.5,
                y=-0.05,
                showarrow=False,
                font=dict(size=12, color="#555555"),
                xanchor="center",
            )
        ],
        margin=dict(l=40, r=160, t=60, b=60),
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(out), include_plotlyjs=True)
    return str(out.resolve())


def create_time_series_map(
    snapshots: list[dict],
    output_path: str = "outputs/positioning_timeline.html",
) -> str | None:
    """Build an interactive Plotly map showing how positioning has shifted over time.

    All snapshots (across all companies) are embedded together in one UMAP pass so
    every point lives in a shared coordinate space. For each company a dotted line
    connects historical positions, with faded dots for older snapshots and a large
    opaque dot for the most recent one.

    Args:
        snapshots:   List of snapshot dicts as returned by get_historical_snapshots.
        output_path: Destination HTML file path.

    Returns:
        Absolute path of the written HTML file, or None if there are too few snapshots.
    """
    if len(snapshots) < 2:
        print("Not enough snapshots to build a time-series map (need at least 2).")
        return None

    # ── 1. Reduce all snapshot embeddings together ───────────────────────────
    all_embeddings = np.stack([s["embedding"] for s in snapshots])
    n_neighbors = min(3, len(snapshots) - 1)

    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=n_neighbors,
        min_dist=0.3,
        metric="cosine",
        random_state=42,
    )
    all_coords = reducer.fit_transform(all_embeddings)

    # ── 2. Group results by company, preserving chronological order ──────────
    company_snapshots: dict[str, list[dict]] = {}
    for i, snap in enumerate(snapshots):
        key = snap["company_key"]
        company_snapshots.setdefault(key, []).append({
            **snap,
            "_xy": all_coords[i],
        })

    for entries in company_snapshots.values():
        entries.sort(key=lambda s: s["timestamp"])

    # ── 3. Build figure ──────────────────────────────────────────────────────
    fig = go.Figure()

    for key, entries in company_snapshots.items():
        competitor = COMPETITORS.get(key, {})
        name = competitor.get("name", key)
        color = competitor.get("color", "#888888")
        is_you = competitor.get("is_you", False)

        xs = [e["_xy"][0] for e in entries]
        ys = [e["_xy"][1] for e in entries]

        # Dotted line connecting historical positions
        fig.add_trace(go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            name=name,
            showlegend=False,
            line=dict(color=color, width=1.5, dash="dot"),
            hoverinfo="skip",
        ))

        # Faded dots for all but the most recent snapshot
        if len(entries) > 1:
            fig.add_trace(go.Scatter(
                x=xs[:-1],
                y=ys[:-1],
                mode="markers",
                name=name,
                showlegend=False,
                hovertemplate=(
                    f"<b>{name}</b><br>"
                    "%{customdata}<extra></extra>"
                ),
                customdata=[e["timestamp"][:10] for e in entries[:-1]],
                marker=dict(
                    symbol="circle",
                    size=8,
                    color=color,
                    opacity=0.35,
                    line=dict(width=1, color="white"),
                ),
            ))

        # Large opaque dot + label for the most recent snapshot
        latest = entries[-1]
        marker_symbol = "star" if is_you else "circle"
        marker_size = 20 if is_you else 14

        messaging = latest.get("messaging", {})
        summary = latest.get("embedding_text", messaging.get("positioning_summary", ""))
        wrapped = "<br>".join(textwrap.wrap(summary[:200], width=60))

        fig.add_trace(go.Scatter(
            x=[xs[-1]],
            y=[ys[-1]],
            mode="markers+text",
            name=name,
            text=[name],
            textposition="top center",
            hovertemplate=(
                f"<b>{name}</b> (latest)<br>"
                f"{wrapped}<br>"
                f"Date: {latest['timestamp'][:10]}"
                "<extra></extra>"
            ),
            marker=dict(
                symbol=marker_symbol,
                size=marker_size,
                color=color,
                opacity=1.0,
                line=dict(width=1.5, color="white"),
            ),
        ))

    fig.update_layout(
        title=dict(
            text="Positioning Timeline",
            font=dict(size=20),
        ),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title=""),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, title=""),
        plot_bgcolor="white",
        paper_bgcolor="white",
        annotations=[
            dict(
                text=(
                    "★ = your company (Valur) · large dot = most recent · "
                    "faded dots = historical positions · dotted line = trajectory"
                ),
                xref="paper",
                yref="paper",
                x=0.5,
                y=-0.05,
                showarrow=False,
                font=dict(size=12, color="#555555"),
                xanchor="center",
            )
        ],
        margin=dict(l=40, r=40, t=60, b=60),
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(out), include_plotlyjs=True)
    return str(out.resolve())
