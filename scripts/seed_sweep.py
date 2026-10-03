"""Seed robustness sweep: repeat the 9 required cases across seeds.

Runs {t-shape, heavy-hex-127, hyperbolic-20} x {ideal, noisy, protected}
for seeds [1, 2, 3, 4, 5] plus the headline seed 42, then writes
results/tables/seed_sweep.csv with mean and standard deviation of
fidelity and yield per (topology, condition). SWAP counts are
deterministic (same seed-independent routing); they are reported once.

Run from the repo root:
    python3 scripts/seed_sweep.py
"""

import csv
import os
import statistics
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from quantum.topologies.tshape import TShapeTopology
from quantum.topologies.heavy_hex import Eagle127Topology
from quantum.topologies.hyperbolic import HyperbolicTiling
from algorithms.experiment_matrix import run_case, CONDITIONS

SHOTS = 2000
SEEDS = [1, 2, 3, 4, 5, 42]
TOPOLOGIES = [TShapeTopology(), Eagle127Topology(), HyperbolicTiling(20)]


def main():
    rows = []
    for topo in TOPOLOGIES:
        for cond in CONDITIONS:
            fids, yields = [], []
            swaps = None
            for seed in SEEDS:
                print(f"  {topo.name:14s} {cond:9s} seed={seed} ...",
                      flush=True)
                r = run_case(topo, cond, shots=SHOTS, seed=seed)
                fids.append(r["fidelity"])
                yields.append(r["yield"])
                swaps = r["swap_count"]  # deterministic; same every seed
            rows.append({
                "topology": topo.name,
                "condition": cond,
                "seeds": len(SEEDS),
                "shots": SHOTS,
                "swap_count": swaps,
                "fidelity_mean": round(statistics.mean(fids), 4),
                "fidelity_std": round(statistics.pstdev(fids), 4),
                "yield_mean": round(statistics.mean(yields), 4),
                "yield_std": round(statistics.pstdev(yields), 4),
            })
    path = f"{REPO_ROOT}/results/tables/seed_sweep.csv"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {path}")
    print("\nFidelity mean +/- std:")
    for r in rows:
        print(f"  {r['topology']:14s} {r['condition']:9s} "
              f"{r['fidelity_mean']:.4f} +/- {r['fidelity_std']:.4f} "
              f"(yield {r['yield_mean']:.3f} +/- {r['yield_std']:.3f})")


if __name__ == "__main__":
    main()
