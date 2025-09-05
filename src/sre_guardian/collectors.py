import datetime as dt
import logging
import pandas as pd
from prometheus_api_client import PrometheusConnect
from .config import settings

log = logging.getLogger("nn_slo.collectors")

DEFAULT_QUERIES = {
    "cpu": 'sum by (namespace,pod,container) (rate(container_cpu_usage_seconds_total{container!=""}[5m]))',
    "mem": 'sum by (namespace,pod,container) (container_memory_working_set_bytes{container!=""})',
    "restarts": 'max by (namespace,pod,container) (increase(kube_pod_container_status_restarts_total[30m]))',
    "throttle": 'sum by (namespace,pod,container) (rate(container_cpu_cfs_throttled_seconds_total{container!=""}[5m]))',
    "http_p95": 'histogram_quantile(0.95, sum by (le,namespace,pod) (rate(http_server_duration_seconds_bucket[5m])))'
}

class PromCollector:
    def __init__(self, url: str | None = None):
        self.url = url or settings.PROM_URL
        self.prom = PrometheusConnect(url=self.url, disable_ssl=True)

    def _range(self, hours: int, step: str):
        end = dt.datetime.utcnow()
        start = end - dt.timedelta(hours=hours)
        return start, end, step

    def _query_range(self, query: str, hours: int, step: str) -> pd.DataFrame:
        start, end, step = self._range(hours, step)
        try:
            series = self.prom.custom_query_range(query, start_time=start, end_time=end, step=step)
        except Exception as e:
            log.warning("Prometheus query failed (%s). Returning empty frame. URL=%s", e, self.url)
            return pd.DataFrame()

        frames = []
        for s in series:
            metric = s.get("metric", {})
            labels = {k: metric.get(k, "") for k in ("namespace","pod","container")}
            df = pd.DataFrame(s["values"], columns=["ts","value"])
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            for k, v in labels.items():
                df[k] = v
            frames.append(df)
        if not frames:
            return pd.DataFrame()
        out = pd.concat(frames, ignore_index=True)
        out["ts"] = pd.to_datetime(out["ts"], unit="s")
        return out

    def collect_all(self, namespace_filter: str | None = None) -> dict[str, pd.DataFrame]:
        data = {}
        for name, q in DEFAULT_QUERIES.items():
            df = self._query_range(q, settings.HISTORY_HOURS, settings.METRIC_STEP)
            if not df.empty and (namespace_filter or settings.NAMESPACE):
                ns = namespace_filter or settings.NAMESPACE
                if ns:
                    df = df[df["namespace"] == ns]
            data[name] = df
        return data
