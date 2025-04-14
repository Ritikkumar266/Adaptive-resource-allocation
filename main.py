from process_simulator import SimulatedProgram
from resource_allocator import ResourceAllocator
from scheduler import CPUScheduler
from monitor import monitor_system
from visualizer import live_plot

import time
import matplotlib.pyplot as plt

def main():
    # Create simulated programs
    p1 = SimulatedProgram("Program-A")
    p2 = SimulatedProgram("Program-B")
    p3 = SimulatedProgram("Program-C")

    programs = [p1, p2, p3]

    # Start programs
    for p in programs:
        p.start()

    allocator = ResourceAllocator(programs)
    scheduler = CPUScheduler(programs)

    cpu_history = []
    mem_history = []

    plt.ion()  # Interactive mode for real-time plotting

    try:
        for _ in range(5):  # Run for 20 cycles
            allocator.allocate()
            cpu, mem = monitor_system()
            cpu_history.append(cpu)
            mem_history.append(mem)

            if len(cpu_history) > 50:
                cpu_history.pop(0)
                mem_history.pop(0)

            live_plot(cpu_history, mem_history)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping programs...")
    finally:
        for p in programs:
            p.stop()
        for p in programs:
            p.join()
        print("All programs stopped.")

if __name__ == "__main__":
    main()
