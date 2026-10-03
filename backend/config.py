"""Central backend configuration. All tunable values live here."""

import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO_ROOT, "experiments", "results")

ALLOWED_TOPOLOGIES = ["t-shape", "star", "heavy-hex-21", "heavy-hex-35",
                      "heavy-hex-127", "hyperbolic-20", "hyperbolic-43"]
# The 3x3 headline matrix uses these three (2016 ref + real Eagle map +
# proposed hyperbolic patch). heavy-hex-21 is a supplementary size-matched row.
MATRIX_TOPOLOGIES = ["t-shape", "heavy-hex-127", "hyperbolic-20"]
ALLOWED_CONDITIONS = ["ideal", "noisy", "protected"]

DEFAULT_SHOTS = 2000
MIN_SHOTS = 100
MAX_SHOTS = 20000
DEFAULT_SEED = 42
