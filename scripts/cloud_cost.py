"""Cloud-cost model: what the measured routing costs imply for QPU bills.

Reads results/tables/summary.csv (9-case matrix) and
results/tables/scaling.csv (size-matched hyperbolic-127 row), then
estimates relative QPU cost from two-qubit depth.

Model (documented in docs/cloud_cost.md):
  - On time-billed QPUs, execution time per shot = fixed overhead
    (readout, reset, repetition delay) + depth-proportional gate time.
  - The depth ratio depth_A / depth_B is an UPPER BOUND on relative cost:
    it holds exactly only if per-shot time were purely depth-proportional.
    Our own ibm_fez job billed 4 s of QPU usage for 6000 shots
    (~0.67 ms/shot), so fixed overhead dominates and the true ratio is
    much closer to 1.0. See the sensitivity table below.
  - Protected runs discard shots, and discarded shots still bill, so cost
    per *useful* shot multiplies by 1 / yield.
  - On per-shot billing (AWS Braket), depth does not change the bill;
    only shot count matters. The model covers time billing only.

Writes results/tables/cloud_cost.csv and
results/tables/cloud_cost_sensitivity.csv, and prints the comparison.

Run from the repo root:
    python3 scripts/cloud_cost.py
"""

import csv
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)


def load_summary():
    with open(f"{REPO_ROOT}/results/tables/summary.csv") as f:
        return {(r["topology"], r["condition"]): r
                for r in csv.DictReader(f)}


def load_scaling():
    with open(f"{REPO_ROOT}/results/tables/scaling.csv") as f:
        return {r["topology"]: r for r in csv.DictReader(f)}


def rel_cost_per_shot(depth_a, depth_b):
    """Depth ratio: UPPER BOUND on relative QPU-time cost per shot.

    Exact only if per-shot time were purely depth-proportional
    (zero fixed overhead)."""
    return depth_a / depth_b


def rel_cost_with_overhead(s, depth_a, depth_b):
    """Relative cost when a share s of per-shot time is fixed overhead.

    s=0 -> the depth ratio (upper bound); s->1 -> 1.0 (overhead dominates
    and geometry barely moves the bill)."""
    return s + (depth_a / depth_b) * (1 - s)


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

    # Sensitivity table: fixed-overhead share s of the per-shot time.
    s_values = [0, 0.5, 0.9, 0.99]
    sens_rows = [
        {"overhead_share_s": s,
         "relative_cost_heavy_hex_vs_hyperbolic":
             round(rel_cost_with_overhead(s, d_hh, d_hy), 2)}
        for s in s_values
    ]
    sens_path = f"{REPO_ROOT}/results/tables/cloud_cost_sensitivity.csv"
    with open(sens_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sens_rows[0].keys()))
        w.writeheader()
        w.writerows(sens_rows)

    # Cost per useful shot. First the protected matrix rows (note: these
    # rows have different qubit counts, 5 / 127 / 20), then a size-matched
    # noisy pair from scaling.csv (yield 1.0: no post-selection).
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
    for topo in ["heavy-hex-127", "hyperbolic-127"]:
        depth = int(scaling[topo]["depth_2q"])
        rows.append({
            "topology": topo,
            "condition": "noisy",
            "depth_2q": depth,
            "yield": 1.0,
            "cost_per_useful_shot_units": round(cost_per_useful_shot(depth, 1.0), 2),
        })

    out_path = f"{REPO_ROOT}/results/tables/cloud_cost.csv"
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("Cloud-cost model (see docs/cloud_cost.md for assumptions)")
    print(f"  Size-matched 127q, noisy: heavy-hex-127 depth {d_hh} vs "
          f"hyperbolic-127 depth {d_hy}")
    print(f"  Relative QPU-time cost per shot: {ratio:.2f}x UPPER BOUND "
          f"(exact only with zero fixed overhead)")
    print(f"  Sensitivity to fixed overhead share s:")
    for r in sens_rows:
        print(f"    s={r['overhead_share_s']:<4} -> "
              f"{r['relative_cost_heavy_hex_vs_hyperbolic']:.2f}x")
    print(f"  Cost per useful shot (depth/yield):")
    for r in rows:
        print(f"    {r['topology']:14s} {r['condition']:9s} "
              f"{r['cost_per_useful_shot_units']}")
    print(f"\nwrote {out_path}\nwrote {sens_path}")


if __name__ == "__main__":
    main()
