from traffic_sim import TrafficSimulator
import matplotlib.pyplot as plt

cars_ns = int(input("Enter NS car rate: "))
cars_ew = int(input("Enter EW car rate: "))

sim = TrafficSimulator(cars_ns, cars_ew)

print("Running baseline (10,10)...")
baseline_wait, _ = sim.run(10, 10)

print("Optimizing...")
(best_ns, best_ew), optimized_wait = sim.optimize()

print("Best Green Times → NS:", best_ns, "EW:", best_ew)
print("Baseline Avg Wait:", baseline_wait)
print("Optimized Avg Wait:", optimized_wait)

# Graph
plt.bar(["Baseline", "Optimized"], [baseline_wait, optimized_wait])
plt.ylabel("Average Waiting Time")
plt.title("Traffic Optimization Result")
plt.show()
