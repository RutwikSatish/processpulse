import pandas as pd
import numpy as np

HOURLY_RATE = 85          # blended analyst cost $/hr
AI_REDUCTION = 0.70       # AI can eliminate 70% of bottleneck time
IMPL_COST_PER_STEP = 45_000   # avg cost to implement AI for one process step
MONTHS_TO_PAYBACK = 18    # target payback horizon

def calculate_roi(bottlenecks: pd.DataFrame) -> dict:
    total_bottleneck_hrs   = bottlenecks["total_hrs"].sum()
    total_cost_impact      = bottlenecks["cost_impact_usd"].sum()
    total_ai_savings       = bottlenecks["ai_savings_usd"].sum()
    implementation_cost    = len(bottlenecks) * IMPL_COST_PER_STEP
    annual_savings         = total_ai_savings * 2          # annualised (6-month log)
    net_benefit_year1      = annual_savings - implementation_cost
    roi_pct                = round(net_benefit_year1 / implementation_cost * 100, 1) if implementation_cost else 0
    payback_months         = round(implementation_cost / (annual_savings / 12), 1) if annual_savings else 999

    return {
        "total_bottleneck_hrs":    round(total_bottleneck_hrs),
        "total_cost_impact_usd":   round(total_cost_impact),
        "total_ai_savings_usd":    round(total_ai_savings),
        "annual_savings_usd":      round(annual_savings),
        "implementation_cost_usd": round(implementation_cost),
        "net_benefit_year1_usd":   round(net_benefit_year1),
        "roi_pct":                 roi_pct,
        "payback_months":          payback_months,
    }

def score_ai_readiness(df: pd.DataFrame) -> pd.DataFrame:
    """Score each activity on 4 dimensions → composite AI readiness."""
    activity_stats = (
        df.groupby("activity")
        .agg(
            freq=("case_id","count"),
            avg_dur=("duration_hrs","mean"),
            std_dur=("duration_hrs","std"),
            ai_opp=("ai_opportunity","first"),
            is_bn=("is_bottleneck","first"),
        )
        .reset_index()
        .fillna(0)
    )

    # Normalise 0-100
    def norm(s):
        mn, mx = s.min(), s.max()
        return (s - mn) / (mx - mn + 1e-9) * 100

    activity_stats["freq_score"]      = norm(activity_stats["freq"])
    activity_stats["duration_score"]  = norm(activity_stats["avg_dur"])
    activity_stats["variance_score"]  = norm(activity_stats["std_dur"])
    activity_stats["opportunity_score"] = activity_stats["ai_opp"]

    activity_stats["composite_score"] = (
        activity_stats["freq_score"]       * 0.20 +
        activity_stats["duration_score"]   * 0.30 +
        activity_stats["variance_score"]   * 0.20 +
        activity_stats["opportunity_score"]* 0.30
    ).round(1)

    return activity_stats.sort_values("composite_score", ascending=False)

def build_phase_roadmap(bottlenecks: pd.DataFrame) -> list:
    phases = []
    sorted_bn = bottlenecks.sort_values("ai_score", ascending=False).reset_index(drop=True)

    phase_map = {0: "Phase 1 — Quick Win (0-3 mo)",
                 1: "Phase 1 — Quick Win (0-3 mo)",
                 2: "Phase 2 — Scale (3-9 mo)",
                 3: "Phase 2 — Scale (3-9 mo)",
                 4: "Phase 3 — Transform (9-18 mo)"}

    for i, row in sorted_bn.iterrows():
        phases.append({
            "phase":    phase_map.get(i, "Phase 3"),
            "activity": row["activity"],
            "ai_score": row["ai_score"],
            "saving":   row["ai_savings_usd"],
            "effort":   "Low" if row["ai_score"] >= 80 else ("Medium" if row["ai_score"] >= 60 else "High"),
        })
    return phases
