"""Tests for the cloud-cost model (scripts/cloud_cost.py).

Only checks arithmetic over the stored CSVs; pricing assumptions live in
docs/cloud_cost.md, not here.
"""

import csv
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from scripts.cloud_cost import cost_per_useful_shot, rel_cost_per_shot


def test_relative_cost_needs_no_gate_time():
    # Size-matched 127q noisy pair from the stored tables.
    assert rel_cost_per_shot(17, 9) == 17 / 9
    assert rel_cost_per_shot(17, 9) > 1.8


def test_protected_cost_counts_discarded_shots():
    # heavy-hex-127 protected: 26 depth, 0.7948 yield.
    got = cost_per_useful_shot(26, 0.7948)
    assert abs(got - 32.71) < 0.01
    # Yield < 1 always inflates cost vs raw depth.
    assert cost_per_useful_shot(26, 0.7948) > 26


def test_cloud_cost_csv_matches_model():
    summary = {(r["topology"], r["condition"]): r for r in
               csv.DictReader(open(f"{REPO_ROOT}/results/tables/summary.csv"))}
    cloud = {r["topology"]: r for r in
             csv.DictReader(open(f"{REPO_ROOT}/results/tables/cloud_cost.csv"))}
    for topo in ["t-shape", "heavy-hex-127", "hyperbolic-20"]:
        s = summary[(topo, "protected")]
        expected = int(s["depth_2q"]) / float(s["yield"])
        assert abs(float(cloud[topo]["cost_per_useful_shot_units"]) - expected) < 0.01
