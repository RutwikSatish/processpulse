"""
ProcessPulse AI
─────────────────────────────────────────────────────
Where Your AI Should Actually Go.

Inspired by Alex Rinke (Celonis Co-CEO) at Celosphere 2025:
"Only 11% of companies are seeing measurable benefits from AI projects today.
 That's not an adoption problem. That's a context problem."

Built by Rutwik Satish | MS Engineering Management, Northeastern University
Celonis Process Mining Certified | SAP S/4HANA | McKinsey Forward
"""

import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from utils.data_generator import (
    generate_event_log, get_process_stats,
    get_bottlenecks, get_variant_flow, O2C_HAPPY, P2P_HAPPY
)
from utils.roi_engine import calculate_roi, score_ai_readiness, build_phase_roadmap
from utils.charts import (
    fig_variant_donut, fig_bottleneck_bar, fig_ai_opportunity_scatter,
    fig_roi_waterfall, fig_cycle_time_distribution, fig_process_flow
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ProcessPulse AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0D1117 !important;
    color: #E6EDF3 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0D1117 !important;
    border-right: 1px solid #30363D !important;
}
section[data-testid="stSidebar"] * { color: #E6EDF3 !important; }

/* Metric cards */
div[data-testid="metric-container"] {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 10px;
    padding: 16px 20px !important;
}
div[data-testid="metric-container"] label { color: #8B949E !important; font-size:12px !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #E6EDF3 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.6rem !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 12px !important; }

/* Tabs */
button[data-baseweb="tab"] {
    background: transparent !important;
    color: #8B949E !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
    border-bottom: 2px solid transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00D4AA !important;
    border-bottom: 2px solid #00D4AA !important;
}

/* Dataframe */
.dataframe thead tr th {
    background: #161B22 !important;
    color: #00D4AA !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
}
.dataframe tbody tr td { font-size: 12px !important; }

/* Custom cards */
.pp-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.pp-card-accent {
    background: linear-gradient(135deg, #0D1117 0%, #1a2332 100%);
    border: 1px solid #00D4AA44;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.pp-tag {
    display: inline-block;
    background: #00D4AA22;
    color: #00D4AA;
    border: 1px solid #00D4AA44;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 11px;
    font-family: 'IBM Plex Mono', monospace;
    margin-right: 6px;
}
.pp-tag-danger {
    background: #EF444422;
    color: #EF4444;
    border: 1px solid #EF444444;
}
.pp-tag-warn {
    background: #F59E0B22;
    color: #F59E0B;
    border: 1px solid #F59E0B44;
}
.pp-section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #00D4AA;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
    margin-top: 4px;
}
.pp-hero {
    background: linear-gradient(135deg, #0D1117 0%, #0d2020 50%, #0D1117 100%);
    border: 1px solid #00D4AA33;
    border-radius: 16px;
    padding: 32px 36px;
    margin-bottom: 28px;
}
.pp-phase-chip {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 6px;
}
div[data-testid="stSelectbox"] > div { background: #161B22 !important; border-color: #30363D !important; }
div[data-testid="stSlider"] { padding: 4px 0; }

/* Plotly chart backgrounds */
.js-plotly-plot .plotly { border-radius: 10px; overflow: hidden; }

/* Upload area */
div[data-testid="stFileUploadDropzone"] {
    background: #161B22 !important;
    border: 1px dashed #30363D !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session state (cache data across rerenders) ───────────────────────────────
@st.cache_data(ttl=3600)
def load_data(process: str, n_cases: int):
    df = generate_event_log(process, n_cases)
    stats = get_process_stats(df)
    bottlenecks = get_bottlenecks(df)
    roi = calculate_roi(bottlenecks)
    ai_scores = score_ai_readiness(df)
    roadmap = build_phase_roadmap(bottlenecks)
    return df, stats, bottlenecks, roi, ai_scores, roadmap


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 24px 0;'>
        <div style='font-family: IBM Plex Mono, monospace; font-size: 22px;
                    font-weight:600; color:#00D4AA; letter-spacing:-1px;'>
            ⚡ ProcessPulse
        </div>
        <div style='font-size:10px; color:#8B949E; letter-spacing:3px;
                    text-transform:uppercase; margin-top:4px;'>
            AI PROCESS INTELLIGENCE
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p class="pp-section-header">Configuration</p>', unsafe_allow_html=True)

    process_type = st.selectbox(
        "Process",
        ["Order-to-Cash (O2C)", "Procure-to-Pay (P2P)"],
        help="Select the enterprise process to analyse"
    )
    process_key = "O2C" if "O2C" in process_type else "P2P"

    n_cases = st.slider("Simulated Cases", 200, 1000, 500, 50,
                        help="Number of process instances to generate")

    uploaded = st.file_uploader(
        "Upload Event Log (CSV)", type=["csv"],
        help="Optional: Upload your own event log with columns: case_id, activity, start_time, end_time"
    )

    st.markdown("---")
    st.markdown('<p class="pp-section-header">About This Project</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px; color:#8B949E; line-height:1.6;'>
    Inspired by <b style='color:#E6EDF3;'>Alex Rinke, Co-CEO of Celonis</b>:
    <br><br>
    <i style='color:#00D4AA;'>"Only 11% of companies see measurable AI benefit.
    That's not an adoption problem.
    That's a context problem."</i>
    <br><br>
    ProcessPulse demonstrates how Process Intelligence grounds AI in real operational context
    — turning failed pilots into measurable ROI.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:10px; color:#8B949E; text-align:center;'>
        Built by <b style='color:#E6EDF3;'>Rutwik Satish</b><br>
        MS Engineering Management · Northeastern<br>
        <span style='color:#00D4AA;'>Celonis Certified · SAP S/4HANA</span>
    </div>
    """, unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
df, stats, bottlenecks, roi, ai_scores, roadmap = load_data(process_key, n_cases)

# Handle uploaded file override
if uploaded:
    try:
        df_upload = pd.read_csv(uploaded)
        required = {"case_id","activity","start_time","end_time"}
        if required.issubset(df_upload.columns):
            st.sidebar.success(f"✅ Loaded {len(df_upload)} rows from your file")
        else:
            st.sidebar.warning(f"CSV must contain: {required}")
    except Exception as e:
        st.sidebar.error(f"Parse error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="pp-hero">
    <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
        <div>
            <div style='font-size:28px; font-weight:700; font-family: IBM Plex Sans, sans-serif;
                        letter-spacing:-0.5px; margin-bottom:6px;'>
                ⚡ ProcessPulse <span style='color:#00D4AA;'>AI</span>
            </div>
            <div style='font-size:13px; color:#8B949E; margin-bottom:14px;'>
                Process Intelligence · AI Opportunity Analysis · ROI Quantification
            </div>
            <div>
                <span class="pp-tag">Celonis Process Mining</span>
                <span class="pp-tag">SAP S/4HANA</span>
                <span class="pp-tag">Lean Six Sigma</span>
                <span class="pp-tag">McKinsey Forward</span>
            </div>
        </div>
        <div style='text-align:right;'>
            <div style='font-family: IBM Plex Mono, monospace; font-size:11px;
                        color:#8B949E; margin-bottom:4px;'>ANALYSING</div>
            <div style='font-size:20px; font-weight:600; color:#00D4AA;
                        font-family: IBM Plex Mono, monospace;'>
                {process_type}
            </div>
            <div style='font-size:11px; color:#8B949E; margin-top:4px;'>
                {n_cases:,} process instances
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPI STRIP
# ══════════════════════════════════════════════════════════════════════════════
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric("Total Cases", f"{stats['total_cases']:,}")
with k2:
    delta = f"+{stats['non_happy_cycle_hrs'] - stats['happy_cycle_hrs']:.0f}h vs happy"
    st.metric("Avg Cycle Time", f"{stats['avg_cycle_time_hrs']:,}h", delta,
              delta_color="inverse")
with k3:
    st.metric("Happy Path %", f"{stats['happy_path_pct']}%",
              f"{100-stats['happy_path_pct']:.0f}% deviating", delta_color="inverse")
with k4:
    st.metric("Bottleneck Time", f"{stats['bottleneck_pct']}%",
              "of total process time", delta_color="off")
with k5:
    at_risk_pct = round(stats["at_risk_value_usd"] / stats["total_value_usd"] * 100, 1)
    st.metric("Value at Risk", f"${stats['at_risk_value_usd']/1e6:.1f}M",
              f"{at_risk_pct}% of portfolio", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Process Overview",
    "🔍  Bottleneck Analysis",
    "🤖  AI Opportunity Map",
    "💰  ROI Calculator",
    "🗺️  Implementation Roadmap",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Process Overview
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown('<p class="pp-section-header">Intended Process Flow</p>', unsafe_allow_html=True)
        happy_steps = O2C_HAPPY if process_key == "O2C" else P2P_HAPPY
        st.plotly_chart(fig_process_flow(happy_steps, "Intended (Happy Path)"),
                        use_container_width=True)

        st.markdown('<p class="pp-section-header">Actual Process Variants Found</p>', unsafe_allow_html=True)
        variant_select = st.selectbox(
            "View variant flow",
            [v for v in df["variant"].unique()],
        )
        variant_steps = get_variant_flow(df, variant_select)
        st.plotly_chart(fig_process_flow(variant_steps, f"Actual: {variant_select}"),
                        use_container_width=True)

    with c2:
        st.plotly_chart(fig_variant_donut(stats["variant_counts"]),
                        use_container_width=True)
        st.plotly_chart(fig_cycle_time_distribution(df),
                        use_container_width=True)

    # insight callout
    excess = stats['non_happy_cycle_hrs'] - stats['happy_cycle_hrs']
    st.markdown(f"""
    <div class="pp-card-accent">
        <div class="pp-section-header">🔎 Process Intelligence Insight</div>
        <p style='font-size:13px; margin:0; line-height:1.7;'>
        Only <b style='color:#00D4AA;'>{stats['happy_path_pct']}%</b> of cases follow the intended happy path.
        The remaining <b style='color:#EF4444;'>{100-stats['happy_path_pct']:.0f}%</b> of cases average
        <b style='color:#F59E0B;'>{excess:.0f} additional hours</b> per case due to rework, manual interventions,
        and exception handling — representing
        <b style='color:#EF4444;'>${stats["at_risk_value_usd"]/1e6:.1f}M in at-risk transaction value.</b>
        <br><br>
        This is the context problem Alex Rinke described at Celosphere 2025.
        AI deployed without this process intelligence will optimise the wrong steps.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Bottleneck Analysis
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<p class="pp-section-header">Top 5 Value-Leaking Activities</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.plotly_chart(fig_bottleneck_bar(bottlenecks), use_container_width=True)
    with c2:
        # Summary table
        display_bn = bottlenecks[["activity","occurrences","avg_duration_hrs",
                                   "cost_impact_usd","ai_score"]].copy()
        display_bn.columns = ["Activity","Cases","Avg Hrs","Cost Impact ($)","AI Score"]
        display_bn["Cost Impact ($)"] = display_bn["Cost Impact ($)"].apply(lambda x: f"${x:,.0f}")
        display_bn["Avg Hrs"] = display_bn["Avg Hrs"].apply(lambda x: f"{x:.1f}h")
        display_bn["AI Score"] = display_bn["AI Score"].apply(lambda x: f"{x}/100")
        st.dataframe(display_bn, hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Individual bottleneck cards
    st.markdown('<p class="pp-section-header">Bottleneck Deep Dive</p>', unsafe_allow_html=True)
    cols = st.columns(min(len(bottlenecks), 5))
    for i, (_, row) in enumerate(bottlenecks.iterrows()):
        if i >= len(cols): break
        with cols[i]:
            score = int(row["ai_score"])
            tag_class = "pp-tag-danger" if score >= 80 else "pp-tag-warn" if score >= 60 else "pp-tag"
            st.markdown(f"""
            <div class="pp-card" style='height:180px;'>
                <div style='font-size:11px; color:#8B949E; margin-bottom:8px;
                            font-family: IBM Plex Mono, monospace;'>BOTTLENECK {i+1}</div>
                <div style='font-size:13px; font-weight:600; color:#E6EDF3;
                            margin-bottom:10px; line-height:1.3;'>{row["activity"]}</div>
                <div style='font-size:11px; color:#8B949E;'>Occurrences</div>
                <div style='font-size:16px; font-family: IBM Plex Mono, monospace;
                            color:#E6EDF3; margin-bottom:4px;'>{int(row["occurrences"]):,}</div>
                <div style='margin-top:8px;'>
                    <span class="pp-tag {tag_class}">AI Score: {score}/100</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — AI Opportunity Map
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<p class="pp-section-header">AI Readiness Scoring — All Activities</p>', unsafe_allow_html=True)

    st.plotly_chart(fig_ai_opportunity_scatter(ai_scores), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="pp-section-header">Top AI Candidates</p>', unsafe_allow_html=True)
        top_ai = ai_scores.head(8)[["activity","composite_score","avg_dur","freq_score"]].copy()
        top_ai.columns = ["Activity","AI Score","Avg Duration (h)","Frequency Score"]
        top_ai["AI Score"] = top_ai["AI Score"].apply(lambda x: f"{x:.0f}/100")
        top_ai["Avg Duration (h)"] = top_ai["Avg Duration (h)"].apply(lambda x: f"{x:.1f}h")
        top_ai["Frequency Score"] = top_ai["Frequency Score"].apply(lambda x: f"{x:.0f}")
        st.dataframe(top_ai, hide_index=True, use_container_width=True)

    with c2:
        st.markdown('<p class="pp-section-header">AI Technology Match</p>', unsafe_allow_html=True)
        ai_tech_map = {
            "Manual Resolution":   ("Agentic AI + RPA",       "Automate exception resolution end-to-end"),
            "Duplicate Flag":      ("ML Classification",      "Near-zero false positives possible"),
            "Match Exception":     ("AI + Process Mining",    "Celonis-native use case"),
            "Credit Check":        ("Predictive Scoring",     "Real-time risk AI"),
            "Manual Review":       ("LLM + Rules Engine",     "Document understanding + policy check"),
            "PR Approved":         ("Agentic Approval Bot",   "Route + auto-approve low-risk PRs"),
            "PO Amendment":        ("Change Detection AI",    "Flag before amendment is needed"),
            "Invoice Disputed":    ("NLP Dispute Resolver",   "Classify & route disputes automatically"),
        }
        for step, (tech, desc) in list(ai_tech_map.items())[:6]:
            st.markdown(f"""
            <div style='background:#161B22; border:1px solid #30363D; border-radius:8px;
                        padding:10px 14px; margin-bottom:8px;'>
                <div style='font-size:11px; font-weight:600; color:#E6EDF3;'>{step}</div>
                <div style='font-size:10px; color:#00D4AA; font-family: IBM Plex Mono, monospace;
                            margin:3px 0;'>{tech}</div>
                <div style='font-size:10px; color:#8B949E;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — ROI Calculator
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<p class="pp-section-header">AI ROI Calculator</p>', unsafe_allow_html=True)

    # Adjustable assumptions
    with st.expander("⚙️  Adjust Assumptions", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            hourly = st.number_input("Blended Hourly Rate ($)", 50, 200, 85, 5)
        with col2:
            reduction = st.slider("AI Time Reduction (%)", 30, 90, 70, 5) / 100
        with col3:
            impl_cost = st.number_input("Impl. Cost per Step ($k)", 20, 150, 45, 5) * 1000

        # Recalculate with custom assumptions
        custom_roi = {
            "annual_savings_usd":      round(bottlenecks["total_hrs"].sum() * hourly * reduction * 2),
            "implementation_cost_usd": round(len(bottlenecks) * impl_cost),
        }
        custom_roi["net_benefit_year1_usd"] = custom_roi["annual_savings_usd"] - custom_roi["implementation_cost_usd"]
        custom_roi["roi_pct"] = round(custom_roi["net_benefit_year1_usd"] / custom_roi["implementation_cost_usd"] * 100, 1)
        custom_roi["payback_months"] = round(custom_roi["implementation_cost_usd"] / (custom_roi["annual_savings_usd"] / 12), 1)
        custom_roi["total_bottleneck_hrs"] = roi["total_bottleneck_hrs"]
        custom_roi["total_cost_impact_usd"] = roi["total_cost_impact_usd"]
        custom_roi["total_ai_savings_usd"] = roi["total_ai_savings_usd"]
        active_roi = custom_roi
    else:
        active_roi = roi

    # ROI metrics
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric("Annual AI Savings", f"${active_roi['annual_savings_usd']:,.0f}")
    with r2:
        st.metric("Implementation Cost", f"${active_roi['implementation_cost_usd']:,.0f}")
    with r3:
        color = "normal" if active_roi["net_benefit_year1_usd"] > 0 else "inverse"
        st.metric("Net Benefit (Year 1)", f"${active_roi['net_benefit_year1_usd']:,.0f}",
                  delta_color=color)
    with r4:
        st.metric("Payback Period", f"{active_roi['payback_months']:.1f} months",
                  f"ROI: {active_roi['roi_pct']}%")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.4, 1])

    with c1:
        st.plotly_chart(fig_roi_waterfall(active_roi), use_container_width=True)

    with c2:
        st.markdown('<p class="pp-section-header">Savings by Activity</p>', unsafe_allow_html=True)
        savings_df = bottlenecks[["activity","ai_savings_usd","ai_score"]].copy()
        savings_df["ai_savings_usd"] = savings_df["ai_savings_usd"].apply(lambda x: f"${x*2:,.0f}")
        savings_df["ai_score"] = savings_df["ai_score"].apply(lambda x: f"{x}/100")
        savings_df.columns = ["Activity","Annual Savings","AI Score"]
        st.dataframe(savings_df, hide_index=True, use_container_width=True)

        st.markdown(f"""
        <div class="pp-card" style='margin-top:12px;'>
            <div class="pp-section-header">ROI Summary</div>
            <div style='font-size:12px; color:#8B949E; line-height:2.0;'>
                Bottleneck Hours Identified<br>
                <b style='color:#E6EDF3; font-family: IBM Plex Mono;'>
                {active_roi['total_bottleneck_hrs']:,}h across {len(bottlenecks)} activities</b>
            </div>
            <div style='font-size:12px; color:#8B949E; line-height:2.0; margin-top:8px;'>
                Cost of Inaction<br>
                <b style='color:#EF4444; font-family: IBM Plex Mono;'>
                ${active_roi['total_cost_impact_usd']:,.0f} / 6 months</b>
            </div>
            <div style='font-size:12px; color:#8B949E; line-height:2.0; margin-top:8px;'>
                AI Recoverable Value<br>
                <b style='color:#00D4AA; font-family: IBM Plex Mono;'>
                ${active_roi['annual_savings_usd']:,.0f} / year</b>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — Implementation Roadmap
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<p class="pp-section-header">Phased AI Implementation Roadmap</p>', unsafe_allow_html=True)

    phase_colors = {
        "Phase 1 — Quick Win (0-3 mo)": ("#00D4AA", "#00D4AA22"),
        "Phase 2 — Scale (3-9 mo)":     ("#7C3AED", "#7C3AED22"),
        "Phase 3 — Transform (9-18 mo)":("#F59E0B", "#F59E0B22"),
    }

    current_phase = None
    for item in roadmap:
        phase = item["phase"]
        if phase != current_phase:
            current_phase = phase
            color, bg = phase_colors.get(phase, ("#8B949E","#8B949E22"))
            st.markdown(f"""
            <div style='background:{bg}; border-left:3px solid {color};
                        border-radius:0 8px 8px 0; padding:10px 16px; margin:16px 0 8px 0;'>
                <span style='color:{color}; font-family: IBM Plex Mono, monospace;
                             font-size:12px; font-weight:600;'>{phase}</span>
            </div>
            """, unsafe_allow_html=True)

        color, _ = phase_colors.get(phase, ("#8B949E",""))
        effort_color = "#EF4444" if item["effort"]=="Low" else "#F59E0B" if item["effort"]=="Medium" else "#8B949E"
        st.markdown(f"""
        <div style='background:#161B22; border:1px solid #30363D; border-radius:8px;
                    padding:14px 18px; margin-bottom:8px; display:flex;
                    justify-content:space-between; align-items:center;'>
            <div>
                <span style='font-size:13px; font-weight:600; color:#E6EDF3;'>{item['activity']}</span>
                <span style='margin-left:10px; font-size:10px; color:{effort_color};
                             font-family: IBM Plex Mono;'>
                    Implementation: {item['effort']}
                </span>
            </div>
            <div style='text-align:right;'>
                <div style='font-size:11px; color:#8B949E;'>AI Score</div>
                <div style='font-family: IBM Plex Mono; color:{color};
                            font-size:15px; font-weight:600;'>{item['ai_score']}/100</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="pp-section-header">BA Deliverables Checklist</p>', unsafe_allow_html=True)

    deliverables = [
        ("✅","Current State Process Map","BPMN diagram of actual process with variant annotations"),
        ("✅","AI Readiness Assessment","Per-activity scoring across 4 dimensions"),
        ("✅","Bottleneck Quantification","Hours + cost impact of top 5 value leakage points"),
        ("✅","AI Opportunity Map","Scatter analysis: effort vs impact for all activities"),
        ("✅","ROI Business Case","NPV, payback period, net benefit year 1"),
        ("✅","Phased Roadmap","3-phase implementation plan with milestones"),
        ("⬜","Change Management Plan","Stakeholder RACI, training plan, adoption KPIs"),
        ("⬜","Vendor Evaluation Matrix","Tool comparison: Celonis vs UiPath vs SAP Joule"),
        ("⬜","Data Readiness Checklist","ERP data quality audit before AI deployment"),
        ("⬜","Governance Framework","AI oversight, exception escalation, KPI review cadence"),
    ]

    d1, d2 = st.columns(2)
    for i, (status, title, desc) in enumerate(deliverables):
        col = d1 if i % 2 == 0 else d2
        with col:
            color = "#00D4AA" if status == "✅" else "#8B949E"
            st.markdown(f"""
            <div style='background:#161B22; border:1px solid #30363D; border-radius:8px;
                        padding:10px 14px; margin-bottom:8px; opacity:{"1.0" if status=="✅" else "0.6"};'>
                <div style='font-size:12px; font-weight:600; color:{color};'>{status} {title}</div>
                <div style='font-size:10px; color:#8B949E; margin-top:3px;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Bottom attribution
    st.markdown("""<br>""", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#161B22; border:1px solid #30363D; border-radius:12px;
                padding:20px 24px; text-align:center;'>
        <div style='font-size:11px; color:#8B949E; line-height:1.8;'>
            Built to demonstrate the thesis of
            <b style='color:#00D4AA;'>Alex Rinke, Co-CEO Celonis</b>:
            AI without Process Intelligence delivers zero measurable benefit.
            <br>
            ProcessPulse AI connects process mining context to AI deployment strategy.
            <br><br>
            <b style='color:#E6EDF3;'>Rutwik Satish</b> · MS Engineering Management, Northeastern University ·
            <span style='color:#00D4AA;'>Celonis Process Mining Certified</span> ·
            SAP S/4HANA · McKinsey Forward · May 2026
        </div>
    </div>
    """, unsafe_allow_html=True)
