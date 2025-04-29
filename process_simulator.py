import threading
import time
import random

class SimulatedProgram(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.running = True
        self.cpu_usage = 0.0
        self.memory_usage = random.uniform(100, 500)
        self.lock = threading.Lock()

    def run(self):
        while self.running:
            with self.lock:
                self.cpu_usage = random.uniform(5, 30)
            time.sleep(1)

    def stop(self):
        self.running = False
