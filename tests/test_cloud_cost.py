"""Tests for the cloud-cost model (scripts/cloud_cost.py).

Only checks arithmetic over the stored CSVs; pricing assumptions live in
docs/cloud_cost.md, not here.
"""

import csv
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from scripts.cloud_cost import (cost_per_useful_shot, rel_cost_per_shot,
                                rel_cost_with_overhead)


def test_relative_cost_is_upper_bound():
    # Size-matched 127q noisy pair from the stored tables.
    assert rel_cost_per_shot(17, 9) == 17 / 9
    assert rel_cost_per_shot(17, 9) > 1.8
    # Zero overhead recovers the depth ratio exactly.
    assert rel_cost_with_overhead(0, 17, 9) == 17 / 9


def test_overhead_dominance_approaches_one():
    # As fixed overhead dominates, geometry stops moving the bill.
    assert rel_cost_with_overhead(1.0, 17, 9) == 1.0
    assert abs(rel_cost_with_overhead(0.99, 17, 9) - 1.01) < 0.01


def test_relative_cost_decreases_with_overhead():
    vals = [rel_cost_with_overhead(s, 17, 9)
            for s in (0, 0.5, 0.9, 0.99)]
    assert vals == sorted(vals, reverse=True), vals
    assert vals[0] > vals[-1] > 1.0


def test_sensitivity_csv_matches_model():
    path = f"{REPO_ROOT}/results/tables/cloud_cost_sensitivity.csv"
    rows = list(csv.DictReader(open(path)))
    assert [r["overhead_share_s"] for r in rows] == ["0", "0.5", "0.9", "0.99"]
    for r in rows:
        s = float(r["overhead_share_s"])
        expected = round(rel_cost_with_overhead(s, 17, 9), 2)
        assert abs(float(r["relative_cost_heavy_hex_vs_hyperbolic"]) - expected) < 1e-9


def test_protected_cost_counts_discarded_shots():
    # heavy-hex-127 protected: 26 depth, 0.7948 yield.
    got = cost_per_useful_shot(26, 0.7948)
    assert abs(got - 32.71) < 0.01
    # Yield < 1 always inflates cost vs raw depth.
    assert cost_per_useful_shot(26, 0.7948) > 26


def test_cloud_cost_csv_matches_model():
    summary = {(r["topology"], r["condition"]): r for r in
               csv.DictReader(open(f"{REPO_ROOT}/results/tables/summary.csv"))}
    scaling = {r["topology"]: r for r in
               csv.DictReader(open(f"{REPO_ROOT}/results/tables/scaling.csv"))}
    cloud = {(r["topology"], r["condition"]): r for r in
             csv.DictReader(open(f"{REPO_ROOT}/results/tables/cloud_cost.csv"))}
    # Protected matrix rows come from summary.csv ...
    for topo in ["t-shape", "heavy-hex-127", "hyperbolic-20"]:
        s = summary[(topo, "protected")]
        expected = int(s["depth_2q"]) / float(s["yield"])
        got = float(cloud[(topo, "protected")]["cost_per_useful_shot_units"])
        assert abs(got - expected) < 0.01, topo
    # ... and the size-matched noisy pair from scaling.csv (yield 1.0).
    for topo in ["heavy-hex-127", "hyperbolic-127"]:
        depth = int(scaling[topo]["depth_2q"])
        got = float(cloud[(topo, "noisy")]["cost_per_useful_shot_units"])
        assert abs(got - depth) < 0.01, topo
        assert float(cloud[(topo, "noisy")]["yield"]) == 1.0
