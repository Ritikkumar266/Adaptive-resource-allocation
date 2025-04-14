import threading
import time
import random

class SimulatedProgram(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.running = True
        self.cpu_usage = 0.0
        self.memory_usage = 0.0

    def run(self):
        while self.running:
            # Simulate changing CPU and memory usage
            self.cpu_usage = random.uniform(1, 30)  # Simulated CPU usage
            self.memory_usage = random.uniform(100, 500)  # Simulated memory in MB
            print(f"{self.name} is running using {self.memory_usage:.0f} MB")
            time.sleep(1)

    def stop(self):
        self.running = False
