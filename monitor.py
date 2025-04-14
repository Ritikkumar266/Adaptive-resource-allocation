import psutil

def monitor_system():
    cpu_percent = psutil.cpu_percent(interval=0.5)  # Capture CPU usage in %
    mem = psutil.virtual_memory()
    mem_percent = mem.percent  # Get memory usage in %
    return cpu_percent, mem_percent
