"""Scaling sweep: diameter / SWAPs / fidelity vs qubit count, per family.

Families: heavy-hex patches (+ the real Eagle-127), hyperbolic {7,3} patches,
and the 2D square grid as the flat reference.

Outputs:
  results/tables/scaling.csv
  results/figures/scaling_diameter.png   (diameter vs qubits, log-x)
  results/figures/scaling_swaps.png      (SWAPs vs qubits, log-x)
  results/figures/scaling_fidelity.png   (noisy fidelity vs qubits)

Run from the repo root:
    python3 scripts/scaling_sweep.py
Takes a few minutes (stabilizer simulation is fast; routing 127 qubits is not).
"""

import csv
import os
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from quantum.topologies.heavy_hex import HeavyHexPatch, Eagle127Topology
from quantum.topologies.hyperbolic import HyperbolicTiling
from quantum.topologies.grid import GridTopology
from algorithms.scaling import run_scaling

SHOTS = 1000
SEED = 42

FAMILIES = {
    "heavy-hex": [HeavyHexPatch(1, 2), HeavyHexPatch(2, 2), HeavyHexPatch(2, 4),
                  HeavyHexPatch(3, 5), Eagle127Topology()],
    "hyperbolic": [HyperbolicTiling(17), HyperbolicTiling(40),
                   HyperbolicTiling(60), HyperbolicTiling(150)],
    "grid": [GridTopology(4, 5), GridTopology(6, 7),
             GridTopology(8, 8), GridTopology(10, 10)],
}
COLORS = {"heavy-hex": "#d62728", "hyperbolic": "#1f77b4", "grid": "#7f7f7f"}


def save_csv(results):
    path = f"{REPO_ROOT}/results/tables/scaling.csv"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    print(f"saved {path} ({len(results)} points)")


def _plot(results, ykey, ylabel, fname, title):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for family, color in COLORS.items():
        pts = sorted((r for r in results if r["family"] == family),
                     key=lambda r: r["num_qubits"])
        xs = [r["num_qubits"] for r in pts]
        ys = [r[ykey] for r in pts]
        ax.plot(xs, ys, "o-", color=color, label=family, ms=7)
        for x, y in zip(xs, ys):
            ax.text(x, y, f" {y}", fontsize=8, color=color)
    ax.set_xscale("log")
    ax.set_xlabel("Qubit count (log scale)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, which="both", ls=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(f"{REPO_ROOT}/results/figures/{fname}", dpi=150)
    plt.close(fig)


def main():
    t0 = time.time()
    print("Running scaling sweep ...")
    results = run_scaling(FAMILIES, shots=SHOTS, seed=SEED)
    save_csv(results)
    _plot(results, "diameter", "Graph diameter (worst-case hops)",
          "scaling_diameter.png",
          "How fast does the worst trip grow? (diameter vs qubits)")
    _plot(results, "swap_count", "SWAPs for farthest-pair Bell state",
          "scaling_swaps.png",
          "Routing cost vs chip size (farthest-pair Bell state)")
    _plot(results, "fidelity_noisy", "Noisy Bell fidelity",
          "scaling_fidelity.png",
          "Noisy fidelity vs chip size (farthest-pair Bell state)")
    print(f"done in {time.time()-t0:.0f}s; figures in results/figures/")
    print("\nSummary:")
    for r in results:
        print(f"  {r['topology']:16s} N={r['num_qubits']:3d} "
              f"diam={r['diameter']:2d} SWAPs={r['swap_count']:2d} "
              f"F_noisy={r['fidelity_noisy']:.3f}")


if __name__ == "__main__":
    main()
