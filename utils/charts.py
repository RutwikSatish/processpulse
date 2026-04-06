import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ── Brand palette ────────────────────────────────────────────────────────────
C_BG       = "#0D1117"
C_CARD     = "#161B22"
C_BORDER   = "#30363D"
C_ACCENT   = "#00D4AA"
C_ACCENT2  = "#7C3AED"
C_WARN     = "#F59E0B"
C_DANGER   = "#EF4444"
C_TEXT     = "#E6EDF3"
C_MUTED    = "#8B949E"

_BASE_LAYOUT = dict(
    paper_bgcolor=C_BG,
    plot_bgcolor=C_CARD,
    font=dict(color=C_TEXT, family="IBM Plex Mono, monospace"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=C_BORDER),
)


def _layout(**extra):
    """Merge _BASE_LAYOUT with extra kwargs, deep-merging nested dicts
    so duplicate keys like 'legend' never trigger a TypeError."""
    base = {k: (dict(v) if isinstance(v, dict) else v)
            for k, v in _BASE_LAYOUT.items()}
    for k, v in extra.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            base[k] = {**base[k], **v}
        else:
            base[k] = v
    return base


def fig_variant_donut(variant_counts: dict) -> go.Figure:
    labels = list(variant_counts.keys())
    values = list(variant_counts.values())
    colors = [C_ACCENT, C_ACCENT2, C_WARN, C_DANGER, "#3B82F6", "#10B981"]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.62,
        marker=dict(colors=colors[:len(labels)], line=dict(color=C_BG, width=2)),
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>Cases: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    fig.update_layout(**_layout(
        title=dict(text="Process Variant Distribution", font=dict(size=14, color=C_TEXT)),
        showlegend=False,
        height=320,
    ))
    return fig


