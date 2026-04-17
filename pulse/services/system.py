import logging

import psutil

logger = logging.getLogger(__name__)

def safe_get(d, key, default):
    return d.get(key) or default

def get_cpu_usage():
    return psutil.cpu_percent(interval=None)

def get_memory_usage():
    memory = psutil.virtual_memory()
    return {
        "total": memory.total,
        "percent": memory.percent,
        "used": memory.used,
        "available": memory.available,
    }

def get_all_metrics():
    return {
        "cpu_usage": get_cpu_usage(),
        "memory_usage": get_memory_usage(),
    }

def get_active_processes(limit=50):
    processes = []
    for proc in psutil.process_iter(
        ["pid", "name", "username", "cpu_percent", "memory_info"]
    ):
        try:
            pinfo = proc.info
            mem_mb = 0
            if pinfo.get("memory_info"):
                mem_mb = pinfo["memory_info"].rss / (1024 * 1024)

            processes.append(
                {
                    "pid": pinfo.get("pid", 0),
                    "name": safe_get(pinfo, "name", "unknown"),
                    "user": safe_get(pinfo, "username", "unknown"),
                    "cpu": pinfo.get("cpu_percent", 0) or 0,
                    "mem_mb": mem_mb,
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.debug(f"Pulse process access error: {e}")

    # Sort by cpu usage
    sorted_procs = sorted(
        processes, key=lambda p: (p["cpu"], p["mem_mb"]), reverse=True
    )
    return sorted_procs[:limit]
