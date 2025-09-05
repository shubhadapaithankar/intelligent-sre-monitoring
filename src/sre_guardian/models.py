import joblib
import numpy as np
import pandas as pd
import os
from sklearn.ensemble import IsolationForest

MODEL_PATH = "/tmp/nn_slo_iforest.joblib"

FEATURE_COLS = [
    # CPU
    "cpu_mean","cpu_std","cpu_p95","cpu_max","cpu_min","cpu_slope",
    # MEM
    "mem_mean","mem_std","mem_p95","mem_max","mem_min","mem_slope",
    # THROTTLE
    "thr_mean","thr_p95","thr_max",
    # RESTARTS
    "restarts_mean","restarts_max",
    # LATENCY
    "lat_mean","lat_p95","lat_max"
]

def _ensure_cols(df: pd.DataFrame) -> pd.DataFrame:
    for c in FEATURE_COLS:
        if c not in df.columns:
            df[c] = 0.0
    return df

def train_iforest(features: pd.DataFrame):
    if features is None or features.empty:
        return None
    X = _ensure_cols(features)[FEATURE_COLS].to_numpy()
    clf = IsolationForest(
        n_estimators=200,
        contamination=float(os.getenv("ISOFOREST_CONTAM", "0.07")),
        random_state=42,
    )
    clf.fit(X)
    joblib.dump(clf, MODEL_PATH)
    return clf

def load_or_train(features: pd.DataFrame):
    try:
        clf = joblib.load(MODEL_PATH)
    except Exception:
        clf = train_iforest(features)
    return clf

def score_anomalies(features: pd.DataFrame) -> pd.DataFrame:
    if features is None or features.empty:
        return pd.DataFrame()
    clf = load_or_train(features)
    if clf is None:
        return pd.DataFrame()
    X = _ensure_cols(features)[FEATURE_COLS].to_numpy()
    raw = -clf.decision_function(X)  # higher = more anomalous
    scores = (raw - raw.min()) / (raw.max() - raw.min() + 1e-9)  # normalize 0..1
    out = features[["namespace","pod","container"]].copy()
    out["anomaly_score"] = scores
    return out.sort_values("anomaly_score", ascending=False).reset_index(drop=True)
