"""
Agricultural Simulation Dashboard
Interactive visualization with map, loop simulation, charts, and data explorer.
"""

import solara
import solara.lab
import pandas as pd
import json
import random
from pathlib import Path
import plotly.graph_objects as go

# ============================================================================
# CUSTOM CSS
# ============================================================================
CUSTOM_CSS = """
.dashboard-header {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #43a047 100%);
    color: white;
    padding: 24px 32px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(27, 94, 32, 0.3);
}
.dashboard-header h1 {
    margin: 0 0 4px 0;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.dashboard-header p {
    margin: 0;
    opacity: 0.85;
    font-size: 14px;
}
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-left: 4px solid #2e7d32;
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}
.metric-card .metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #1b5e20;
    margin: 4px 0;
}
.metric-card .metric-label {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #666;
    font-weight: 600;
}
.metric-card.blue { border-left-color: #1565c0; }
.metric-card.blue .metric-value { color: #1565c0; }
.metric-card.orange { border-left-color: #e65100; }
.metric-card.orange .metric-value { color: #e65100; }
.metric-card.purple { border-left-color: #6a1b9a; }
.metric-card.purple .metric-value { color: #6a1b9a; }
.metric-card.green { border-left-color: #2e7d32; }
.metric-card.green .metric-value { color: #2e7d32; }

.loop-step {
    padding: 14px 18px;
    border-radius: 10px;
    margin: 6px 0;
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 500;
    transition: all 0.3s;
}
.loop-step.active {
    background: linear-gradient(90deg, #e8f5e9, #c8e6c9);
    border-left: 4px solid #2e7d32;
    box-shadow: 0 2px 8px rgba(46, 125, 50, 0.2);
}
.loop-step.done {
    background: #f1f8e9;
    border-left: 4px solid #7cb342;
    color: #33691e;
}
.loop-step.pending {
    background: #fafafa;
    border-left: 4px solid #e0e0e0;
    color: #9e9e9e;
}

.section-card {
    border-radius: 12px !important;
    overflow: hidden;
}
.v-tabs .v-tab {
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
}
"""

# ============================================================================
# REACTIVE STATE
# ============================================================================
df_state = solara.reactive(None)
metrics_state = solara.reactive({})
tab_index = solara.reactive(0)
loop_step = solara.reactive(0)
data_loaded = solara.reactive(False)

# ============================================================================
# DATA LOADING
# ============================================================================
def load_data():
    """Load simulation results from files."""
    try:
        results_dir = Path("results")
        csv_path = results_dir / "agents_results.csv"
        json_path = results_dir / "metrics.json"

        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df_state.set(df)

            if json_path.exists():
                with open(json_path) as f:
                    metrics_state.set(json.load(f))

            data_loaded.set(True)
            return True
    except Exception as e:
        print(f"Error loading data: {e}")
    return False


# ============================================================================
# MOROCCO ZONE COORDINATES
# ============================================================================
ZONE_COORDS = {
    "IRRIGATED_SOUSS": (30.4, -9.0, "Souss-Massa (Irrigated)"),
    "SUB_HUMID": (34.0, -6.5, "Gharb-Loukkos (Sub-Humid)"),
    "SEMI_ARID_WARM": (31.6, -7.6, "Haouz-Tadla (Semi-Arid Warm)"),
    "SEMI_ARID_COOL": (33.9, -4.0, "Fès-Saïs (Semi-Arid Cool)"),
    "ARID": (32.3, -1.9, "Oriental (Arid)"),
    "SAHARAN": (30.0, -5.8, "Drâa-Tafilalet (Saharan)"),
}

ZONE_COLORS = {
    "IRRIGATED_SOUSS": "#1565c0",
    "SUB_HUMID": "#2e7d32",
    "SEMI_ARID_WARM": "#e65100",
    "SEMI_ARID_COOL": "#00838f",
    "ARID": "#bf360c",
    "SAHARAN": "#4e342e",
}

