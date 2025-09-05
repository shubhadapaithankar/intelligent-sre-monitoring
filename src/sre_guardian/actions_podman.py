from podman import PodmanClient
import os

PODMAN_BASE_URL = os.getenv("PODMAN_BASE_URL", "unix:///run/podman/podman.sock")
PODMAN_DRY_RUN = os.getenv("PODMAN_DRY_RUN", "true").lower() == "true"

def _client():
    return PodmanClient(base_url=PODMAN_BASE_URL)

def restart_container(container_name: str):
    if PODMAN_DRY_RUN:
        return {"ok":True,"dry_run":True}
    with _client() as c:
        cont = c.containers.get(container_name)
        cont.restart()
    return {"ok":True,"dry_run":False}
