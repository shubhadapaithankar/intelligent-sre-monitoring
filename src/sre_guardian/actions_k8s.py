from typing import Dict
from kubernetes import client, config
import os

K8S_IN_CLUSTER = os.getenv("K8S_IN_CLUSTER", "true").lower() == "true"
K8S_DRY_RUN = os.getenv("K8S_DRY_RUN", "true").lower() == "true"

def _init():
    if K8S_IN_CLUSTER:
        config.load_incluster_config()
    else:
        config.load_kube_config()

# All actions are reversible & dry-run aware
def roll_restart_deployment(namespace: str, deployment: str) -> Dict:
    _init()
    api = client.AppsV1Api()
    body = {"spec":{"template":{"metadata":{"annotations":{"nn-slo/roll-ts":"now"}}}}}
    dr = "All" if K8S_DRY_RUN else None
    api.patch_namespaced_deployment(
        name=deployment, namespace=namespace, body=body, dry_run=dr
    )
    return {"ok":True,"dry_run":K8S_DRY_RUN}

def scale_deployment(namespace: str, deployment: str, replicas: int) -> Dict:
    _init()
    api = client.AppsV1Api()
    body = {"spec":{"replicas": replicas}}
    dr = "All" if K8S_DRY_RUN else None
    api.patch_namespaced_deployment_scale(deployment, namespace, body, dry_run=dr)
    return {"ok":True,"dry_run":K8S_DRY_RUN}

def restart_pod(namespace: str, pod: str) -> Dict:
    _init()
    api = client.CoreV1Api()
    dr = "All" if K8S_DRY_RUN else None
    api.delete_namespaced_pod(name=pod, namespace=namespace, grace_period_seconds=0, dry_run=dr)
    return {"ok":True,"dry_run":K8S_DRY_RUN}
