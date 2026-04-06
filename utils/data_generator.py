import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# ── Process definitions ──────────────────────────────────────────────────────

O2C_HAPPY = [
    "Order Created", "Credit Check", "Order Confirmed",
    "Goods Picked", "Goods Shipped", "Invoice Sent", "Payment Received"
]

O2C_VARIANTS = {
    "Happy Path":        (O2C_HAPPY, 0.38),
    "Credit Hold Loop":  (["Order Created","Credit Check","Credit Hold","Credit Check","Order Confirmed",
                           "Goods Picked","Goods Shipped","Invoice Sent","Payment Received"], 0.14),
    "Manual Override":   (["Order Created","Credit Check","Manual Review","Order Confirmed",
                           "Goods Picked","Goods Shipped","Invoice Sent","Payment Received"], 0.10),
    "Late Payment":      (["Order Created","Credit Check","Order Confirmed","Goods Picked",
                           "Goods Shipped","Invoice Sent","Payment Reminder","Payment Received"], 0.18),
    "Return Loop":       (["Order Created","Credit Check","Order Confirmed","Goods Picked",
                           "Goods Shipped","Goods Returned","Credit Note Issued","Invoice Sent","Payment Received"], 0.09),
    "Invoice Dispute":   (["Order Created","Credit Check","Order Confirmed","Goods Picked",
                           "Goods Shipped","Invoice Sent","Invoice Disputed","Invoice Revised","Payment Received"], 0.11),
}

P2P_HAPPY = [
    "PR Created", "PR Approved", "PO Created", "PO Sent",
    "Goods Received", "Invoice Received", "3-Way Match", "Payment Processed"
]

P2P_VARIANTS = {
    "Happy Path":         (P2P_HAPPY, 0.32),
    "PO Amendment":       (["PR Created","PR Approved","PO Created","PO Amendment","PO Sent",
                            "Goods Received","Invoice Received","3-Way Match","Payment Processed"], 0.16),
    "Late Delivery":      (["PR Created","PR Approved","PO Created","PO Sent","Delivery Reminder",
                            "Goods Received","Invoice Received","3-Way Match","Payment Processed"], 0.14),
    "Match Exception":    (["PR Created","PR Approved","PO Created","PO Sent","Goods Received",
                            "Invoice Received","Match Exception","Manual Resolution","3-Way Match","Payment Processed"], 0.18),
    "Duplicate Invoice":  (["PR Created","PR Approved","PO Created","PO Sent","Goods Received",
                            "Invoice Received","Duplicate Flag","Invoice Rejected","Invoice Received","3-Way Match","Payment Processed"], 0.10),
    "Emergency PO":       (["Emergency PR","PO Created","PO Sent","Goods Received",
                            "Invoice Received","3-Way Match","Payment Processed"], 0.10),
}

# Step durations (hours): mean, std, is_bottleneck
STEP_DURATIONS = {
    # O2C
    "Order Created":       (0.5,  0.2,  False),
    "Credit Check":        (4.0,  8.0,  True),   # bottleneck
    "Credit Hold":         (48.0, 24.0, True),   # major bottleneck
    "Manual Review":       (16.0, 12.0, True),   # bottleneck
    "Order Confirmed":     (1.0,  0.5,  False),
    "Goods Picked":        (6.0,  3.0,  False),
    "Goods Shipped":       (24.0, 8.0,  False),
    "Goods Returned":      (72.0, 24.0, True),
    "Invoice Sent":        (2.0,  1.0,  False),
    "Payment Reminder":    (48.0, 24.0, True),
    "Payment Received":    (72.0, 48.0, False),
    "Invoice Disputed":    (96.0, 48.0, True),   # bottleneck
    "Invoice Revised":     (24.0, 12.0, True),
    "Credit Note Issued":  (24.0, 12.0, True),
    # P2P
    "PR Created":          (1.0,  0.5,  False),
    "PR Approved":         (8.0,  16.0, True),   # bottleneck
    "PO Created":          (2.0,  1.0,  False),
    "PO Amendment":        (12.0, 8.0,  True),   # bottleneck
    "PO Sent":             (1.0,  0.5,  False),
    "Delivery Reminder":   (48.0, 24.0, True),
    "Goods Received":      (4.0,  2.0,  False),
    "Invoice Received":    (4.0,  2.0,  False),
    "3-Way Match":         (2.0,  4.0,  False),
    "Match Exception":     (24.0, 16.0, True),   # bottleneck
    "Manual Resolution":   (32.0, 16.0, True),
    "Duplicate Flag":      (2.0,  1.0,  False),
    "Invoice Rejected":    (8.0,  4.0,  False),
    "Payment Processed":   (48.0, 24.0, False),
    "Emergency PR":        (0.5,  0.2,  False),
}

