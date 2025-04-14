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
        self.root.configure(bg="white")

        self.running = False
        self.cpu_history = []
        self.mem_history = []
        self.programs = []
        self.allocator = None
        self.start_time = None

        self.create_widgets()

    def create_widgets(self):
        # Frames
        left_frame = tk.Frame(self.root, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        right_frame = tk.Frame(self.root, bg="white")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Buttons
        self.start_button = ttk.Button(right_frame, text="▶ Start Simulation", command=self.start_simulation)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(right_frame, text="■ Stop Simulation", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.save_button = ttk.Button(right_frame, text="💾 Save Graph", command=self.save_graph)
        self.save_button.pack(pady=5)

        # Status
        self.status_label = tk.Label(right_frame, text="🔴 Status: Stopped", font=("Arial", 12), fg="red", bg="white")
        self.status_label.pack(pady=10)

        # Output log
        self.output_text = tk.Text(right_frame, height=20, width=48, bg="black", fg="lime", font=("Consolas", 12))
        self.output_text.pack(padx=5, pady=5)
        sys.stdout = RedirectText(self.output_text)

        # Summary
        self.summary_label = tk.Label(right_frame, text="📊 Summary", font=("Arial", 12, "bold"), bg="white")
        self.summary_label.pack(pady=(10, 0))
        self.summary_text = tk.Label(right_frame, text="", justify=tk.LEFT, font=("Arial", 10), bg="white")
        self.summary_text.pack()

        # Program table
        self.tree = ttk.Treeview(right_frame, columns=("CPU", "Memory"), show="headings", height=5)
        self.tree.heading("CPU", text="CPU (%)")
        self.tree.heading("Memory", text="Memory (%)")
        self.tree.column("CPU", width=80)
        self.tree.column("Memory", width=100)
        self.tree.pack(pady=10)

        # Graph
        self.figure = plt.Figure(figsize=(4, 2.5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=left_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start_simulation(self):
        self.running = True
        self.start_time = time.time()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="🟢 Status: Running", fg="green")

        self.programs = [SimulatedProgram(f"Program-{c}") for c in ['A', 'B', 'C']]
        for p in self.programs:
            p.start()
            print(f"✔ Started {p.name}")

        self.allocator = ResourceAllocator(self.programs)
        self.sim_thread = Thread(target=self.run_simulation)
        self.sim_thread.start()

    def run_simulation(self):
        while self.running:
            self.allocator.allocate()
            cpu, mem = monitor_system()
            print(f"📈 CPU: {cpu:.2f}% | Memory: {mem:.2f}%")

            self.cpu_history.append(cpu)
            self.mem_history.append(mem)

            if len(self.cpu_history) > 50:
                self.cpu_history.pop(0)
                self.mem_history.pop(0)

            self.update_plot()
            self.update_table()
            self.update_summary()

            time.sleep(1)

    def stop_simulation(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="🔴 Status: Stopped", fg="red")

        for p in self.programs:
            p.stop()
            print(f"✖ Stopped {p.name}")
        for p in self.programs:
            p.join()

        print("✔ Simulation stopped.\n")

    def update_plot(self):
        self.ax.clear()
        self.ax.plot(self.cpu_history, label="CPU Usage (%)", color="blue")
        self.ax.plot(self.mem_history, label="Memory Usage (%)", color="green")
        self.ax.set_title("Live CPU & Memory Usage", fontsize=10)
        
        # ✅ Add these lines:
        self.ax.set_xlabel("Time (seconds)", fontsize=9)
        self.ax.set_ylabel("Usage (%)", fontsize=9)
        
        self.ax.set_ylim(0, 100)
        self.ax.legend(fontsize=8)
        self.ax.grid(True, linestyle="--", alpha=0.3)
        self.canvas.draw()


    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in self.programs:
            cpu = getattr(p, 'cpu_usage', 0.0)
            mem = getattr(p, 'memory_usage', 0.0)
            self.tree.insert('', 'end', values=(f"{cpu:.2f}", f"{mem:.2f}"))

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
