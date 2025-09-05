import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np

from sre_guardian.collectors import PromCollector
from sre_guardian.features import build_feature_table
from sre_guardian.models import score_anomalies
from sre_guardian.rca import annotate_with_rca
from sre_guardian.actions_k8s import roll_restart_deployment, scale_deployment, restart_pod
from sre_guardian.actions_podman import restart_container

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

app = FastAPI(title="NN-SLO", version="1.1")

class ActionRequest(BaseModel):
    kind: str  # k8s.roll_restart | k8s.scale | k8s.restart_pod | podman.restart
    namespace: str | None = None
    deployment: str | None = None
    pod: str | None = None
    replicas: int | None = None
    container_name: str | None = None

@app.get("/healthz")
def healthz():
    return {"ok": True}

def _demo_metrics():
    def mk(ns,pod,container,seed=0,leak=False,noisy=False,n=300):
        rng = np.random.default_rng(seed); t = np.arange(n)
        cpu = rng.normal(0.2,0.05,n); mem = rng.normal(200*1024**2, 20*1024**2, n)
        thr = np.clip(rng.normal(0.0,0.005,n),0,None); restarts = np.zeros(n)
        lat = rng.normal(0.12,0.02,n)
        if leak: mem = mem + t*300_000
        if noisy:
            cpu = cpu + np.sin(t/5)*0.2 + rng.normal(0,0.1,n)
            thr = thr + np.abs(np.sin(t/10))*0.02
            lat = lat + np.abs(np.sin(t/7))*0.06
        ts = pd.date_range("2024-01-01", periods=n, freq="min")
        def df(vals):
            out = pd.DataFrame({"ts": ts, "value": vals})
            out["namespace"]=ns; out["pod"]=pod; out["container"]=container
            return out
        return {"cpu":df(cpu),"mem":df(mem),"throttle":df(thr),"restarts":df(restarts),"http_p95":df(lat)}
    combined = {k: pd.DataFrame() for k in ["cpu","mem","throttle","restarts","http_p95"]}
    for (ns,pod,container,kw) in [
        ("prod","svc-a-123","app",dict(seed=1)),
        ("prod","svc-b-999","app",dict(seed=2)),
        ("prod","svc-leak-777","app",dict(seed=3, leak=True)),
        ("prod","svc-noisy-555","app",dict(seed=4, noisy=True)),
    ]:
        ser = mk(ns,pod,container,**kw)
        for k,df in ser.items():
            combined[k] = pd.concat([combined[k], df], ignore_index=True)
    return combined

@app.get("/anomalies")
def anomalies(namespace: str | None = None, top_k: int = 10):
    coll = PromCollector()
    metrics = coll.collect_all(namespace_filter=namespace)
    # If everything is empty, use DEMO_MODE or return empty list
    if all(df is None or df.empty for df in metrics.values()):
        if DEMO_MODE:
            metrics = _demo_metrics()
        else:
            return {"anomalies": []}
    feats = build_feature_table(metrics)
    if feats is None or feats.empty:
        return {"anomalies":[]}
    scores = score_anomalies(feats)
    joined = annotate_with_rca(feats, scores)
    out = joined.head(top_k)[["namespace","pod","container","anomaly_score","rca"]]
    return {"anomalies": out.to_dict(orient="records")}

@app.post("/suggest")
def suggest(namespace: str | None = None):
    return anomalies(namespace=namespace, top_k=10)

@app.post("/act")
def act(req: ActionRequest):
    if req.kind == "k8s.roll_restart":
        if not (req.namespace and req.deployment):
            raise HTTPException(400, "namespace and deployment required")
        return roll_restart_deployment(req.namespace, req.deployment)
    if req.kind == "k8s.scale":
        if not (req.namespace and req.deployment and req.replicas is not None):
            raise HTTPException(400, "namespace, deployment, replicas required")
        return scale_deployment(req.namespace, req.deployment, req.replicas)
    if req.kind == "k8s.restart_pod":
        if not (req.namespace and req.pod):
            raise HTTPException(400, "namespace and pod required")
        return restart_pod(req.namespace, req.pod)
    if req.kind == "podman.restart":
        if not req.container_name:
            raise HTTPException(400, "container_name required")
        return restart_container(req.container_name)
    raise HTTPException(400, "unknown kind")



