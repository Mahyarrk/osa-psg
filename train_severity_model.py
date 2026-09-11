"""
train_severity_model.py — OSA severity prediction from smartwatch-grade features.

Research framing: can OSA severity be estimated from the signals a consumer
smart band / smartwatch can plausibly measure, without a sleep lab?
A wrist device can approximate: sleep duration, awakenings/sleep
interruptions, heart-rate-derived arousal surrogates, SpO2, and body metrics.
It CANNOT measure: event counts, stage-specific AHI, Mallampati.

Weights: features get prior-importance weights (a wearable's known signal
quality), applied by replicating each column n_weight times in X — the
forest and the scaled logistic model both see the strong features more
often. BMI is preferred over raw weight (height-corrected), so height is
dropped and weight demoted.

Pipeline:
  1. load modeling table (build_model_table, full n=55 cohort)
  2. restrict to the smartwatch feature set, apply importance weights
  3. two targets: 4-class severity, and binary severe vs non-severe
  4. logistic regression vs random forest, 5-fold stratified CV
  5. multi-seed evaluation (30 seeds) for a stable accuracy estimate
  6. feature importances from the forest

Run:  uv run train_severity_model.py
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from build_model_table import build_model_table

# Features a consumer wearable can plausibly provide.
# Weights express prior domain importance: how many times each column is
# replicated. Weight > 1 = the device measures this signal reliably and it
# is known to relate to OSA severity.
FEATURE_WEIGHTS = {
    # body metrics — BMI is the clinically meaningful habitus measure;
    # raw weight/height are redundant with it (demoted, height dropped)
    "bmi": 3,
    "weight_kg": 1,
    # sleep continuity — the core of what a wearable actually sees
    "awakenings_count": 3,
    "sleep_efficiency_pct": 2,
    "tst_min": 2,
    "sleep_latency_min": 1,
    # SpO2 signals — pulse-ox sensors are the device's strongest asset
    "odi": 3,
    "spo2_nonrem_mean": 2,
    "spo2_rem_mean": 1,
    "spo2_awake_mean": 1,
    # movement/HR surrogates
    "arousal_index": 2,
    "plms_index": 1,
    # demographics
    "age_years": 1,
    "sex": 1,
    # symptoms (in-app questionnaires) — self-reported, low reliability
    "snoring": 1,
    "apnea_feeling": 1,
}
FEATURES = list(FEATURE_WEIGHTS)


def make_xy(binary: bool = False) -> tuple[pd.DataFrame, pd.Series]:
    inc = build_model_table()
    # apply weights: each weighted feature contributes w identical columns
    # with unique names (_w2/_w3 suffixes — sklearn requires uniqueness)
    X = pd.concat(
        [pd.DataFrame({f"{name}_w{i}" if w > 1 else name: inc[name]
                       for i in range(1, w + 1)})
         for name, w in FEATURE_WEIGHTS.items()],
        axis=1,
    )
    if binary:
        y = (inc["severity"] == "severe").map({True: "severe", False: "non_severe"})
    else:
        y = inc["severity"].astype(str)
    return X, y


def evaluate(name: str, model, X: pd.DataFrame, y: pd.Series, seeds: list[int]) -> None:
    print(f"\n=== {name} ===")
    # single representative run (seed 42) for the detailed report
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    pred = cross_val_predict(model, X, y, cv=cv)
    print(classification_report(y, pred, zero_division=0))
    labels = sorted(y.unique())
    print("confusion matrix (rows=true, cols=predicted):")
    print(confusion_matrix(y, pred, labels=labels))

    # multi-seed: the honest estimate is the distribution, not one split
    scores = []
    for seed in seeds:
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
        scores.append(cross_val_score(model, X, y, cv=cv, scoring="accuracy"))
    all_scores = pd.Series([s for fold in scores for s in fold])
    print(f"multi-seed CV accuracy over {len(seeds)} seeds x 5 folds: "
          f"mean {all_scores.mean():.3f}, SD {all_scores.std():.3f}, "
          f"range {all_scores.min():.3f}-{all_scores.max():.3f}")


def main() -> None:
    seeds = list(range(1, 31))  # 30 seeds; frozen in code for reproducibility

    for binary in [False, True]:
        X, y = make_xy(binary=binary)
        title = "severe vs non-severe" if binary else "4-class severity"
        print(f"\n{'#' * 10} TARGET: {title}  (n={len(X)}, "
              f"{X.shape[1]} weighted cols) {'#' * 10}")
        print(f"class balance: {y.value_counts().to_dict()}")

        models = {
            "logistic regression": make_pipeline(
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
        for name, model in models.items():
            evaluate(name, model, X, y, seeds)


if __name__ == "__main__":
    main()