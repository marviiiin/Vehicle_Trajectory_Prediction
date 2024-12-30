import numpy as np
import matplotlib.pyplot as plt

class VehicleSimulation:
    def __init__(self, n=5, velocity=50 / 3600, headway=10, min_headway=2, final_velocity=30):
        self.n = n  # Number of vehicles
        self.velocity = velocity  # Velocity in mi/s
        self.headway = headway  # Seconds
        self.min_headway = min_headway
        self.final_velocity = final_velocity
        self.final_time = (3600 / self.final_velocity) + (self.headway * (self.n - 1))
        self.num_of_iteration = int(self.final_time / 0.1)
        self.headway_interval = np.arange(0, self.headway * self.n, self.headway)
        self.time_list = self.generate_time_list()
        self.distance_list = self.create_empty_lists(self.n)
        self.flatline_ranges = self.create_flatline_ranges()

    def generate_time_list(self):
        time_list = []
        for i in self.headway_interval:
            time = np.arange(i, self.final_time, 0.1)
            time_list.append(time)
        return time_list

    def create_empty_lists(self, num):
        return [[] for _ in range(num)]

    def create_flatline_ranges(self):
        return [(50, 80 + 2 * i) for i in range(self.n)]  # Define flatline ranges for each vehicle

    def update_distance(self, distance, current_velocity, time, car_idx):
        start, end = self.flatline_ranges[car_idx]
        target_distance = 0.5 - (car_idx * 0.005)

        if start <= time <= end:
            if distance < target_distance:
                distance += current_velocity * 0.1
                if distance > target_distance:
                    distance = target_distance
            elif distance > target_distance:
                distance += current_velocity * 0.1
        else:
            distance += current_velocity * 0.1

        return distance

    def run_simulation(self):
        # Initialize distance and velocity for dynamic update
        current_velocity = self.velocity

        # Update distances for all cars
        for car_idx, car_distances in enumerate(self.distance_list):
            distance = 0
            for t in self.time_list[car_idx]:
                if len(car_distances) == self.num_of_iteration:
                    break

                # Check if the car reaches or exceeds the target distance before the restriction period starts
                start, _ = self.flatline_ranges[car_idx]
                target_distance = 0.5 - (car_idx * 0.005)

                if t < start and distance >= target_distance:
                    # Car passes unrestricted; continue normal journey
                    distance += current_velocity * 0.1
                else:
                    distance = self.update_distance(distance, current_velocity, t, car_idx)

                distance = round(distance, 5)

                if distance >= 1.0:
                    car_distances.append(1.0)
                    break
                else:
                    car_distances.append(distance)

    def get_plot(self):
    # Return the figure object instead of plotting it
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    
        for times, distances in zip(self.time_list, self.distance_list):
            if len(times) > len(distances):
                times = times[:len(distances)]
            ax.plot(times, distances)  # No label here
    
        # Add the requested horizontal line at 0.5 mi with different color sections
        t1 = 50  # Start of the red section
        t2 = 80  # End of the red section
    
        ax.axhline(y=0.5, xmin=0, xmax=t1 / 160, color='green', linestyle='-', linewidth=3)
        ax.axhline(y=0.5, xmin=t1 / 160, xmax=t2 / 160, color='red', linestyle='-', linewidth=3)
        ax.axhline(y=0.5, xmin=t2 / 160, xmax=1, color='green', linestyle='-', linewidth=3)
    
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Space (mi)")
        ax.set_title("Space vs Time")
        
        ax.grid()
    
        # Close the figure to free up memory after it's done being used
        plt.close(fig)
    
        return fig  # Return the figure object for display in the GUI
