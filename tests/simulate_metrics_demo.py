import os, sys
from pathlib import Path
# Make src available on path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from sre_guardian.features import build_feature_table
from sre_guardian.models import score_anomalies

def synth_series(ns, pod, container, seed=0, leak=False, noisy=False, n=300):
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    cpu = rng.normal(0.2, 0.05, size=n)
    mem = rng.normal(200*1024**2, 20*1024**2, size=n)  # bytes
    thr = np.clip(rng.normal(0.0, 0.005, size=n), 0, None)
    restarts = np.zeros(n)
    lat = rng.normal(0.12, 0.02, size=n)  # ~120ms

    if leak:
        mem = mem + (t * 300_000)  # slow increase
    if noisy:
        cpu = cpu + np.sin(t/5)*0.2 + rng.normal(0,0.1,size=n)
        thr = thr + np.abs(np.sin(t/10))*0.02
        lat = lat + np.abs(np.sin(t/7))*0.06

    ts = pd.date_range("2024-01-01", periods=n, freq="min")
    def df(vals):
        out = pd.DataFrame({"ts": ts, "value": vals})
        out["namespace"] = ns; out["pod"] = pod; out["container"] = container
        return out

    return {
        "cpu": df(cpu),
        "mem": df(mem),
        "throttle": df(thr),
        "restarts": df(restarts),
        "http_p95": df(lat),
    }

def main():
    # Build combined metric frames for multiple services
    combined = {"cpu": pd.DataFrame(), "mem": pd.DataFrame(), "throttle": pd.DataFrame(),
                "restarts": pd.DataFrame(), "http_p95": pd.DataFrame()}

    scenarios = [
        ("prod", "svc-a-123", "app", dict(seed=1)),
        ("prod", "svc-b-999", "app", dict(seed=2)),
        ("prod", "svc-leak-777", "app", dict(seed=3, leak=True)),
        ("prod", "svc-noisy-555", "app", dict(seed=4, noisy=True)),
    ]

    for ns, pod, container, kw in scenarios:
        series = synth_series(ns, pod, container, **kw)
        for k, df in series.items():
            combined[k] = pd.concat([combined[k], df], ignore_index=True)

    feats = build_feature_table(combined)
    scores = score_anomalies(feats)

    print("Top anomalies:")
    print(scores.head(10).to_string(index=False))

if __name__ == "__main__":
    main()
