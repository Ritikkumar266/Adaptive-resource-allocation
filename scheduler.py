import time
import random

class CPUScheduler:
    def __init__(self, programs):
        self.programs = programs
        self.last_cpu_usages = {p.name: 0.0 for p in programs}
        self.running = True  # 🔥 Flag to control scheduler loop

    def run(self):
        while self.running:
            self.programs.sort(key=lambda p: self.last_cpu_usages.get(p.name, 0.0))
            for p in self.programs:
                if not self.running:  # 🔥 Check again before allocating
                    break
                cpu_time = self.get_dynamic_quantum(p)
                print(f"[Scheduler] Allocating {cpu_time:.2f}s CPU to {p.name}")
                time.sleep(cpu_time)
                self.last_cpu_usages[p.name] = getattr(p, 'cpu_usage', 0.0)

    def get_dynamic_quantum(self, program):
        cpu = getattr(program, 'cpu_usage', 0.0)
        if cpu < 10:
            return 1.5
        elif cpu < 20:
            return 1.0
        else:
            return 0.5

    def stop(self):  # 🔥 Call this to stop
        self.running = False
