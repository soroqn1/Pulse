import logging
import os

import docker
from docker.errors import DockerException

logger = logging.getLogger(__name__)


def get_client():
    try:
        return docker.from_env()
    except DockerException as e:
        home = os.path.expanduser("~")
        orbstack_sock = f"{home}/.orbstack/run/docker.sock"
        if os.path.exists(orbstack_sock):
            try:
                return docker.DockerClient(base_url=f"unix://{orbstack_sock}")
            except DockerException as e2:
                logger.error(f"Failed to connect to OrbStack Docker daemon: {e2}")
                return None

        logger.error(f"Failed to connect to Docker daemon: {e}")
        return None


def get_containers():
    client = get_client()
    if not client:
        return []
    try:
        return client.containers.list(all=True)
    except Exception as e:
        logger.error(f"Error fetching containers: {e}")
        return []


def _execute_action(container_id: str, action: str, **kwargs) -> bool:
    client = get_client()
    if not client:
        return False
    try:
        container = client.containers.get(container_id)
        action_method = getattr(container, action)
        action_method(**kwargs)
        return True
    except Exception as e:
        logger.error(f"Error executing '{action}' on container {container_id}: {e}")
        return False


def start_container(container_id: str) -> bool:
    return _execute_action(container_id, "start")


def stop_container(container_id: str) -> bool:
    return _execute_action(container_id, "stop")


def restart_container(container_id: str) -> bool:
    return _execute_action(container_id, "restart")


def remove_container(container_id: str) -> bool:
    return _execute_action(container_id, "remove", force=True, v=False)


def get_container_logs(container_id: str, tail: int = 100):
    client = get_client()
    if not client:
        return "Docker daemon not running?"
    try:
        container = client.containers.get(container_id)
        logs = container.logs(tail=tail).decode("utf-8")
        return logs
    except Exception as e:
        logger.error(f"Error fetching logs for container {container_id}: {e}")
        return f"Error: {e}"
