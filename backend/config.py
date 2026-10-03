"""Central backend configuration. All tunable values live here."""

import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO_ROOT, "experiments", "results")

# Topology tiers: the required 9-case matrix, size-matched supplementary
# rows, and exploratory topologies usable in the Run tab only.
REQUIRED_TOPOLOGIES = ["t-shape", "heavy-hex-127", "hyperbolic-20"]
SUPPLEMENTARY_TOPOLOGIES = ["heavy-hex-21", "hyperbolic-127"]
EXPLORATORY_TOPOLOGIES = ["star", "heavy-hex-35", "hyperbolic-43"]
ALLOWED_TOPOLOGIES = (REQUIRED_TOPOLOGIES + SUPPLEMENTARY_TOPOLOGIES
                      + EXPLORATORY_TOPOLOGIES)
# The 3x3 headline matrix uses these three (2016 ref + Eagle-style map +
# proposed hyperbolic patch). heavy-hex-21 and hyperbolic-127 are
# supplementary size-matched rows.
MATRIX_TOPOLOGIES = REQUIRED_TOPOLOGIES
ALLOWED_CONDITIONS = ["ideal", "noisy", "protected"]

DEFAULT_SHOTS = 2000
MIN_SHOTS = 100
MAX_SHOTS = 20000
DEFAULT_SEED = 42
