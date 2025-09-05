import numpy as np
import pandas as pd

def _agg_stats(df: pd.DataFrame, value_col="value"):
    if df is None or df.empty:
        return pd.DataFrame()
    group_cols = ["namespace","pod","container"]
    agg = df.groupby(group_cols, dropna=False)[value_col].agg(
        mean="mean", std="std", p95=lambda x: np.nanpercentile(x,95),
        max="max", min="min"
    ).reset_index()
    return agg

def _slope(df: pd.DataFrame, value_col="value"):
    if df is None or df.empty:
        return pd.DataFrame(columns=["namespace","pod","container","slope"])
    def slope_of_group(g):
        x = (g["ts"].astype("int64")//1_000_000_000).to_numpy()
        y = g[value_col].to_numpy()
        if len(x) < 3:
            return 0.0
        x = x - x[0]
        m, _ = np.polyfit(x, y, 1)
        return float(m)
    slopes = df.groupby(["namespace","pod","container"], dropna=False).apply(lambda g: slope_of_group(g)).reset_index()
    slopes.columns = ["namespace","pod","container","slope"]
    return slopes

def build_feature_table(metrics: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # CPU
    cpu_df = metrics.get("cpu")
    cpu = _agg_stats(cpu_df)
    cpu_slope = _slope(cpu_df)
    cpu = cpu.merge(cpu_slope, on=["namespace","pod","container"], how="left", suffixes=("","_cpu"))
    cpu = cpu.add_prefix("cpu_")
    cpu.rename(columns={"cpu_namespace":"namespace","cpu_pod":"pod","cpu_container":"container"}, inplace=True)

    # Memory
    mem_df = metrics.get("mem")
    mem = _agg_stats(mem_df)
    mem_slope = _slope(mem_df)
    mem = mem.merge(mem_slope, on=["namespace","pod","container"], how="left", suffixes=("","_mem"))
    mem = mem.add_prefix("mem_")
    mem.rename(columns={"mem_namespace":"namespace","mem_pod":"pod","mem_container":"container"}, inplace=True)

    # Restarts
    rest = _agg_stats(metrics.get("restarts"))
    rest = rest.add_prefix("restarts_")
    rest.rename(columns={"restarts_namespace":"namespace","restarts_pod":"pod","restarts_container":"container"}, inplace=True)

    # Throttle
    thr = _agg_stats(metrics.get("throttle"))
    thr = thr.add_prefix("thr_")
    thr.rename(columns={"thr_namespace":"namespace","thr_pod":"pod","thr_container":"container"}, inplace=True)

    # HTTP p95
    p95 = _agg_stats(metrics.get("http_p95"))
    p95 = p95.add_prefix("lat_")
    p95.rename(columns={"lat_namespace":"namespace","lat_pod":"pod","lat_container":"container"}, inplace=True)

    # Merge
    dfs = [cpu, mem, rest, thr, p95]
    base = None
    for d in dfs:
        if d is None or d.empty:
            continue
        base = d if base is None else base.merge(d, on=["namespace","pod","container"], how="outer")
    if base is None:
        return pd.DataFrame()
    return base.fillna(0.0)
