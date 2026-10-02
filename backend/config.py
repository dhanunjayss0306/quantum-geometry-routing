"""Central backend configuration. All tunable values live here."""

import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO_ROOT, "experiments", "results")

ALLOWED_TOPOLOGIES = ["t-shape", "star", "heavy-hex-21", "heavy-hex-35",
                      "hyperbolic-20", "hyperbolic-43"]
# The 3x3 headline matrix uses these three (matched ~20 qubits + 2016 ref).
MATRIX_TOPOLOGIES = ["t-shape", "heavy-hex-21", "hyperbolic-20"]
ALLOWED_CONDITIONS = ["ideal", "noisy", "protected"]

DEFAULT_SHOTS = 2000
MIN_SHOTS = 100
MAX_SHOTS = 20000
DEFAULT_SEED = 42
