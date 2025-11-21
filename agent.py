#!/usr/bin/env python3
"""
Smart Parking Allocation Agent

Files:
- agent.py        # core agent
- data_sim.py     # optional simulator to produce sample inputs
- requirements.txt

Run:
$ python agent.py --input sample_data/vehicles.json --slots sample_data/slots.json --out allocations.csv
"""

import argparse
import json
import csv
import time
from math import inf

# Fallback pure-Python implementation of Hungarian (for small matrices)
# For production, use scipy.optimize.linear_sum_assignment if available.
try:
    from scipy.optimize import linear_sum_assignment
    SCIPY_AVAILABLE = True
except Exception:
    SCIPY_AVAILABLE = False

def build_cost_matrix(cars, slots, weights=None):
    """Build cost matrix: rows=cars, cols=slots.
    weights: dict controlling cost components, e.g. {'distance':1.0, 'size_penalty':1000, 'priority':-50}
    """
    if weights is None:
        weights = {'distance': 1.0, 'size_penalty': 1000.0, 'priority': -10.0}

    matrix = []
    for car in cars:
        row = []
        for slot in slots:
            dist = slot.get('distance', 0)
            cost = weights['distance'] * dist

            # Size compatibility penalty
            if car.get('size') != slot.get('size'):
                cost += weights['size_penalty']

            # Priority adjustment
            priority = slot.get('priority', 0)
            cost += weights['priority'] * priority

            row.append(cost)
        matrix.append(row)
    return matrix

def assign_hungarian(cost_matrix):
    """Return list of (row_idx, col_idx) assignments and total cost.
    Uses scipy if available, otherwise fallback greedy.
    """
    n_rows = len(cost_matrix)
    n_cols = len(cost_matrix[0]) if n_rows else 0

    if SCIPY_AVAILABLE:
        import numpy as np
        arr = np.array(cost_matrix)
        row_ind, col_ind = linear_sum_assignment(arr)
        total = arr[row_ind, col_ind].sum()
        return list(zip(list(map(int, row_ind)), list(map(int, col_ind)))), float(total)

    # Fallback greedy assignment (not globally optimal)
    assignments = []
    used_cols = set()
    total = 0.0
    for r, row in enumerate(cost_matrix):
        best_c = None
        best_cost = float('inf')
        for c, val in enumerate(row):
            if c in used_cols:
                continue
            if val < best_cost:
                best_cost = val
                best_c = c
        if best_c is not None:
            assignments.append((r, best_c))
            used_cols.add(best_c)
            total += best_cost
    return assignments, total

def save_allocations(assignments, cars, slots, out_csv, timestamp=None):
    ts = timestamp or int(time.time())
    header = ['timestamp', 'car_id', 'car_size', 'slot_id', 'slot_size', 'cost']

    write_header = False
    try:
        with open(out_csv, 'r') as _:
            write_header = False
    except FileNotFoundError:
        write_header = True

    with open(out_csv, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        for (r, c), cost in assignments:
            car = cars[r]
            slot = slots[c]
            writer.writerow([ts, car.get('id'), car.get('size'), slot.get('id'), slot.get('size'), cost])

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='vehicles JSON file')
    parser.add_argument('--slots', required=True, help='slots JSON file')
    parser.add_argument('--out', default='allocations.csv')
    parser.add_argument('--weights', help='optional JSON with weights')
    args = parser.parse_args()

    cars = load_json(args.input)
    slots = load_json(args.slots)

    weights = None
    if args.weights:
        weights = load_json(args.weights)

    cost_matrix = build_cost_matrix(cars, slots, weights)
    assignment_pairs, total = assign_hungarian(cost_matrix)

    # Enrich assignments with cost
    assignments_with_cost = [((r, c), cost_matrix[r][c]) for r, c in assignment_pairs]

    save_allocations(assignments_with_cost, cars, slots, args.out)

    # Print friendly output
    out = [{'car': cars[r]['id'], 'slot': slots[c]['id'], 'cost': cost} for (r, c), cost in assignments_with_cost]
    print(json.dumps({'assignments': out, 'total_cost': total}, indent=2))

if __name__ == '__main__':
    main()
