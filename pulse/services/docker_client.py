import docker
from docker.errors import DockerException
import logging

logger = logging.getLogger(__name__)

def get_client():
    try:
        return docker.from_env()
    except DockerException as e:
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

def start_container(container_id: str):
    client = get_client()
    if not client: return False
    try:
        container = client.containers.get(container_id)
        container.start()
        return True
    except Exception as e:
        logger.error(f"Error starting container {container_id}: {e}")
        return False

def stop_container(container_id: str):
    client = get_client()
    if not client: return False
    try:
        container = client.containers.get(container_id)
        container.stop()
        return True
    except Exception as e:
        logger.error(f"Error stopping container {container_id}: {e}")
        return False

def restart_container(container_id: str):
    client = get_client()
    if not client: return False
    try:
        container = client.containers.get(container_id)
        container.restart()
        return True
    except Exception as e:
        logger.error(f"Error restarting container {container_id}: {e}")
        return False

def get_container_logs(container_id: str, tail: int = 100):
    client = get_client()
    if not client: return "Docker daemon not running?"
    try:
        container = client.containers.get(container_id)
        logs = container.logs(tail=tail).decode('utf-8')
        return logs
    except Exception as e:
        logger.error(f"Error fetching logs for container {container_id}: {e}")
        return f"Error: {e}"
