import time

class CPUScheduler:
    def __init__(self, programs):
        self.programs = programs

    def run(self):
        while True:
            for p in self.programs:
                print(f"[Scheduler] Running {p.name} on CPU")
                time.sleep(1)
