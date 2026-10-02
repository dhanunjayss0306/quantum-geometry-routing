"""Run the full 9-case matrix and generate all submission artifacts.

Outputs:
  experiments/results/<topology>_<condition>.json   per-case raw results
  results/tables/summary.csv                        the 9-case table
  results/figures/fidelity.png                       fidelity comparison chart
  results/figures/routing_cost.png                   SWAPs + depth chart
  results/figures/protection_tradeoff.png            fidelity vs yield (protected)

Run from the repo root:
    python3 scripts/run_all_cases.py
"""

import csv
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from quantum.topologies.tshape import TShapeTopology
from quantum.topologies.heavy_hex import HeavyHexPatch
from quantum.topologies.hyperbolic import HyperbolicTiling
from algorithms.experiment_matrix import run_matrix, CONDITIONS

SHOTS = 2000
SEED = 42
# Headline comparison at matched sizes (~20 qubits); the T-shape is the
# 5-qubit 2016 reference. The full size story lives in scaling_sweep.py.
TOPOLOGIES = [TShapeTopology(), HeavyHexPatch(1, 2), HyperbolicTiling(17)]
COLORS = {"ideal": "#2ca02c", "noisy": "#d62728", "protected": "#1f77b4"}


def save_results(results):
    os.makedirs(f"{REPO_ROOT}/experiments/results", exist_ok=True)
    os.makedirs(f"{REPO_ROOT}/results/tables", exist_ok=True)
    os.makedirs(f"{REPO_ROOT}/results/figures", exist_ok=True)
    for r in results:
        path = f"{REPO_ROOT}/experiments/results/{r['topology']}_{r['condition']}.json"
        with open(path, "w") as f:
            json.dump(r, f, indent=2)
    with open(f"{REPO_ROOT}/results/tables/summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    print(f"saved {len(results)} JSON results + summary.csv")


def chart_fidelity(results):
    fig, ax = plt.subplots(figsize=(10, 5))
    topologies = [t.name for t in TOPOLOGIES]
    x = range(len(topologies))
    width = 0.25
    for i, cond in enumerate(CONDITIONS):
        vals = [next(r["fidelity"] for r in results
                     if r["topology"] == t and r["condition"] == cond)
                for t in topologies]
        bars = ax.bar([p + (i - 1) * width for p in x], vals, width,
                      label=cond, color=COLORS[cond])
        ax.bar_label(bars, fmt="%.3f", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(topologies)
    ax.set_ylabel("Bell-state fidelity")
    ax.set_ylim(0, 1.08)
    ax.set_title("Bell-state fidelity across topologies and conditions")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{REPO_ROOT}/results/figures/fidelity.png", dpi=150)
    plt.close(fig)


def chart_routing_cost(results):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    topologies = [t.name for t in TOPOLOGIES]
    x = range(len(topologies))
    for ax, metric, title in zip(axes,
                                 ["swap_count", "depth_2q"],
                                 ["SWAP gates inserted", "Two-qubit gate depth"]):
        # routing cost is identical across conditions; take 'ideal'
        vals = [next(r[metric] for r in results
                     if r["topology"] == t and r["condition"] == "ideal")
                for t in topologies]
        bars = ax.bar(list(x), vals, color="#9467bd")
        ax.bar_label(bars, fontsize=9)
        ax.set_xticks(list(x))
        ax.set_xticklabels(topologies)
        ax.set_title(title)
    fig.suptitle("Routing cost: Bell state across each chip's diameter")
    fig.tight_layout()
    fig.savefig(f"{REPO_ROOT}/results/figures/routing_cost.png", dpi=150)
    plt.close(fig)


def chart_protection_cost(results):
    """What protection costs (extra SWAPs/depth) vs what it buys (fidelity)."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    topologies = [t.name for t in TOPOLOGIES]
    x = range(len(topologies))
    prot = [next(r for r in results
                 if r["topology"] == t and r["condition"] == "protected")
            for t in topologies]
    noisy = [next(r for r in results
                  if r["topology"] == t and r["condition"] == "noisy")
             for t in topologies]
    ax = axes[0]
    w = 0.35
    ax.bar([p - w / 2 for p in x],
           [r["added_swap_count"] for r in prot], w, label="+ SWAPs")
    ax.bar([p + w / 2 for p in x],
           [r["added_depth_2q"] for r in prot], w, label="+ 2q depth")
    ax.set_xticks(list(x))
    ax.set_xticklabels(topologies)
    ax.set_title("Protection overhead (extra gates)")
    ax.legend()
    ax = axes[1]
    gains = [p["fidelity"] - n["fidelity"] for p, n in zip(prot, noisy)]
    yields = [p["yield"] for p in prot]
    ax.bar([p - w / 2 for p in x], gains, w, label="fidelity gain")
    ax.bar([p + w / 2 for p in x],
           [1 - y for y in yields], w, label="shots discarded")
    ax.set_xticks(list(x))
    ax.set_xticklabels(topologies)
    ax.set_title("Protection payoff: fidelity gained vs shots lost")
    ax.legend()
    fig.suptitle("Syndrome protection: cost (left) vs payoff (right)")
    fig.tight_layout()
    fig.savefig(f"{REPO_ROOT}/results/figures/protection_cost.png", dpi=150)
    plt.close(fig)


def chart_protection_tradeoff(results):
    fig, ax = plt.subplots(figsize=(7, 5))
    for r in results:
        if r["condition"] != "protected":
            continue
        noisy = next(x for x in results if x["topology"] == r["topology"]
                     and x["condition"] == "noisy")
        ax.annotate("", xy=(r["yield"], r["fidelity"]),
                    xytext=(1.0, noisy["fidelity"]),
                    arrowprops=dict(arrowstyle="->", lw=2))
        ax.scatter([r["yield"]], [r["fidelity"]], s=120, label=r["topology"])
        ax.text(r["yield"] - 0.015, r["fidelity"] + 0.008, r["topology"], fontsize=9)
    ax.set_xlabel("Survival yield (fraction of shots kept)")
    ax.set_ylabel("Bell-state fidelity")
    ax.set_title("Protection trade-off: fidelity gained vs shots discarded\n"
                 "(arrow tail = noisy, head = noisy+protected)")
    ax.set_xlim(0.5, 1.03)
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{REPO_ROOT}/results/figures/protection_tradeoff.png", dpi=150)
    plt.close(fig)


def main():
    print("Running the 9-case experiment matrix ...")
    results = run_matrix(TOPOLOGIES, shots=SHOTS, seed=SEED)
    save_results(results)
    chart_fidelity(results)
    chart_routing_cost(results)
    chart_protection_tradeoff(results)
    chart_protection_cost(results)
    print("charts written to results/figures/")
    print("\nSummary:")
    for r in results:
        print(f"  {r['topology']:14s} {r['condition']:9s} "
              f"SWAPs={r['swap_count']:3d} depth2q={r['depth_2q']:2d} "
              f"F={r['fidelity']:.4f} yield={r['yield']:.3f} "
              f"+SWAPs={r['added_swap_count']} +CX={r['added_cx_count']}")


if __name__ == "__main__":
    main()
