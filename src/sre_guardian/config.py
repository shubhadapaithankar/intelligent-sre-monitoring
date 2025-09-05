import os
from pydantic import BaseModel

class Settings(BaseModel):
    # Prometheus
    PROM_URL: str = os.getenv("PROM_URL", "http://prometheus.monitoring:9090")
    METRIC_STEP: str = os.getenv("METRIC_STEP", "60s")
    HISTORY_HOURS: int = int(os.getenv("HISTORY_HOURS", "24"))
    LOOKBACK_MINUTES: int = int(os.getenv("LOOKBACK_MINUTES", "30"))

    # Kubernetes
    K8S_IN_CLUSTER: bool = os.getenv("K8S_IN_CLUSTER", "true").lower() == "true"
    NAMESPACE: str = os.getenv("NAMESPACE", "")  # empty = all
    K8S_DRY_RUN: bool = os.getenv("K8S_DRY_RUN", "true").lower() == "true"

    # Podman
    PODMAN_BASE_URL: str = os.getenv("PODMAN_BASE_URL", "unix:///run/podman/podman.sock")
    PODMAN_DRY_RUN: bool = os.getenv("PODMAN_DRY_RUN", "true").lower() == "true"

    # Modeling / thresholds
    TOP_K: int = int(os.getenv("TOP_K", "10"))
    ISOFOREST_CONTAM: float = float(os.getenv("ISOFOREST_CONTAM", "0.07"))
    ANOMALY_THRESH: float = float(os.getenv("ANOMALY_THRESH", "0.65"))
    SLO_P95_TARGET_MS: float = float(os.getenv("SLO_P95_TARGET_MS", "300.0"))  # example SLO

settings = Settings()