# AI opportunity scores per step (0-100)
AI_OPPORTUNITY = {
    "Credit Check":       85, "Credit Hold":        70, "Manual Review":     90,
    "Invoice Disputed":   80, "Invoice Revised":    75, "Payment Reminder":  65,
    "Goods Returned":     60, "Credit Note Issued": 55,
    "PR Approved":        80, "PO Amendment":       85, "Delivery Reminder": 70,
    "Match Exception":    90, "Manual Resolution":  95, "Duplicate Flag":    95,
}


def generate_event_log(process: str = "O2C", n_cases: int = 500) -> pd.DataFrame:
    variants = O2C_VARIANTS if process == "O2C" else P2P_VARIANTS
    rows = []
    start_base = datetime(2024, 1, 1)

    for case_id in range(1, n_cases + 1):
        # pick variant
        names = list(variants.keys())
        probs = [v[1] for v in variants.values()]
        variant_name = random.choices(names, weights=probs)[0]
        steps = variants[variant_name][0]

        # random case start
        case_start = start_base + timedelta(days=random.randint(0, 300))
        ts = case_start
        amount = round(random.uniform(500, 250_000), 2)
        resource_pool = ["Alice","Bob","Carol","Dave","Eve","SAP-Auto","System"]

        for step in steps:
            mean_h, std_h, _ = STEP_DURATIONS.get(step, (2.0, 1.0, False))
            duration = max(0.1, np.random.normal(mean_h, std_h))
            end_ts = ts + timedelta(hours=duration)
            rows.append({
                "case_id":       f"{process}-{case_id:04d}",
                "activity":      step,
                "start_time":    ts,
                "end_time":      end_ts,
                "duration_hrs":  round(duration, 2),
                "resource":      random.choice(resource_pool),
                "variant":       variant_name,
                "process":       process,
                "amount_usd":    amount,
            })
            ts = end_ts

    df = pd.DataFrame(rows)
    df["is_bottleneck"] = df["activity"].map(
        lambda a: STEP_DURATIONS.get(a, (0,0,False))[2]
    )
    df["ai_opportunity"] = df["activity"].map(
        lambda a: AI_OPPORTUNITY.get(a, random.randint(10, 40))
    )
    return df


def get_process_stats(df: pd.DataFrame) -> dict:
    cases = df.groupby("case_id").agg(
        total_hrs=("duration_hrs","sum"),
        steps=("activity","count"),
        amount=("amount_usd","first"),
        variant=("variant","first"),
    ).reset_index()

    happy_cases = cases[cases["variant"] == "Happy Path"]
    non_happy   = cases[cases["variant"] != "Happy Path"]

    bottleneck_time = df[df["is_bottleneck"]]["duration_hrs"].sum()
    total_time      = df["duration_hrs"].sum()

    return {
        "total_cases":         len(cases),
        "total_activities":    len(df),
        "happy_path_pct":      round(len(happy_cases) / len(cases) * 100, 1),
        "avg_cycle_time_hrs":  round(cases["total_hrs"].mean(), 1),
        "happy_cycle_hrs":     round(happy_cases["total_hrs"].mean(), 1) if len(happy_cases) else 0,
        "non_happy_cycle_hrs": round(non_happy["total_hrs"].mean(), 1)   if len(non_happy) else 0,
        "bottleneck_pct":      round(bottleneck_time / total_time * 100, 1),
        "total_value_usd":     round(cases["amount"].sum()),
        "at_risk_value_usd":   round(non_happy["amount"].sum()),
        "variant_counts":      cases["variant"].value_counts().to_dict(),
    }


def get_bottlenecks(df: pd.DataFrame) -> pd.DataFrame:
    bn = (
        df[df["is_bottleneck"]]
        .groupby("activity")
        .agg(
            occurrences=("case_id","count"),
            avg_duration_hrs=("duration_hrs","mean"),
            total_hrs=("duration_hrs","sum"),
            ai_score=("ai_opportunity","first"),
        )
        .reset_index()
        .sort_values("total_hrs", ascending=False)
    )
    bn["cost_impact_usd"] = (bn["total_hrs"] * 85).round(0)   # $85 / hr blended rate
    bn["ai_savings_usd"]  = (bn["cost_impact_usd"] * bn["ai_score"] / 100 * 0.7).round(0)
    return bn.head(5)


def get_variant_flow(df: pd.DataFrame, variant: str) -> list:
    sub = df[df["variant"] == variant].sort_values("start_time")
    return sub["activity"].unique().tolist()
