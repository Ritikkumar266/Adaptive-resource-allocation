import psutil

def monitor_system():
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    # Return percentage used instead of MB
    return cpu, mem.percent
