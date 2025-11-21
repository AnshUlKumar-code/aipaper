#!/usr/bin/env python3
"""
Parking Usage Heatmap Generator
Reads allocations.csv and slots.json, generates a heatmap image
"""

import csv
import argparse
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import json

# Expect allocations.csv with header:
# timestamp,car_id,car_size,slot_id,slot_size,cost

def load_counts(csvfile):
    """Count how many times each slot is used."""
    c = Counter()
    with open(csvfile, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            slot = row['slot_id']
            c[slot] += 1
    return c

def layout_from_slots(slots_json):
    """
    Create a layout mapping slot_id -> (row, col).
    Assumes slot id like 'A1', 'B3': letters -> rows, digits -> cols
    """
    mapping = {}
    for s in slots_json:
        sid = s['id']
        row = ord(sid[0].upper()) - ord('A')
        try:
            col = int(''.join([c for c in sid[1:] if c.isdigit()])) - 1
        except Exception:
            col = 0
        mapping[sid] = (row, col)
    return mapping

def draw_heatmap(counts, slots_json, out_image='heatmap.png'):
    """Draw and save the heatmap image."""
    mapping = layout_from_slots(slots_json)
    max_row = max(r for r, c in mapping.values())
    max_col = max(c for r, c in mapping.values())
    grid = np.zeros((max_row + 1, max_col + 1), dtype=int)
    for sid, (r, c) in mapping.items():
        grid[r, c] = counts.get(sid, 0)

    plt.figure(figsize=(6, 4))
    plt.imshow(grid, origin='upper')
    plt.title('Parking Usage Heatmap (counts)')
    plt.colorbar(label='Usage count')
    plt.xlabel('Columns')
    plt.ylabel('Rows')
    plt.tight_layout()
    plt.savefig(out_image)
    print('Saved heatmap to', out_image)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--alloc', default='../allocations.csv', help='CSV allocations file')
    parser.add_argument('--slots', default='../sample_data/slots.json', help='Slots JSON file')
    parser.add_argument('--out', default='heatmap.png', help='Output heatmap image')
    args = parser.parse_args()

    counts = load_counts(args.alloc)
    slots_json = json.load(open(args.slots))
    draw_heatmap(counts, slots_json, args.out)
