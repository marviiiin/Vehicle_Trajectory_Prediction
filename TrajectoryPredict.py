import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from main_2 import VehicleSimulation

class VehicleTrajectoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Predicting Vehicle Trajectories")
        self.root.geometry("800x600")

        self.init_menu()
        self.init_inputs()
        self.init_plot()

    def init_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save Image", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def init_inputs(self):
        input_frame = tk.Frame(self.root)
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Number of Vehicles
        tk.Label(input_frame, text="Number of Vehicles:").pack(anchor="w")
        self.n_var = tk.IntVar(value=5)
        self.n_dropdown = ttk.Combobox(input_frame, textvariable=self.n_var, values=list(range(3, 11)))
        self.n_dropdown.pack(fill=tk.X)

        # Velocity
        tk.Label(input_frame, text="Velocity (mi/hr):").pack(anchor="w")
        self.velocity_var = tk.DoubleVar(value=50)
        tk.Entry(input_frame, textvariable=self.velocity_var).pack(fill=tk.X)

        # Initial Headway
        tk.Label(input_frame, text="Initial Headway (sec):").pack(anchor="w")
        self.headway_var = tk.DoubleVar(value=10)
        tk.Entry(input_frame, textvariable=self.headway_var).pack(fill=tk.X)

        # Minimum Headway
        tk.Label(input_frame, text="Min. Headway (sec):").pack(anchor="w")
        self.min_headway_var = tk.DoubleVar(value=2)
        tk.Entry(input_frame, textvariable=self.min_headway_var).pack(fill=tk.X)

        # Traffic Red Signal Start and End Times
        tk.Label(input_frame, text="Traffic Red Signal Start Time (sec):").pack(anchor="w")
        self.t1_var = tk.DoubleVar(value=50)
        tk.Entry(input_frame, textvariable=self.t1_var).pack(fill=tk.X)

        tk.Label(input_frame, text="Traffic Red Signal End Time (sec):").pack(anchor="w")
        self.t2_var = tk.DoubleVar(value=80)
        tk.Entry(input_frame, textvariable=self.t2_var).pack(fill=tk.X)

        # Vehicle Lengths
        tk.Label(input_frame, text="Do vehicles have the same lengths?").pack(anchor="w")
        self.same_length_var = tk.StringVar(value="yes")
        ttk.Radiobutton(input_frame, text="Yes", variable=self.same_length_var, value="yes", command=self.toggle_length_inputs).pack(anchor="w")
        ttk.Radiobutton(input_frame, text="No", variable=self.same_length_var, value="no", command=self.toggle_length_inputs).pack(anchor="w")

        self.length_frame = tk.Frame(input_frame)
        self.length_frame.pack(fill=tk.X)
        self.length_entries = []
        self.update_length_inputs()

        # Run Simulation Button
        tk.Button(input_frame, text="Run Simulation", command=self.run_simulation).pack(pady=10)

    def init_plot(self):
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def toggle_length_inputs(self):
        for widget in self.length_frame.winfo_children():
            widget.destroy()
        self.length_entries.clear()
        self.update_length_inputs()

    def update_length_inputs(self):
        if self.same_length_var.get() == "yes":
            tk.Label(self.length_frame, text="Vehicle Length (ft):").pack(anchor="w")
            self.length_entries.append(tk.DoubleVar(value=20))
            tk.Entry(self.length_frame, textvariable=self.length_entries[0]).pack(fill=tk.X)
        else:
            for i in range(self.n_var.get()):
                tk.Label(self.length_frame, text=f"Length of Vehicle {i+1} (ft):").pack(anchor="w")
                length_var = tk.DoubleVar(value=20)
                self.length_entries.append(length_var)
                tk.Entry(self.length_frame, textvariable=length_var).pack(fill=tk.X)

    def run_simulation(self):
        n = self.n_var.get()
        velocity = self.velocity_var.get()/3600
        headway = self.headway_var.get()
        min_headway = self.min_headway_var.get()
        t1 = self.t1_var.get()
        t2 = self.t2_var.get()

        if self.same_length_var.get() == "yes":
            lengths = [self.length_entries[0].get()] * n
        else:
            lengths = [length_var.get() for length_var in self.length_entries]

        simulation = VehicleSimulation(
            n=n, 
            velocity=velocity, 
            headway=headway, 
            min_headway=min_headway, 
            final_velocity=30  # Assuming a fixed final velocity
        )
        simulation.flatline_ranges = [(t1, t2 + 2 * i) for i in range(n)]
        simulation.run_simulation()

        self.update_plot(simulation)

    def update_plot(self, simulation):
        self.ax.clear()
        
        # Plot vehicle trajectories
        for times, distances in zip(simulation.time_list, simulation.distance_list):
            if len(times) > len(distances):
                times = times[:len(distances)]
            self.ax.plot(times, distances)
        
        # Plot the red horizontal line for the red signal
        t1 = self.t1_var.get()
        t2 = self.t2_var.get()
        y_value = 0.5
    
        # Red line from t1 to t2
        self.ax.plot([t1, t2], [y_value, y_value], color='red', linestyle='-', linewidth=3)
        
        # Green line from 0 to t1-1
        self.ax.plot([0, t1 - 1], [y_value, y_value], color='green', linestyle='-', linewidth=3)
        
        # Green line from t2+1 to 150
        self.ax.plot([t2 + 1, 150], [y_value, y_value], color='green', linestyle='-', linewidth=3)
        
        # Configure axes
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Space (mi)")
        self.ax.set_title("Space vs Time")
        self.ax.grid()
        self.canvas.draw()


    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
        if file_path:
            self.figure.savefig(file_path)
            messagebox.showinfo("Save Image", f"Plot saved to {file_path}")

    def show_about(self):
        messagebox.showinfo("About", "Predicting Vehicle Trajectories\nDeveloped by Marvin Osei-Kuffour")

if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleTrajectoryApp(root)
    root.mainloop()
