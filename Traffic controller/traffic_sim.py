import random
import numpy as np
import matplotlib.pyplot as plt

class TrafficLight:
    def __init__(self, green_time=10):
        self.green_time = green_time

class TrafficSimulator:
    def __init__(self, cars_rate_ns, cars_rate_ew, cycles=20):
        self.cars_rate_ns = cars_rate_ns
        self.cars_rate_ew = cars_rate_ew
        self.cycles = cycles

    def run(self, green_ns, green_ew):
        queue_ns = 0
        queue_ew = 0
        total_wait = 0
        total_cars_passed = 0

        for _ in range(self.cycles):
            # car arrivals (Poisson process)
            queue_ns += np.random.poisson(self.cars_rate_ns)
            queue_ew += np.random.poisson(self.cars_rate_ew)

            # NS green phase
            passed = min(queue_ns, green_ns)
            queue_ns -= passed
            total_cars_passed += passed
            total_wait += queue_ns

            # EW green phase
            passed = min(queue_ew, green_ew)
            queue_ew -= passed
            total_cars_passed += passed
            total_wait += queue_ew

        avg_wait = total_wait / self.cycles
        return avg_wait, total_cars_passed

    def optimize(self):
        best_wait = float("inf")
        best_config = (10, 10)

        # Try multiple green time splits
        for ns in range(5, 31, 5):
            for ew in range(5, 31, 5):
                wait, _ = self.run(ns, ew)
                if wait < best_wait:
                    best_wait = wait
                    best_config = (ns, ew)

        return best_config, best_wait
