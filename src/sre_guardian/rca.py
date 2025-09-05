import pandas as pd
import os

SLO_P95_TARGET_MS = float(os.getenv("SLO_P95_TARGET_MS", "300.0"))

def rca_row(row: pd.Series) -> dict:
    reasons = []
    actions = []
    if row.get("restarts_max", 0) >= 1:
        reasons.append("Container restarted recently (possible crashloop).")
        actions.append({"action":"k8s.restart_pod","reason":"Crash suspected"})
    if row.get("thr_mean", 0) > 0.05 and row.get("cpu_mean",0) > 0.1:
        reasons.append("CPU throttling indicative of CPU pressure.")
        actions.append({"action":"k8s.scale","reason":"Increase CPU/share"})
    if row.get("mem_slope",0) > 0 and row.get("mem_p95",0) > 0:
        reasons.append("Memory increasing over time (possible leak).")
        actions.append({"action":"k8s.roll_restart","reason":"Reset memory footprint"})
    if row.get("lat_p95",0)*1000 > SLO_P95_TARGET_MS:
        reasons.append("p95 latency above target (SLO drift).")
        actions.append({"action":"k8s.scale","reason":"Handle load"})
    if not reasons:
        reasons.append("Generic anomaly detected.")
        actions.append({"action":"none","reason":"Monitor only"})
    return {"reasons":reasons, "suggested_actions":actions}

def annotate_with_rca(features: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    joined = features.merge(scores, on=["namespace","pod","container"], how="inner")
    suggestions = joined.apply(rca_row, axis=1)
    joined["rca"] = suggestions
    return joined.sort_values("anomaly_score", ascending=False).reset_index(drop=True)
