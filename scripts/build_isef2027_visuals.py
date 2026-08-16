#!/usr/bin/env python3
"""Build high-quality + animated 3D visualizations of RISHI-Q scientific concepts.

Outputs interactive HTML (Plotly) under visuals/isef2027/ for local viewing.
No scientific conclusions — concept illustrations only.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "visuals/isef2027"


def _plotly_available() -> bool:
    try:
        import plotly.graph_objects as go  # noqa: F401

        return True
    except ImportError:
        return False


def ensure_plotly():
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    return go, make_subplots


def fig_akasa_sound_field_3d(go):
    """Pervasive medium with sound propagation vs separate tejas heat carrier."""
    rng = np.random.default_rng(42)
    # Medium points (ākāśa volume)
    n = 400
    x = rng.normal(0, 1.2, n)
    y = rng.normal(0, 1.2, n)
    z = rng.normal(0, 1.2, n)
    # Sound wavefronts as spheres of intensity
    t = np.linspace(0, 4 * np.pi, 80)
    path_x = 1.8 * np.sin(t)
    path_y = 1.8 * np.cos(t)
    path_z = 0.35 * np.sin(2 * t)

    # Tejas cluster offset
    tx = 3.2 + rng.normal(0, 0.35, 120)
    ty = rng.normal(0, 0.35, 120)
    tz = rng.normal(0, 0.35, 120)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=x, y=y, z=z, mode="markers",
            marker=dict(size=2.5, color="#64748b", opacity=0.35),
            name="ākāśa (pervasive medium)",
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=path_x, y=path_y, z=path_z, mode="lines+markers",
            line=dict(color="#1d4ed8", width=6),
            marker=dict(size=3, color="#93c5fd"),
            name="śabda (sound mark / propagation)",
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=tx, y=ty, z=tz, mode="markers",
            marker=dict(size=4, color="#ea580c", opacity=0.85),
            name="tejas (heat/light carrier — distinct)",
        )
    )
    fig.update_layout(
        title="Concept: Vaiśeṣika sound-marked medium vs distinct tejas",
        scene=dict(
            xaxis_title="x", yaxis_title="y", zaxis_title="z",
            bgcolor="#0b1220",
            xaxis=dict(backgroundcolor="#0b1220", gridcolor="#1e293b"),
            yaxis=dict(backgroundcolor="#0b1220", gridcolor="#1e293b"),
            zaxis=dict(backgroundcolor="#0b1220", gridcolor="#1e293b"),
        ),
        paper_bgcolor="#0b1220",
        font=dict(color="#e2e8f0"),
        legend=dict(bgcolor="#0f172a"),
        margin=dict(l=0, r=0, t=50, b=0),
        height=720,
    )
    return fig


def fig_maxwell_field_3d(go):
    """Simplified EM field lines + light as field excitation (illustration)."""
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 20)
    # Field line helices
    traces = []
    for i, r in enumerate([0.6, 1.0, 1.4]):
        t = np.linspace(0, 6 * np.pi, 200)
        traces.append(
            go.Scatter3d(
                x=r * np.cos(t),
                y=r * np.sin(t),
                z=t / 6,
                mode="lines",
                line=dict(width=4, color=["#22d3ee", "#38bdf8", "#818cf8"][i]),
                name=f"EM field line {i+1}",
            )
        )
    # Light pulse along axis
    z = np.linspace(0, np.pi, 80)
    traces.append(
        go.Scatter3d(
            x=0.15 * np.sin(12 * z),
            y=0.15 * np.cos(12 * z),
            z=z,
            mode="lines",
            line=dict(width=8, color="#fbbf24"),
            name="light as EM excitation",
        )
    )
    fig = go.Figure(data=traces)
    fig.update_layout(
        title="Concept: Maxwell — light as excitation of one EM field (not sound-defined)",
        scene=dict(bgcolor="#0b1220", xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"), zaxis=dict(gridcolor="#1e293b")),
        paper_bgcolor="#0b1220",
        font=dict(color="#e2e8f0"),
        height=720,
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig


def fig_tradition_embedding_3d(go):
    """PCA-like 3D layout of six-tradition R1–R6 vectors (from frozen exploratory)."""
    # Order R1..R6 from expansion_v2
    names = ["Vaiśeṣika", "Lucretius", "Timaeus", "Dao De Jing", "Dhammapada", "Maxwell"]
    V = np.array(
        [
            [1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 0],
            [1, 0, 1, 1, 1, 0],
            [1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0],
            [1, 0, 0, 1, 0, 1],
        ],
        dtype=float,
    )
    # Simple deterministic 3D projection via top singular vectors
    V0 = V - V.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(V0, full_matrices=False)
    coords = V0 @ vt[:3].T
    colors = ["#22c55e", "#94a3b8", "#94a3b8", "#94a3b8", "#94a3b8", "#f59e0b"]
    sizes = [16, 10, 10, 10, 10, 14]
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=coords[:, 0],
                y=coords[:, 1],
                z=coords[:, 2],
                mode="markers+text",
                text=names,
                textposition="top center",
                marker=dict(size=sizes, color=colors, opacity=0.95, line=dict(width=1, color="#e2e8f0")),
            )
        ]
    )
    fig.update_layout(
        title="Exploratory geometry: six-tradition R1–R6 vectors (PCA-style 3D)",
        scene=dict(bgcolor="#0b1220", xaxis_title="PC1", yaxis_title="PC2", zaxis_title="PC3",
                   xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"), zaxis=dict(gridcolor="#1e293b")),
        paper_bgcolor="#0b1220",
        font=dict(color="#e2e8f0"),
        height=720,
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig


def fig_concept_graph_3d(go):
    """3D layout of template ākāśa vs Maxwell concept-graph nodes/edges."""
    # Load templates if present
    ak_path = ROOT / "ontology/concept_graph/template_vaisesika_akasa_sabda.json"
    mx_path = ROOT / "ontology/concept_graph/template_maxwell_em.json"
    nodes = []
    edges = []
    if ak_path.exists():
        ak = json.loads(ak_path.read_text())
        for i, n in enumerate(ak["nodes"]):
            nodes.append((n["id"], n["label"], "akasa", i))
        for e in ak["edges"]:
            edges.append((e["source"], e["target"], "#3b82f6"))
    if mx_path.exists():
        mx = json.loads(mx_path.read_text())
        offset = 5
        for i, n in enumerate(mx["nodes"]):
            nodes.append((n["id"] + "_m", n["label"], "maxwell", i + offset))
        for e in mx["edges"]:
            edges.append((e["source"] + "_m", e["target"] + "_m", "#f59e0b"))

    # Place nodes on two rings
    pos = {}
    ak_nodes = [n for n in nodes if n[2] == "akasa"]
    mx_nodes = [n for n in nodes if n[2] == "maxwell"]
    for i, (nid, lab, _, _) in enumerate(ak_nodes):
        ang = 2 * np.pi * i / max(len(ak_nodes), 1)
        pos[nid] = (np.cos(ang), np.sin(ang), 0.0)
    for i, (nid, lab, _, _) in enumerate(mx_nodes):
        ang = 2 * np.pi * i / max(len(mx_nodes), 1)
        pos[nid] = (3.5 + np.cos(ang), np.sin(ang), 1.2)

    edge_traces = []
    for s, t, col in edges:
        if s in pos and t in pos:
            x0, y0, z0 = pos[s]
            x1, y1, z1 = pos[t]
            edge_traces.append(
                go.Scatter3d(
                    x=[x0, x1, None], y=[y0, y1, None], z=[z0, z1, None],
                    mode="lines", line=dict(color=col, width=4), hoverinfo="none", showlegend=False,
                )
            )
    node_x, node_y, node_z, texts, cols = [], [], [], [], []
    for nid, lab, fam, _ in nodes:
        if nid not in pos:
            continue
        x, y, z = pos[nid]
        node_x.append(x); node_y.append(y); node_z.append(z)
        texts.append(lab)
        cols.append("#60a5fa" if fam == "akasa" else "#fbbf24")

    fig = go.Figure(data=edge_traces + [
        go.Scatter3d(
            x=node_x, y=node_y, z=node_z, mode="markers+text", text=texts,
            textposition="top center",
            marker=dict(size=10, color=cols, line=dict(width=1, color="white")),
            name="nodes",
        )
    ])
    fig.update_layout(
        title="TEMPLATE concept graphs in 3D (ākāśa–śabda vs Maxwell) — verify before freeze",
        scene=dict(bgcolor="#0b1220", xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"), zaxis=dict(gridcolor="#1e293b")),
        paper_bgcolor="#0b1220",
        font=dict(color="#e2e8f0"),
        height=720,
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig


def fig_animated_wave_medium(go):
    """Animated frames: sound wavefront expanding in a medium (concept demo)."""
    frames = []
    xm, ym = np.meshgrid(np.linspace(-2, 2, 40), np.linspace(-2, 2, 40))
    for fi, t in enumerate(np.linspace(0, 2 * np.pi, 36)):
        r = np.sqrt(xm**2 + ym**2)
        z = np.exp(-((r - (0.3 + 0.25 * fi / 36) * 2.5) ** 2) / 0.08) * np.cos(6 * r - t)
        frames.append(go.Frame(data=[go.Surface(z=z, x=xm, y=ym, colorscale="Blues", showscale=False)], name=str(fi)))
    z0 = np.exp(-(np.sqrt(xm**2 + ym**2) ** 2))
    fig = go.Figure(
        data=[go.Surface(z=z0, x=xm, y=ym, colorscale="Blues", showscale=False)],
        frames=frames,
    )
    fig.update_layout(
        title="Animated concept: wavefront in a pervasive medium (illustration only)",
        scene=dict(bgcolor="#0b1220", xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"), zaxis=dict(gridcolor="#1e293b", range=[-1.2, 1.2])),
        paper_bgcolor="#0b1220",
        font=dict(color="#e2e8f0"),
        height=720,
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                y=0,
                x=0.05,
                buttons=[
                    dict(label="Play", method="animate", args=[None, {"frame": {"duration": 60, "redraw": True}, "fromcurrent": True}]),
                    dict(label="Pause", method="animate", args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}]),
                ],
            )
        ],
    )
    return fig


def fig_claim_boundary_surface(go):
    """3D surface separating claimable comparative structure vs forbidden EM/QM upgrades."""
    a = np.linspace(0, 1, 30)
    b = np.linspace(0, 1, 30)
    A, B = np.meshgrid(a, b)
    # height = comparative attestation strength vs forbidden anticipation
    Z_claim = 0.7 * A * (1 - B)
    Z_forbid = 0.7 * B * (1 - 0.3 * A)
    fig = go.Figure()
    fig.add_trace(go.Surface(x=A, y=B, z=Z_claim, colorscale="Greens", opacity=0.75, name="claimable structure"))
    fig.add_trace(go.Surface(x=A, y=B, z=Z_forbid, colorscale="Reds", opacity=0.55, name="forbidden upgrades"))
    fig.update_layout(
        title="Concept surface: recoverable structure vs forbidden EM/QM anticipation",
        scene=dict(
            xaxis_title="attestation strength",
            yaxis_title="metaphor-upgrade pressure",
            zaxis_title="score (schematic)",
            bgcolor="#0b1220",
            xaxis=dict(gridcolor="#1e293b"),
            yaxis=dict(gridcolor="#1e293b"),
            zaxis=dict(gridcolor="#1e293b"),
        ),
        paper_bgcolor="#0b1220",
        font=dict(color="#e2e8f0"),
        height=720,
    )
    return fig


def write_index(paths: list[Path]) -> Path:
    links = "\n".join(f'<li><a href="{p.name}">{p.stem}</a></li>' for p in paths)
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><title>RISHI-Q ISEF2027 Visuals</title>
<style>
body{{margin:0;font-family:Georgia,serif;background:#0b1220;color:#e2e8f0}}
main{{max-width:720px;margin:48px auto;padding:0 20px}}
a{{color:#93c5fd}}
.note{{color:#94a3b8;font-size:0.95rem}}
</style></head><body><main>
<h1>RISHI-Q — scientific concept visuals</h1>
<p class="note">Interactive 3D / animated illustrations for methodology review. Not confirmatory results. Not paper text.</p>
<ul>{links}</ul>
</main></body></html>"""
    out = OUT / "index.html"
    out.write_text(html, encoding="utf-8")
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not _plotly_available():
        # fallback stub
        (OUT / "INSTALL_PLOTLY.txt").write_text(
            "Run: uv pip install plotly\nThen: uv run python scripts/build_isef2027_visuals.py\n",
            encoding="utf-8",
        )
        print("plotly missing — wrote INSTALL_PLOTLY.txt")
        return

    go, _ = ensure_plotly()
    builders = [
        ("01_akasa_sound_field_3d", fig_akasa_sound_field_3d),
        ("02_maxwell_field_3d", fig_maxwell_field_3d),
        ("03_tradition_geometry_3d", fig_tradition_embedding_3d),
        ("04_concept_graph_3d", fig_concept_graph_3d),
        ("05_animated_wave_medium", fig_animated_wave_medium),
        ("06_claim_boundary_surface", fig_claim_boundary_surface),
    ]
    paths = []
    for name, fn in builders:
        fig = fn(go)
        path = OUT / f"{name}.html"
        fig.write_html(path, include_plotlyjs="cdn", full_html=True)
        paths.append(path)
        print("wrote", path)
    idx = write_index(paths)
    print("index", idx)


if __name__ == "__main__":
    main()
