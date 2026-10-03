"""Tests on the generated matrix artifacts (summary.csv + result JSONs).

These verify the 9 required cases demanded by the Track 4 spec exist with
the right structure, without re-running the expensive simulations.
"""

import csv
import glob
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO_ROOT, "experiments", "results")
SUMMARY = os.path.join(REPO_ROOT, "results", "tables", "summary.csv")

REQUIRED_TOPOS = {"t-shape", "heavy-hex-127", "hyperbolic-20"}
CONDITIONS = {"ideal", "noisy", "protected"}


def _rows():
    with open(SUMMARY) as f:
        return list(csv.DictReader(f))


def test_nine_required_cases():
    rows = [r for r in _rows() if r["required"] == "True"]
    assert len(rows) == 9, f"expected 9 required cases, got {len(rows)}"
    got = {(r["topology"], r["condition"]) for r in rows}
    expected = {(t, c) for t in REQUIRED_TOPOS for c in CONDITIONS}
    assert got == expected, f"missing: {expected - got}"
    # supplementary row is present but flagged
    supp = [r for r in _rows() if r["required"] == "False"]
    assert len(supp) == 3
    assert {r["topology"] for r in supp} == {"heavy-hex-21"}


def test_ideal_fidelity_is_one_for_required():
    for r in _rows():
        if r["required"] == "True" and r["condition"] == "ideal":
            assert float(r["fidelity"]) == 1.0, r["topology"]


def test_protected_yield_in_unit_interval():
    for r in _rows():
        if r["condition"] == "protected":
            y = float(r["yield"])
            assert 0.0 < y <= 1.0, (r["topology"], y)
            assert float(r["fidelity"]) < 1.0, r["topology"]


def test_result_jsons_match_csv():
    paths = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
    assert len(paths) == 12, f"expected 12 JSON files, got {len(paths)}"
    csv_rows = {(r["topology"], r["condition"]): r for r in _rows()}
    for p in paths:
        with open(p) as f:
            j = json.load(f)
        key = (j["topology"], j["condition"])
        assert key in csv_rows, f"{p} not in summary.csv"
        assert j["fidelity"] == float(csv_rows[key]["fidelity"])
        assert j["required"] == (csv_rows[key]["required"] == "True")
