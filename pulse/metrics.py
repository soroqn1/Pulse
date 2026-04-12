import psutil


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    memory = psutil.virtual_memory()
    return {
        "total": memory.total,
        "percent": memory.percent,
        "used": memory.used,
        "available": memory.available,
    }


def get_net_io_counters():
    return psutil.net_io_counters()


def get_all_metrics():
    return {
        "cpu_usage": get_cpu_usage(),
        "memory_usage": get_memory_usage(),
        "net_io_counters": get_net_io_counters(),
    }


# TEMP
if __name__ == "__main__":
    metrics = get_all_metrics()
    print(metrics)