# ============================================================================
# CHART BUILDERS
# ============================================================================
def build_map(df):
    """Geographic map with farmer agents on Morocco zones — realistic terrain style."""
    fig = go.Figure()

    # ── Zone shading circles (colored translucent areas for each zone) ──
    zone_radius = {
        "IRRIGATED_SOUSS": 0.7, "SUB_HUMID": 0.8, "SEMI_ARID_WARM": 0.8,
        "SEMI_ARID_COOL": 0.7, "ARID": 0.9, "SAHARAN": 0.9,
    }
    zone_bg_colors = {
        "IRRIGATED_SOUSS": "rgba(33,150,243,0.12)",
        "SUB_HUMID": "rgba(76,175,80,0.12)",
        "SEMI_ARID_WARM": "rgba(255,152,0,0.12)",
        "SEMI_ARID_COOL": "rgba(0,188,212,0.12)",
        "ARID": "rgba(244,67,54,0.10)",
        "SAHARAN": "rgba(161,136,127,0.10)",
    }
    import numpy as np
    for zone_id, (clat, clon, _) in ZONE_COORDS.items():
        r = zone_radius.get(zone_id, 0.7)
        angles = np.linspace(0, 2 * np.pi, 40)
        ring_lats = [clat + r * np.sin(a) for a in angles]
        ring_lons = [clon + r * np.cos(a) for a in angles]
        fig.add_trace(go.Scattergeo(
            lon=ring_lons, lat=ring_lats,
            mode="lines",
            line=dict(width=2.5, color=ZONE_COLORS[zone_id]),
            fill="toself",
            fillcolor=zone_bg_colors.get(zone_id, "rgba(100,100,100,0.08)"),
            showlegend=False,
            hoverinfo="skip",
        ))

    # ── SHARED agents ──
    shared_df = df[df["strategy"] == "SHARED"]
    s_lats, s_lons, s_texts, s_sizes, s_yields = [], [], [], [], []
    for _, row in shared_df.iterrows():
        base_lat, base_lon, zone_label = ZONE_COORDS.get(row["zone"], (31, -5, row["zone"]))
        s_lats.append(base_lat + random.uniform(-0.45, 0.45))
        s_lons.append(base_lon + random.uniform(-0.45, 0.45))
        s_sizes.append(max(8, min(18, row["mean_yield"] * 1.5)))
        s_yields.append(row["mean_yield"])
        s_texts.append(
            f"<b>Farmer #{int(row['unique_id'])}</b><br>"
            f"<span style='color:#4caf50'>\u25cf SHARED</span><br>"
            f"Zone: {zone_label}<br>"
            f"Yield: {row['mean_yield']:.2f} t/ha<br>"
            f"Profit: {row['mean_profit']:.1f}"
        )

    fig.add_trace(go.Scattergeo(
        lon=s_lons, lat=s_lats, mode="markers",
        name=f"\ud83e\udd1d SHARED ({len(shared_df)})",
        text=s_texts,
        hovertemplate="%{text}<extra></extra>",
        marker=dict(
            size=s_sizes,
            color="#2e7d32",
            showscale=False,
            opacity=0.88,
            line=dict(width=1.5, color="white"),
            symbol="circle",
        ),
    ))

    # ── INDIVIDUAL agents ──
    indiv_df = df[df["strategy"] == "INDIVIDUAL"]
    i_lats, i_lons, i_texts, i_sizes, i_yields = [], [], [], [], []
    for _, row in indiv_df.iterrows():
        base_lat, base_lon, zone_label = ZONE_COORDS.get(row["zone"], (31, -5, row["zone"]))
        i_lats.append(base_lat + random.uniform(-0.45, 0.45))
        i_lons.append(base_lon + random.uniform(-0.45, 0.45))
        i_sizes.append(max(8, min(18, row["mean_yield"] * 1.5)))
        i_yields.append(row["mean_yield"])
        i_texts.append(
            f"<b>Farmer #{int(row['unique_id'])}</b><br>"
            f"<span style='color:#ef5350'>\u25cf INDIVIDUAL</span><br>"
            f"Zone: {zone_label}<br>"
            f"Yield: {row['mean_yield']:.2f} t/ha<br>"
            f"Profit: {row['mean_profit']:.1f}"
        )

    fig.add_trace(go.Scattergeo(
        lon=i_lons, lat=i_lats, mode="markers",
        name=f"\ud83d\udc64 INDIVIDUAL ({len(indiv_df)})",
        text=i_texts,
        hovertemplate="%{text}<extra></extra>",
        marker=dict(
            size=i_sizes,
            color="#d32f2f",
            showscale=False,
            opacity=0.88,
            line=dict(width=1.5, color="white"),
            symbol="diamond",
        ),
    ))

    # ── Zone labels with colored backgrounds ──
    for zone_id, (lat, lon, label) in ZONE_COORDS.items():
        zc = ZONE_COLORS[zone_id]
        fig.add_trace(go.Scattergeo(
            lon=[lon], lat=[lat + 0.85],
            mode="markers+text",
            text=[f"  {label}  "],
            textfont=dict(size=11, color=zc, family="Arial", weight="bold"),
            textposition="top center",
            marker=dict(size=0, color="rgba(0,0,0,0)"),
            showlegend=False,
            hoverinfo="skip",
        ))

    # ── Layout — realistic terrain style ──
    fig.update_layout(
        title=dict(
            text="<b>Farmer Agents Across Morocco</b>",
            font=dict(size=18, color="#333"),
            x=0.5, xanchor="center",
        ),
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="#e8e0d4",
            coastlinecolor="#8d6e63",
            coastlinewidth=1.5,
            countrycolor="#a1887f",
            countrywidth=1,
            showocean=True,
            oceancolor="#b3d9e8",
            showlakes=True,
            lakecolor="#90caf9",
            showrivers=True,
            rivercolor="#90caf9",
            riverwidth=1,
            showcountries=True,
            showsubunits=True,
            subunitcolor="#bcaaa4",
            center=dict(lat=31.5, lon=-6),
            projection_scale=12,
            lataxis=dict(range=[27, 36]),
            lonaxis=dict(range=[-13, 0]),
            bgcolor="#f5f0eb",
            framecolor="#8d6e63",
            framewidth=2,
        ),
        height=620,
        margin=dict(l=0, r=60, t=55, b=0),
        legend=dict(
            yanchor="top", y=0.95,
            xanchor="left", x=0.01,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#8d6e63", borderwidth=2,
            font=dict(size=14, color="#333", family="Arial"),
            title=dict(text="<b>Strategy</b>", font=dict(size=13)),
            itemsizing="constant",
        ),
        paper_bgcolor="#f5f0eb",
        font=dict(color="#333"),
    )
    return fig


