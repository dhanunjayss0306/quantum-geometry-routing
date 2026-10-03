"""Cloud-cost model: what the measured routing costs imply for QPU bills.

Reads results/tables/summary.csv (9-case matrix) and
results/tables/scaling.csv (size-matched hyperbolic-127 row), then
estimates relative QPU cost from two-qubit depth.

Model (documented in docs/cloud_cost.md):
  - On time-billed QPUs (IBM Quantum Pay-As-You-Go, $1.60/s, priced
    2026-10-03), execution time per shot scales with two-qubit depth.
  - Relative cost per shot = depth_A / depth_B (same device, same shots).
    This needs no assumed gate time.
  - Protected runs discard shots, and discarded shots still bill, so cost
    per *useful* shot multiplies by 1 / yield.
  - On per-shot billing (AWS Braket $0.30/task + per-shot), depth does not
    change the bill; only shot count matters. The model covers time billing.

Writes results/tables/cloud_cost.csv and prints the headline comparison.

Run from the repo root:
    python3 scripts/cloud_cost.py
"""

import csv
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

IBM_USD_PER_SEC = 1.60  # IBM Quantum Pay-As-You-Go, 2026-10-03
SEC_PER_2Q_LAYER = 0.5e-6  # illustrative assumption, see docs/cloud_cost.md


def load_summary():
    with open(f"{REPO_ROOT}/results/tables/summary.csv") as f:
        return {(r["topology"], r["condition"]): r
                for r in csv.DictReader(f)}


def load_scaling():
    with open(f"{REPO_ROOT}/results/tables/scaling.csv") as f:
        return {r["topology"]: r for r in csv.DictReader(f)}


def rel_cost_per_shot(depth_a, depth_b):
    """Relative QPU-time cost per shot: needs no gate-time assumption."""
    return depth_a / depth_b


def cost_per_useful_shot(depth, yld):
    """Depth x 1/yield: discarded shots still bill on time-billed QPUs."""
    return depth / yld


def main():
    summary = load_summary()
    scaling = load_scaling()

    # Headline: size-matched 127-qubit pair, noisy condition.
    hh = summary[("heavy-hex-127", "noisy")]
    hy = scaling["hyperbolic-127"]
    d_hh, d_hy = int(hh["depth_2q"]), int(hy["depth_2q"])
    ratio = rel_cost_per_shot(d_hh, d_hy)

    # Protected cost per useful shot (matrix rows; sizes differ, see docs).
    rows = []
    for topo in ["t-shape", "heavy-hex-127", "hyperbolic-20"]:
        r = summary[(topo, "protected")]
        depth, yld = int(r["depth_2q"]), float(r["yield"])
        rows.append({
            "topology": topo,
            "condition": "protected",
            "depth_2q": depth,
            "yield": yld,
            "cost_per_useful_shot_units": round(cost_per_useful_shot(depth, yld), 2),
        })

    # Illustrative dollars for 1M shots (assumes 0.5 us per 2q layer).
    shots = 1_000_000
    usd_hh = d_hh * SEC_PER_2Q_LAYER * shots * IBM_USD_PER_SEC
    usd_hy = d_hy * SEC_PER_2Q_LAYER * shots * IBM_USD_PER_SEC

    out_path = f"{REPO_ROOT}/results/tables/cloud_cost.csv"
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("Cloud-cost model (see docs/cloud_cost.md for assumptions)")
    print(f"  Size-matched 127q, noisy: heavy-hex-127 depth {d_hh} vs "
          f"hyperbolic-127 depth {d_hy}")
    print(f"  Relative QPU-time cost per shot: {ratio:.2f}x "
          f"(Eagle-style costs ~{ratio:.1f}x the hyperbolic layout)")
    print(f"  Illustrative IBM billing, 1M shots: "
          f"${usd_hh:.2f} vs ${usd_hy:.2f} "
          f"(saves ~{(1 - usd_hy / usd_hh) * 100:.0f}%)")
    print(f"  Protected cost per useful shot (depth/yield):")
    for r in rows:
        print(f"    {r['topology']:14s} {r['cost_per_useful_shot_units']}")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