def fig_bottleneck_bar(bottlenecks: pd.DataFrame) -> go.Figure:
    df = bottlenecks.sort_values("total_hrs")
    colors = [C_DANGER if s >= 80 else C_WARN if s >= 60 else C_ACCENT
              for s in df["ai_score"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["activity"], x=df["total_hrs"],
        orientation="h",
        marker_color=colors,
        text=[f"{h:,.0f}h" for h in df["total_hrs"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Total Hours: %{x:,.0f}<br><extra></extra>",
    ))
    fig.update_layout(**_layout(
        title=dict(text="Top 5 Value-Leaking Activities (Total Hours)", font=dict(size=14)),
        xaxis=dict(title="Total Hours", gridcolor=C_BORDER, color=C_MUTED),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", color=C_TEXT),
        height=320,
    ))
    return fig


def fig_ai_opportunity_scatter(scores_df: pd.DataFrame) -> go.Figure:
    top = scores_df.head(15)
    colors = [C_DANGER if s >= 75 else C_WARN if s >= 50 else C_ACCENT
              for s in top["composite_score"]]

    fig = go.Figure(go.Scatter(
        x=top["avg_dur"],
        y=top["composite_score"],
        mode="markers+text",
        text=top["activity"],
        textposition="top center",
        textfont=dict(size=9, color=C_TEXT),
        marker=dict(
            size=top["freq_score"] / 5 + 8,
            color=colors,
            line=dict(color=C_BG, width=1),
            opacity=0.85,
        ),
        hovertemplate="<b>%{text}</b><br>Avg Duration: %{x:.1f}h<br>AI Score: %{y:.0f}<extra></extra>",
    ))

    med_x = top["avg_dur"].median()
    med_y = top["composite_score"].median()
    for val, axis in [(med_x, "x"), (med_y, "y")]:
        fig.add_shape(
            type="line",
            **({axis + "0": val, axis + "1": val,
                ("y" if axis == "x" else "x") + "0": 0,
                ("y" if axis == "x" else "x") + "1": 1}),
            xref="x" if axis == "x" else "paper",
            yref="y" if axis == "y" else "paper",
            line=dict(color=C_BORDER, dash="dot", width=1),
        )

    fig.add_annotation(
        x=top["avg_dur"].max() * 0.85, y=top["composite_score"].max() * 0.95,
        text="🎯 High Priority", showarrow=False,
        font=dict(color=C_DANGER, size=10),
    )

    fig.update_layout(**_layout(
        title=dict(text="AI Opportunity Map (bubble = frequency)", font=dict(size=14)),
        xaxis=dict(title="Avg Duration (hrs)", gridcolor=C_BORDER, color=C_MUTED),
        yaxis=dict(title="AI Readiness Score", gridcolor=C_BORDER, color=C_MUTED),
        height=380,
    ))
    return fig


def fig_roi_waterfall(roi: dict) -> go.Figure:
    labels = ["Cost of Bottlenecks", "AI Savings (Yr 1)", "Implementation Cost", "Net Benefit"]
    values = [
        roi["annual_savings_usd"] * -1,
        roi["annual_savings_usd"],
        -roi["implementation_cost_usd"],
        roi["net_benefit_year1_usd"],
    ]

    fig = go.Figure(go.Waterfall(
        name="ROI",
        measure=["absolute", "relative", "relative", "total"],
        x=labels, y=values,
        connector=dict(line=dict(color=C_BORDER, width=1)),
        increasing=dict(marker_color=C_ACCENT),
        decreasing=dict(marker_color=C_DANGER),
        totals=dict(marker_color=C_ACCENT2),
        text=[f"${abs(v):,.0f}" for v in values],
        textposition="outside",
        textfont=dict(color=C_TEXT, size=11),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**_layout(
        title=dict(text="AI ROI Waterfall — Year 1", font=dict(size=14)),
        yaxis=dict(title="USD", gridcolor=C_BORDER, color=C_MUTED, tickformat="$,.0f"),
        xaxis=dict(color=C_TEXT),
        showlegend=False,
        height=340,
    ))
    return fig


def fig_cycle_time_distribution(df: pd.DataFrame) -> go.Figure:
    cases = df.groupby(["case_id", "variant"])["duration_hrs"].sum().reset_index()
    happy = cases[cases["variant"] == "Happy Path"]["duration_hrs"]
    other = cases[cases["variant"] != "Happy Path"]["duration_hrs"]

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=happy, name="Happy Path",
        marker_color=C_ACCENT, opacity=0.75, nbinsx=30,
        hovertemplate="Duration: %{x:.0f}h<br>Count: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Histogram(
        x=other, name="Variant",
        marker_color=C_DANGER, opacity=0.65, nbinsx=30,
        hovertemplate="Duration: %{x:.0f}h<br>Count: %{y}<extra></extra>",
    ))
    # legend is deep-merged by _layout() — no duplicate keyword error
    fig.update_layout(**_layout(
        title=dict(text="Cycle Time Distribution: Happy Path vs Variants", font=dict(size=14)),
        xaxis=dict(title="Total Case Duration (hrs)", gridcolor=C_BORDER, color=C_MUTED),
        yaxis=dict(title="# Cases", gridcolor=C_BORDER, color=C_MUTED),
        legend=dict(orientation="h", y=1.1),
        barmode="overlay",
        height=300,
    ))
    return fig


def fig_process_flow(steps: list, process: str) -> go.Figure:
    n = len(steps)
    x = list(range(n))

    BOTTLENECK_STEPS = {
        "Credit Check", "Credit Hold", "Manual Review", "Invoice Disputed",
        "Invoice Revised", "Payment Reminder", "PR Approved", "PO Amendment",
        "Match Exception", "Manual Resolution", "Delivery Reminder",
    }

    node_colors = [C_DANGER if s in BOTTLENECK_STEPS else C_ACCENT for s in steps]
    node_sizes  = [24     if s in BOTTLENECK_STEPS else 18          for s in steps]

    fig = go.Figure()

    for i in range(n - 1):
        fig.add_trace(go.Scatter(
            x=[x[i], x[i + 1]], y=[0, 0],
            mode="lines",
            line=dict(color=C_BORDER, width=2),
            showlegend=False, hoverinfo="skip",
        ))

    fig.add_trace(go.Scatter(
        x=x, y=[0] * n,
        mode="markers+text",
        text=steps,
        textposition="top center",
        textfont=dict(size=9, color=C_TEXT),
        marker=dict(size=node_sizes, color=node_colors,
                    line=dict(color=C_BG, width=2)),
        hovertemplate="<b>%{text}</b><extra></extra>",
        showlegend=False,
    ))

    fig.add_annotation(
        x=0, y=-0.4, xref="paper", yref="paper",
        text="🔴 Bottleneck   🟢 Normal",
        showarrow=False, font=dict(color=C_MUTED, size=10),
    )

    fig.update_layout(**_layout(
        title=dict(text=f"{process} Process Flow", font=dict(size=14)),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   range=[-0.5, 0.5]),
        height=220,
    ))
    return fig
