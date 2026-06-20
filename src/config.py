"""
Triagegeist — central configuration module.

Holds the single source of truth for seeds, paths (Kaggle vs local),
modelling constants, target/leakage definitions, and the reproducibility
package manifest. Importing this module has no side effects beyond defining
constants; call ``seed_everything()`` explicitly to lock randomness.
"""

import os
import random

import numpy as np

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
SEED = 42


def seed_everything(seed: int = SEED) -> int:
    """Lock all relevant sources of randomness to ``seed``.

    Pins ``PYTHONHASHSEED``, the stdlib ``random`` module, and NumPy's global
    RNG. Returns the seed so callers can use it inline.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    return seed


# ---------------------------------------------------------------------------
# Environment detection (Kaggle vs local)
# ---------------------------------------------------------------------------
# On Kaggle the competition data is mounted read-only under /kaggle/input and
# writable scratch lives at /kaggle/working. Locally we use the repo's data/
# and outputs/ folders. No path that only exists on one platform is hardcoded
# into the consuming code — everything flows through these constants.
ON_KAGGLE = os.path.isdir("/kaggle/input")

if ON_KAGGLE:
    DATA_DIR = "/kaggle/input/triagegeist"
    OUT_DIR = "/kaggle/working"
    DATA_NHAMCS = "/kaggle/input/nhamcs-2022"
else:
    DATA_DIR = "./data/raw"
    OUT_DIR = "./outputs"
    DATA_NHAMCS = "./data/nhamcs"
    # MIMIC-IV-ED: credentialed PhysioNet data — local-only, never commit raw files.
    # Section 10b skips if absent; aggregate outputs only when run locally.
    DATA_MIMIC = "./data/mimic"

# ---------------------------------------------------------------------------
# Modelling constants
# ---------------------------------------------------------------------------
HOLDOUT_FRAC = 0.20
CV_FOLDS = 5
LONG_STAY_THRESHOLD_H = 4.0

# ---------------------------------------------------------------------------
# Synthetic-data target columns (as found in train.csv)
# ---------------------------------------------------------------------------
TARGET_ACUITY = "triage_acuity"
TARGET_DISPOSITION = "disposition"
TARGET_LOS = "ed_los_hours"

# ---------------------------------------------------------------------------
# Derived binary targets (engineered downstream, never present as raw columns)
# ---------------------------------------------------------------------------
# is_admitted    -> disposition in {admitted, transferred}
# is_long_stay   -> ed_los_hours >= LONG_STAY_THRESHOLD_H (4.0)
# is_lwbs        -> left without being seen
# is_lama        -> left against medical advice
TARGET_ADMIT = "is_admitted"
TARGET_LONG_STAY = "is_long_stay"
TARGET_LWBS = "is_lwbs"
TARGET_LAMA = "is_lama"

# ---------------------------------------------------------------------------
# Leakage guard — these columns encode the outcome and must NEVER be used as
# model features. Includes both the raw targets and every derived target.
# ---------------------------------------------------------------------------
LEAKAGE_COLS = [
    TARGET_ACUITY,
    TARGET_DISPOSITION,
    TARGET_LOS,
    TARGET_ADMIT,
    TARGET_LONG_STAY,
    TARGET_LWBS,
    TARGET_LAMA,
]

# ---------------------------------------------------------------------------
# Informative-missingness trap columns. Missingness in these is NOT random:
# it correlates with acuity (e.g. a stable low-acuity patient may not get a
# full vitals workup). Must be handled explicitly (e.g. missing-indicator
# features) rather than naively imputed, or the model learns the gap instead
# of the physiology.
# ---------------------------------------------------------------------------
MISSINGNESS_TRAP_COLS = ["systolic_bp", "respiratory_rate", "pain_score"]

# ---------------------------------------------------------------------------
# NHAMCS 2022 (Step 9, real-data replication) caveats
# ---------------------------------------------------------------------------
# When the real NHAMCS data is brought in for replication in Step 9, the
# outcome columns require careful reconstruction:
#
#   * ADMISSION must be reconstructed from the disposition flag set
#       ADMITHOS / OBSHOS / TRANNH / TRANPSYC / TRANOTH / LWBS /
#       LEFTAMA / DIEDED
#     and NOT read from ADMTPHYS alone, which is mostly NaN due to NHAMCS
#     skip-pattern questionnaire logic.
#   * LENGTH OF STAY must use `ed_los_min` (ED minutes), NOT the `LOS`
#     column (which refers to hospital length of stay, a different concept).
#   * The SURVEY WEIGHT for producing nationally representative estimates is
#     `PATWT`; analyses must apply it when generalising beyond the sample.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Reproducibility manifest: package -> minimum version. Printed in the
# notebook's Section 0 header so reviewers can confirm the environment.
# ---------------------------------------------------------------------------
REQUIRED_PACKAGES = {
    "pandas": "2.0",
    "numpy": "1.24",
    "scikit-learn": "1.3",
    "lightgbm": "4.0",
    "shap": "0.42",
    "matplotlib": "3.7",
    "seaborn": "0.12",
}
