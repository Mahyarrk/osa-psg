"""
build_model_table.py — build the modeling table for severity prediction.

Loads the full cohort (n=55: 42 thesis-included + 13 excluded patients),
computes true total AHI from event counts and total sleep time, derives
severity bands (AASM: Normal <5, Mild 5-14, Moderate 15-29, Severe >=30),
drops identifier/free-text columns, saves data_model.csv.

Cohort note: the model table now includes the 13 thesis-excluded patients.
The thesis excluded them for good clinical reasons (normals, upper-airway
obstruction, narcolepsy, parasomnia...), but for a *screening* model the
right population is "everyone referred to the sleep lab" — mixed, not
pre-filtered. Their severity distribution (7 normal / 2 mild / 1 moderate
/ 3 severe by ahi_true_total) confirms they land mostly outside severe.

AHI derivation
--------------
The dataset stores stage-specific rates, not a total AHI:
  ahi_rem     = REM respiratory events / REM hours
  ahi_nonrem  = non-REM respiratory events / non-REM hours
These cannot be summed (rates with different denominators). The total is
recovered from the raw event counts instead (AASM definition: total apneas +
hypopneas per hour of sleep):

  ahi_true_total = (obstructive_apnea_rem + central_apnea_rem
                    + mixed_apnea_rem + obstructive_apnea_nonrem
                    + central_apnea_nonrem + mixed_apnea_nonrem
                    + hypopnea_rem + hypopnea_nonrem) / (tst_min / 60)

Cross-check: as a weighted average of the stage AHIs by stage-time shares
(cohort REM share ~11%), this predicts ~53.7 vs the count-derived 54.05 —
the two routes agree. Correlation with ODI (0.578) is in the expected
0.5-0.7 range for a correctly constructed AHI.

Naming caution — two different "total AHI"s exist:
  ahi_true_total  the real AASM total (events / total sleep hours);
                  this defines the severity target.
  ahi_sum_stages  the thesis's apparent convention (ahi_rem + ahi_nonrem,
                  two rates with different denominators added together).
                  Kept ONLY to reproduce the thesis's published
                  correlations in stats_tests.py; the thesis's exact
                  formula is unrecoverable from archived outputs, and this
                  quantity has no clinical meaning. Never use it for
                  severity or any new analysis.

Run:  uv run build_model_table.py
"""

import pandas as pd

from clean import load_clean

MODEL_FILE = "data_model.csv"

# Identifiers and free text — not usable as model features.
NON_FEATURES = [
    "patient_name",
    "referral_reason",
    "comorbidities",
    "final_impression",
    "excluded",
    "exclusion_reason",
    "sex_label",
]


def build_model_table() -> pd.DataFrame:
    inc = load_clean()
    # Full cohort for the screening-model framing: thesis-included (42) +
    # thesis-excluded (13). The excluded are mostly non-severe, which is
    # exactly what a screening population needs.
    inc = inc.copy()

    # Reproduction column: thesis's summed stage rates. No clinical meaning.
    inc["ahi_sum_stages"] = inc["ahi_rem"] + inc["ahi_nonrem"]

    # True total AHI: all respiratory events per hour of sleep (AASM).
    events = (
        inc["obstructive_apnea_rem"] + inc["central_apnea_rem"]
        + inc["mixed_apnea_rem"] + inc["obstructive_apnea_nonrem"]
        + inc["central_apnea_nonrem"] + inc["mixed_apnea_nonrem"]
        + inc["hypopnea_rem"] + inc["hypopnea_nonrem"]
    )
    inc["ahi_true_total"] = events / (inc["tst_min"] / 60)

    # Severity bands from true total AHI; half-open bins put 15 in
    # Moderate and 30 in Severe.
    inc["severity"] = pd.cut(
        inc["ahi_true_total"],
        bins=[-float("inf"), 5, 15, 30, float("inf")],
        labels=["normal", "mild", "moderate", "severe"],
    )

    inc = inc.drop(columns=[c for c in NON_FEATURES if c in inc.columns])
    return inc


def main() -> None:
    inc = build_model_table()
    inc.to_csv(MODEL_FILE, index=False)

    print(f"rows: {len(inc)}")
    print(f"ahi_true_total: mean {inc['ahi_true_total'].mean():.2f}, "
          f"range {inc['ahi_true_total'].min():.1f}-{inc['ahi_true_total'].max():.1f}")
    print(f"ODI correlation (sanity): {inc['odi'].corr(inc['ahi_true_total']):.3f}")
    print("\nseverity distribution:")
    print(inc["severity"].value_counts().sort_index())
    print("\nmissing values per column:")
    print(inc.isna().sum()[inc.isna().sum() > 0])
    print(f"\nwritten: {MODEL_FILE}")


if __name__ == "__main__":
    main()