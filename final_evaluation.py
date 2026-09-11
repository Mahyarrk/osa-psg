"""
final_evaluation.py — final head-to-head results for the report.

Two feature sets, both on the full cohort (n=55), both targets (4-class
severity and binary severe vs non-severe), both models (logistic, forest),
5-fold stratified CV, 30 seeds — mean/SD/range per configuration.

  Set A "smartband": only wearable-plausible features (unweighted —
                     the step-3 configuration, which beat weighting).
  Set B "full PSG":  the original feature set (everything except AHI
                     columns — leakage — and Mallampati).

Run:  uv run final_evaluation.py
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from build_model_table import build_model_table

SMARTBAND_FEATURES = [
    "age_years", "sex", "height_cm", "weight_kg", "bmi",
    "tst_min", "sleep_latency_min", "awakenings_count", "sleep_efficiency_pct",
    "spo2_awake_mean", "spo2_rem_mean", "spo2_nonrem_mean", "odi",
    "arousal_index", "plms_index",
    "snoring", "apnea_feeling", "night_sweats", "morning_headache",
    "poor_concentration", "sleep_talking", "night_terrors",
]
# leakage columns excluded from set B
LEAKY = ["ahi_rem", "ahi_nonrem", "ahi_true_total", "ahi_sum_stages",
         "severity", "mallampati_score"]


def make_xy(feature_set: str, binary: bool) -> tuple[pd.DataFrame, pd.Series]:
    inc = build_model_table()
    if feature_set == "smartband":
        X = inc[SMARTBAND_FEATURES].copy()
    else:
        X = inc.drop(columns=[c for c in LEAKY if c in inc.columns])
    if binary:
        y = (inc["severity"] == "severe").map({True: "severe", False: "non_severe"})
    else:
        y = inc["severity"].astype(str)
    return X, y


def models() -> dict:
    return {
        "logistic": make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(max_iter=5000, class_weight="balanced"),
        ),
        "random forest": make_pipeline(
            SimpleImputer(strategy="median"),
            RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                   random_state=42),
        ),
    }


def multiseed(model, X, y, seeds) -> pd.Series:
    scores = []
    for seed in seeds:
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
        scores.extend(cross_val_score(model, X, y, cv=cv, scoring="accuracy"))
    return pd.Series(scores)


def main() -> None:
    seeds = list(range(1, 31))
    rows = []
    for feature_set in ["smartband", "full PSG"]:
        for binary, target in [(True, "severe vs non-severe"),
                               (False, "4-class severity")]:
            X, y = make_xy(feature_set, binary)
            for name, model in models().items():
                s = multiseed(model, X, y, seeds)
                rows.append({
                    "features": feature_set, "target": target, "model": name,
                    "mean": round(s.mean(), 3), "sd": round(s.std(), 3),
                    "min": round(s.min(), 3), "max": round(s.max(), 3),
                })
                print(f"{feature_set:10s} | {target:20s} | {name:16s} "
                      f"acc {s.mean():.3f} ± {s.std():.3f} "
                      f"[{s.min():.3f}..{s.max():.3f}]")
    print("\nbaselines: 4-class majority 0.582 | binary majority 0.582")
    results = pd.DataFrame(rows)
    results.to_csv("final_results.csv", index=False)
    print("\nwritten: final_results.csv")


if __name__ == "__main__":
    main()