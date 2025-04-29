import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import sys
import io
import datetime
from process_simulator import SimulatedProgram
from resource_allocator import ResourceAllocator
from monitor import monitor_system
from scheduler import CPUScheduler


class RedirectText(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class ResourceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Adaptive Resource Allocation System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#eef1f6")

        self.running = False
        self.cpu_history = []
        self.mem_history = []
        self.programs = []
        self.allocator = None
        self.scheduler = None
        self.start_time = None
        self.program_frames = {}

        self.TOTAL_MEMORY_MB = 1000  # Used to normalize memory usage for graph

        self.create_widgets()

    def create_widgets(self):
        left_frame = tk.Frame(self.root, bg="#f0f4f8")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        right_frame = tk.Frame(self.root, bg="#e7eff6")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.start_button = ttk.Button(right_frame, text="▶ Start Simulation", command=self.start_simulation)
        self.start_button.pack(pady=(5, 4))

        self.stop_button = ttk.Button(right_frame, text="■ Stop Simulation", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.pack(pady=(2, 2))

        self.save_button = ttk.Button(right_frame, text="💾 Save Graph", command=self.save_graph)
        self.save_button.pack(pady=(2, 3))

        self.status_label = tk.Label(right_frame, text="🔴 Status: Stopped", font=("Arial", 12), fg="red", bg="#e7eff6")
        self.status_label.pack(pady=3)

        self.output_text = tk.Text(right_frame, height=10, width=60, bg="#1e1e1e", fg="lime", font=("Consolas", 12))
        self.output_text.pack(padx=3, pady=3)
        sys.stdout = RedirectText(self.output_text)

        self.summary_label = tk.Label(right_frame, text="📊 Summary", font=("Arial", 12, "bold"), bg="#e7eff6")
        self.summary_label.pack(pady=(10, 0))

        self.summary_text = tk.Label(right_frame, text="", justify=tk.LEFT, font=("Arial", 10), bg="#e7eff6")
        self.summary_text.pack()

        self.program_container = tk.Frame(right_frame, bg="#e7eff6")
        self.program_container.pack(pady=10)

        for name in ['A', 'B', 'C']:
            frame = tk.LabelFrame(self.program_container, text=f"Program-{name}", bg="#dee8f2", font=("Arial", 8, "bold"), bd=3)
            frame.pack(fill="x", padx=5, pady=5)

            cpu_label = tk.Label(frame, text="CPU: 0.00%", fg="blue", bg="#dee8f2", font=("Arial", 6))
            cpu_label.pack(anchor="w", padx=6)

            cpu_bar = ttk.Progressbar(frame, orient='horizontal', length=150, mode='determinate', maximum=80)
            cpu_bar.pack(padx=8, pady=1)

            mem_label = tk.Label(frame, text="Memory: 0.00 MB", fg="green", bg="#dee8f2", font=("Arial", 6))
            mem_label.pack(anchor="w", padx=6)

            mem_bar = ttk.Progressbar(frame, orient='horizontal', length=150, mode='determinate', maximum=800)
            mem_bar.pack(padx=8, pady=(0, 3))

            self.program_frames[f"Program-{name}"] = {
                "cpu_label": cpu_label,
                "cpu_bar": cpu_bar,
                "mem_label": mem_label,
                "mem_bar": mem_bar
            }

        self.figure = plt.Figure(figsize=(3.5, 2.0), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=left_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start_simulation(self):
        self.running = True
        self.start_time = time.time()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="🟢 Status: Running", fg="green")

        self.cpu_history = []
        self.mem_history = []
        self.programs = [SimulatedProgram(f"Program-{c}") for c in ['A', 'B', 'C']]
        for p in self.programs:
            p.start()
            print(f"✔ Started {p.name}")

        self.allocator = ResourceAllocator(self.programs)
        self.scheduler = CPUScheduler(self.programs)

        self.scheduler_thread = Thread(target=self.scheduler.run)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

        self.sim_thread = Thread(target=self.run_simulation)
        self.sim_thread.start()

    def run_simulation(self):
        while self.running:
            self.allocator.allocate()

            if hasattr(self, 'scheduler'):
                self.scheduler.last_cpu_usages = {
                    p.name: getattr(p, 'cpu_usage', 0.0) for p in self.programs
                }

            cpu, _ = monitor_system()  # Only use CPU usage from system monitor

            # ✅ Simulated memory percentage based on program usage
            total_used = sum(p.memory_usage for p in self.programs)
            mem_percentage = (total_used / self.TOTAL_MEMORY_MB) * 100

            self.cpu_history.append(cpu)
            self.mem_history.append(mem_percentage)

            if len(self.cpu_history) > 30:
                self.cpu_history.pop(0)
                self.mem_history.pop(0)

            self.update_plot()
            self.update_summary()
            self.update_program_panels()
            time.sleep(1)


    def stop_simulation(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="🔴 Status: Stopped", fg="red")

        for p in self.programs:
            p.stop()
        for p in self.programs:
            p.join()

        if hasattr(self, 'scheduler'):
            self.scheduler.stop()

    def update_plot(self):
        self.ax.clear()
        self.ax.plot(self.cpu_history, label="CPU Usage (%)", color="blue")
        self.ax.plot(self.mem_history, label="Memory Usage (%)", color="green")
        self.ax.set_title("Live CPU & Memory Usage", fontsize=10)
        self.ax.set_xlabel("Time (seconds)", fontsize=9)
        self.ax.set_ylabel("Usage (%)", fontsize=9)
        self.ax.set_ylim(0, 100)
        self.ax.legend(fontsize=8)
        self.ax.grid(True, linestyle="--", alpha=0.3)
        self.canvas.draw()

    def update_program_panels(self):
        for p in self.programs:
            name = p.name
            cpu = getattr(p, 'cpu_usage', 0.0)
            mem = getattr(p, 'memory_usage', 0.0)

            if name in self.program_frames:
                frame = self.program_frames[name]
                frame["cpu_label"].config(text=f"CPU: {cpu:.2f}%")
                frame["cpu_bar"]["value"] = cpu
                frame["mem_label"].config(text=f"Memory: {mem:.2f} MB")
                frame["mem_bar"]["value"] = mem

    def update_summary(self):
        avg_cpu = sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0
        peak_mem = max(self.mem_history) if self.mem_history else 0
        uptime = str(datetime.timedelta(seconds=int(time.time() - self.start_time))) if self.start_time else "0s"
        summary = f"Avg CPU: {avg_cpu:.2f}%\nPeak Memory: {peak_mem:.2f}%\nUptime: {uptime}"
        self.summary_text.config(text=summary)

    def save_graph(self):
        filename = f"resource_graph_{int(time.time())}.png"
        self.figure.savefig(filename)
        messagebox.showinfo("Graph Saved", f"Graph saved as {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ResourceApp(root)
    root.mainloop()