def build_yield_comparison(df):
    """Box plot comparing strategies."""
    fig = go.Figure()

    for strat, color, symbol in [("SHARED", "#2e7d32", "🤝"), ("INDIVIDUAL", "#1565c0", "👤")]:
        data = df[df["strategy"] == strat]
        fig.add_trace(go.Box(
            y=data["mean_yield"],
            name=f"{symbol} {strat}",
            marker_color=color,
            boxmean="sd",
            jitter=0.3,
            pointpos=-1.5,
            boxpoints="all",
        ))

    fig.update_layout(
        title=dict(text="<b>Yield Distribution by Strategy</b>", font=dict(size=16)),
        yaxis_title="Mean Yield (t/ha)",
        height=420,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fafafa",
        yaxis=dict(gridcolor="#eee"),
    )
    return fig


def build_zone_chart(df):
    """Bar chart showing zone performance with strategy breakdown."""
    fig = go.Figure()

    for strat, color in [("SHARED", "#2e7d32"), ("INDIVIDUAL", "#1565c0")]:
        sdf = df[df["strategy"] == strat]
        zone_avg = sdf.groupby("zone")["mean_yield"].mean()
        fig.add_trace(go.Bar(
            x=[ZONE_COORDS.get(z, (0, 0, z))[2] for z in zone_avg.index],
            y=zone_avg.values,
            name=strat,
            marker_color=color,
            text=[f"{v:.1f}" for v in zone_avg.values],
            textposition="auto",
        ))

    fig.update_layout(
        title=dict(text="<b>Average Yield by Zone & Strategy</b>", font=dict(size=16)),
        xaxis_title="Agricultural Zone",
        yaxis_title="Mean Yield (t/ha)",
        barmode="group",
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fafafa",
        yaxis=dict(gridcolor="#eee"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    return fig


def build_profit_scatter(df):
    """Scatter plot of yield vs profit colored by strategy."""
    fig = go.Figure()

    for strat, color in [("SHARED", "#2e7d32"), ("INDIVIDUAL", "#1565c0")]:
        sdf = df[df["strategy"] == strat]
        fig.add_trace(go.Scatter(
            x=sdf["mean_yield"],
            y=sdf["mean_profit"],
            mode="markers",
            name=strat,
            marker=dict(color=color, size=8, opacity=0.7, line=dict(width=1, color="white")),
            text=[f"Farmer #{int(r['unique_id'])}<br>{r['zone']}" for _, r in sdf.iterrows()],
            hovertemplate="<b>%{text}</b><br>Yield: %{x:.2f}<br>Profit: %{y:.2f}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="<b>Yield vs Profit</b>", font=dict(size=16)),
        xaxis_title="Mean Yield (t/ha)",
        yaxis_title="Mean Profit",
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fafafa",
        xaxis=dict(gridcolor="#eee"),
        yaxis=dict(gridcolor="#eee"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    return fig


# ============================================================================
# LOOP SIMULATION DATA
# ============================================================================
LOOP_STEPS = [
    {
        "icon": "🌱",
        "title": "Step 1: Farmers Evaluate Crops",
        "detail": "Each farmer scores all viable crops using zone compatibility, soil match, and climate fit. "
                  "Suitability = 0.4×zone + 0.25×soil + 0.25×climate.",
    },
    {
        "icon": "🌾",
        "title": "Step 2: Crop Selection",
        "detail": "INDIVIDUAL farmers pick the top-scoring crop. "
                  "SHARED farmers blend their score with community knowledge (60% shared, 40% individual).",
    },
    {
        "icon": "📊",
        "title": "Step 3: Yield Calculation",
        "detail": "yield = base_yield × suitability × variability. "
                  "Variability is random between 0.8–1.2 to simulate real conditions.",
    },
    {
        "icon": "🤝",
        "title": "Step 4: Knowledge Sharing",
        "detail": "SHARED farmers within each zone pool their results. "
                  "The community average yield per crop is computed and stored.",
    },
    {
        "icon": "🔄",
        "title": "Step 5: Update & Repeat",
        "detail": "Community knowledge is updated. Next timestep begins. "
                  "Over time, SHARED farmers converge on the best crop for their zone.",
    },
]


# ============================================================================
# COMPONENTS
# ============================================================================
@solara.component
def MetricCard(value, label, css_class=""):
    """A styled metric display card."""
    solara.HTML(tag="div", attributes={"class": f"metric-card {css_class}"}, unsafe_innerHTML=f"""
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    """)


@solara.component
def LoopSimulator():
    """Interactive step-through of the shared knowledge loop."""
    step = loop_step.value

    solara.Markdown("### ⚙️ Shared Knowledge Loop — How It Works")
    solara.Warning(
        label="This is an educational walkthrough — it shows the 5 phases that happen each simulation timestep.",
        dense=True,
    )

    with solara.Row(gap="8px", justify="start"):
        solara.Button(
            "▶️ Next Step",
            on_click=lambda: loop_step.set(min(step + 1, 5)),
            color="green",
            disabled=(step >= 5),
        )
        solara.Button(
            "⏮️ Reset",
            on_click=lambda: loop_step.set(0),
            outlined=True,
            color="grey",
        )
        solara.Markdown(f"**Step {step} / 5**")

    # Render steps
    for i, s in enumerate(LOOP_STEPS):
        idx = i + 1
        if idx < step:
            css = "done"
            icon = "✅"
        elif idx == step:
            css = "active"
            icon = s["icon"]
        else:
            css = "pending"
            icon = "⬜"

        solara.HTML(
            tag="div",
            attributes={"class": f"loop-step {css}"},
            unsafe_innerHTML=f"""
                <span style="font-size:22px">{icon}</span>
                <div>
                    <div style="font-weight:600">{s['title']}</div>
                    {'<div style="font-size:13px;margin-top:4px;color:#555">' + s['detail'] + '</div>' if idx <= step else ''}
                </div>
            """,
        )


@solara.component
def MapTab(df):
    """Map visualization tab."""
    solara.Markdown("### 🗺️ Farmer Locations in Morocco")
    solara.Info(
        label="Each dot is a farmer agent. Green = SHARED strategy, Blue = INDIVIDUAL. Size reflects yield.",
        dense=True,
    )
    fig = build_map(df)
    solara.FigurePlotly(fig)


@solara.component
def ChartsTab(df):
    """Charts visualization tab."""
    solara.Markdown("### 📊 Performance Analysis")

    with solara.Columns([6, 6]):
        with solara.Card("Yield by Strategy", elevation=1, style={"border-radius": "12px"}):
            solara.FigurePlotly(build_yield_comparison(df))

        with solara.Card("Zone Performance", elevation=1, style={"border-radius": "12px"}):
            solara.FigurePlotly(build_zone_chart(df))

    with solara.Card("Yield vs Profit Correlation", elevation=1, style={"border-radius": "12px"}):
        solara.FigurePlotly(build_profit_scatter(df))


@solara.component
def DataTab(df):
    """Data explorer tab with zone comparison."""
    solara.Markdown("### 📋 Zone Comparison — SHARED vs INDIVIDUAL")
    solara.Info(
        label="Side-by-side comparison of strategies within each agricultural zone.",
        dense=True,
    )

    # Build zone comparison summary
    zone_rows = []
    for zone_id in sorted(df["zone"].unique()):
        zone_label = ZONE_COORDS.get(zone_id, (0, 0, zone_id))[2]
        zdf = df[df["zone"] == zone_id]
        shared = zdf[zdf["strategy"] == "SHARED"]
        indiv = zdf[zdf["strategy"] == "INDIVIDUAL"]
        zone_rows.append({
            "zone_id": zone_id,
            "label": zone_label,
            "total": len(zdf),
            "s_count": len(shared),
            "s_yield": shared["mean_yield"].mean() if len(shared) > 0 else 0,
            "s_profit": shared["mean_profit"].mean() if len(shared) > 0 else 0,
            "i_count": len(indiv),
            "i_yield": indiv["mean_yield"].mean() if len(indiv) > 0 else 0,
            "i_profit": indiv["mean_profit"].mean() if len(indiv) > 0 else 0,
        })

    # Styled HTML comparison table
    table_html = """
    <style>
    .zone-table { width:100%; border-collapse:separate; border-spacing:0; font-size:14px; border-radius:12px; overflow:hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
    .zone-table th { background: linear-gradient(135deg, #1b5e20, #2e7d32); color:white; padding:12px 16px; text-align:center; font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:0.5px; }
    .zone-table th.zone-header { text-align:left; min-width:180px; }
    .zone-table th.shared-header { background: linear-gradient(135deg, #2e7d32, #43a047); }
    .zone-table th.indiv-header { background: linear-gradient(135deg, #1565c0, #1976d2); }
    .zone-table td { padding:10px 16px; text-align:center; border-bottom:1px solid #f0f0f0; }
    .zone-table tr:last-child td { border-bottom:none; }
    .zone-table tr:nth-child(even) { background:#fafffe; }
    .zone-table tr:hover { background:#e8f5e9; transition:background 0.2s; }
    .zone-table .zone-name { text-align:left; font-weight:600; color:#333; }
    .zone-table .zone-tag { display:inline-block; background:#e8f5e9; color:#2e7d32; padding:2px 8px; border-radius:4px; font-size:11px; margin-left:6px; }
    .zone-table .s-val { color:#2e7d32; font-weight:600; }
    .zone-table .i-val { color:#1565c0; font-weight:600; }
    .zone-table .winner { background: linear-gradient(90deg, transparent, #e8f5e920); }
    .zone-table .count-badge { display:inline-block; background:#f5f5f5; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
    .zone-table .s-badge { background:#e8f5e9; color:#2e7d32; }
    .zone-table .i-badge { background:#e3f2fd; color:#1565c0; }
    </style>
    <table class="zone-table">
    <thead>
        <tr>
            <th class="zone-header" rowspan="2">Zone</th>
            <th rowspan="2">Total</th>
            <th class="shared-header" colspan="3">🤝 SHARED</th>
            <th class="indiv-header" colspan="3">👤 INDIVIDUAL</th>
        </tr>
        <tr>
            <th class="shared-header">Count</th>
            <th class="shared-header">Yield</th>
            <th class="shared-header">Profit</th>
            <th class="indiv-header">Count</th>
            <th class="indiv-header">Yield</th>
            <th class="indiv-header">Profit</th>
        </tr>
    </thead>
    <tbody>
    """

    for z in zone_rows:
        best_yield = "s" if z["s_yield"] >= z["i_yield"] else "i"
        table_html += f"""
        <tr>
            <td class="zone-name">{z['label']}</td>
            <td><span class="count-badge">{z['total']}</span></td>
            <td><span class="count-badge s-badge">{z['s_count']}</span></td>
            <td class="s-val">{'<b>' if best_yield=='s' else ''}{z['s_yield']:.2f}{'</b> ⭐' if best_yield=='s' else ''}</td>
            <td class="s-val">{z['s_profit']:.1f}</td>
            <td><span class="count-badge i-badge">{z['i_count']}</span></td>
            <td class="i-val">{'<b>' if best_yield=='i' else ''}{z['i_yield']:.2f}{'</b> ⭐' if best_yield=='i' else ''}</td>
            <td class="i-val">{z['i_profit']:.1f}</td>
        </tr>
        """

    # Totals row
    t_shared = df[df["strategy"] == "SHARED"]
    t_indiv = df[df["strategy"] == "INDIVIDUAL"]
    table_html += f"""
    <tr style="background:linear-gradient(90deg,#f5f5f5,#e8f5e9); font-weight:700; border-top:2px solid #ddd;">
        <td class="zone-name" style="font-size:13px;">📊 OVERALL AVERAGE</td>
        <td><span class="count-badge">{len(df)}</span></td>
        <td><span class="count-badge s-badge">{len(t_shared)}</span></td>
        <td class="s-val">{t_shared['mean_yield'].mean():.2f}</td>
        <td class="s-val">{t_shared['mean_profit'].mean():.1f}</td>
        <td><span class="count-badge i-badge">{len(t_indiv)}</span></td>
        <td class="i-val">{t_indiv['mean_yield'].mean():.2f}</td>
        <td class="i-val">{t_indiv['mean_profit'].mean():.1f}</td>
    </tr>
    """
    table_html += "</tbody></table>"
    solara.HTML(unsafe_innerHTML=table_html)

    # Individual agent table below
    solara.HTML(tag="div", unsafe_innerHTML='<div style="height:24px"></div>')
    solara.Markdown("### 👥 Individual Agent Details")

    filter_strategy, set_filter = solara.use_state("All")
    filter_zone, set_zone = solara.use_state("All")

    with solara.Row(gap="12px"):
        solara.Select(
            label="Strategy",
            value=filter_strategy,
            values=["All", "SHARED", "INDIVIDUAL"],
            on_value=set_filter,
        )
        solara.Select(
            label="Zone",
            value=filter_zone,
            values=["All"] + sorted(df["zone"].unique().tolist()),
            on_value=set_zone,
        )

    display_df = df.copy()
    if filter_strategy != "All":
        display_df = display_df[display_df["strategy"] == filter_strategy]
    if filter_zone != "All":
        display_df = display_df[display_df["zone"] == filter_zone]

    cols = ["unique_id", "strategy", "zone", "mean_yield", "mean_profit"]
    display_df = display_df[cols].copy()
    display_df["mean_yield"] = display_df["mean_yield"].round(3)
    display_df["mean_profit"] = display_df["mean_profit"].round(2)
    display_df.columns = ["ID", "Strategy", "Zone", "Yield (t/ha)", "Profit"]

    solara.Markdown(f"Showing **{len(display_df)}** of {len(df)} farmers")
    solara.DataFrame(display_df, items_per_page=10)


@solara.component
def InfoTab(metrics):
    """Info and documentation tab."""
    solara.Markdown("### ℹ️ About This Simulation")

    with solara.Card("What is this?", elevation=1, style={"border-radius": "12px"}):
        solara.Markdown("""
This is an **Agent-Based Model (ABM)** of Moroccan agriculture using the **Mesa** framework.

**100 farmer agents** are distributed across **6 agricultural zones** of Morocco.
Each farmer chooses a crop every season based on ecological suitability and either:

- **INDIVIDUAL** strategy: Decides alone based on zone, soil, and climate scores
- **SHARED** strategy: Blends personal assessment with community knowledge
        """)

    with solara.Columns([6, 6]):
        with solara.Card("Map Legend", elevation=1, style={"border-radius": "12px"}):
            solara.Markdown("""
- 🟢 **Green dots** = SHARED strategy farmers
- 🔵 **Blue dots** = INDIVIDUAL strategy farmers
- **Dot size** = Yield (bigger = higher yield)
- **Hover** for farmer details
            """)

        with solara.Card("Loop Explanation", elevation=1, style={"border-radius": "12px"}):
            solara.Markdown("""
Each simulation timestep follows 5 phases:
1. Farmers evaluate crop suitability
2. Select optimal crop
3. Calculate yield with variability
4. SHARED farmers pool knowledge
5. Community knowledge updates
            """)

    if metrics:
        with solara.Card("Current Metrics", elevation=1, style={"border-radius": "12px"}):
            yield_adv = metrics.get("yield_advantage_shared", 0)
            profit_adv = metrics.get("profit_advantage_shared", 0)
            if yield_adv > 0 and profit_adv > 0:
                solara.Success(label=f"SHARED outperforms: +{yield_adv:.3f} t/ha yield, +{profit_adv:.1f} profit", dense=True)
            elif yield_adv > 0:
                solara.Info(label=f"SHARED has +{yield_adv:.3f} t/ha yield advantage", dense=True)
            else:
                solara.Warning(label=f"INDIVIDUAL leads by {abs(yield_adv):.3f} t/ha yield", dense=True)

            solara.Markdown(f"""
| Metric | SHARED | INDIVIDUAL |
|--------|--------|------------|
| Avg Yield (t/ha) | **{metrics.get('avg_yield_shared', 0):.3f}** | {metrics.get('avg_yield_individual', 0):.3f} |
| Avg Profit | **{metrics.get('avg_profit_shared', 0):.1f}** | {metrics.get('avg_profit_individual', 0):.1f} |
| Yield Advantage | **+{yield_adv:.3f}** | — |
| Profit Advantage | **+{profit_adv:.1f}** | — |
| Agents | {metrics.get('shared_agents', 0)} | {metrics.get('individual_agents', 0)} |
| Total | **{metrics.get('total_agents', 0)}** | |
            """)


# ============================================================================
# MAIN DASHBOARD
# ============================================================================
@solara.component
def Dashboard():
    """Main dashboard component."""

    # Load data on mount
    def init():
        if not data_loaded.value:
            load_data()

    solara.use_effect(init, [])

    # Inject custom CSS
    solara.Style(CUSTOM_CSS)

    df = df_state.value
    metrics = metrics_state.value

    # ── Header ──
    solara.HTML(tag="div", attributes={"class": "dashboard-header"}, unsafe_innerHTML="""
        <h1>🌾 AgroAI — Agricultural Simulation Dashboard</h1>
        <p>Agent-Based Model · 6 Moroccan Zones · SHARED vs INDIVIDUAL Strategy Comparison</p>
    """)

    if df is None:
        solara.SpinnerSolara(size="80px")
        solara.Markdown("**Loading simulation results...**")
        return

    # ── Metric Cards ──
    total = len(df)
    shared = len(df[df["strategy"] == "SHARED"])
    individual = total - shared
    avg_yield = df["mean_yield"].mean()
    avg_profit = df["mean_profit"].mean()
    yield_adv = metrics.get("yield_advantage_shared", 0)
    profit_adv = metrics.get("profit_advantage_shared", 0)

    with solara.Row(gap="16px", justify="center"):
        MetricCard(str(total), "Total Farmers")
        MetricCard(f"{shared}", "Shared Strategy", css_class="blue")
        MetricCard(f"{avg_yield:.2f}", "Avg Yield (t/ha)", css_class="orange")
        MetricCard(f"{yield_adv:+.3f}", "Yield Advantage", css_class="purple")
        MetricCard(f"{profit_adv:+.1f}", "Profit Advantage", css_class="green")

    solara.HTML(tag="div", unsafe_innerHTML='<div style="height:16px"></div>')

    # ── Tabs ──
    with solara.lab.Tabs(
        value=tab_index,
        color="green",
        dark=False,
        grow=True,
    ):
        with solara.lab.Tab("🗺️ Map", icon_name="mdi-map"):
            with solara.Card(elevation=1, style={"border-radius": "12px", "padding": "16px"}):
                MapTab(df)

        with solara.lab.Tab("⚙️ Loop", icon_name="mdi-sync"):
            with solara.Card(elevation=1, style={"border-radius": "12px", "padding": "16px"}):
                LoopSimulator()

        with solara.lab.Tab("📊 Charts", icon_name="mdi-chart-box"):
            with solara.Card(elevation=1, style={"border-radius": "12px", "padding": "16px"}):
                ChartsTab(df)

        with solara.lab.Tab("📋 Data", icon_name="mdi-table"):
            with solara.Card(elevation=1, style={"border-radius": "12px", "padding": "16px"}):
                DataTab(df)

        with solara.lab.Tab("ℹ️ Info", icon_name="mdi-information"):
            with solara.Card(elevation=1, style={"border-radius": "12px", "padding": "16px"}):
                InfoTab(metrics)

    # Footer
    solara.HTML(tag="div", unsafe_innerHTML="""
        <div style="text-align:center; padding:20px; color:#999; font-size:12px; margin-top:24px">
            AgroAI · Mesa Agent-Based Simulation · Solara Dashboard · Data from results/
        </div>
    """)


# ============================================================================
# ENTRY POINT
# ============================================================================
@solara.component
def Page():
    Dashboard()
