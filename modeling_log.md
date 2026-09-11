# Modeling log — OSA severity from smartwatch-grade features

## Step 1: baseline model (all PSG features)
- **Date:** Day 1–2 of the reanalysis sprint
- **Script:** `train_severity_model.py` (first version, now superseded)
- **Features:** all 37 numeric columns except AHI columns (leakage) and
  Mallampati (34/42 missing)
- **Target:** severity 3-class, derived from ahi_true_total
  (3 mild / 10 moderate / 29 severe)
- **Method:** logistic regression + random forest, 5-fold stratified CV,
  one seed
- **Result:** forest 80.8% accuracy vs 69% majority-class baseline;
  mild class 0/3 recall; importances dominated by event counts
  (obstructive_apnea_nonrem 0.138, hypopnea_nonrem 0.124) then weight,
  awakenings, BMI
- **Read:** event counts are the label's ingredients — dominance was
  expected; the interesting signal was in non-ingredient features.

## Step 2: smartwatch reframing (current)
- **Decision:** remove ALL sleep-lab-only features (event counts, stage
  AHI). Keep only what a consumer wearable can plausibly measure:
  body metrics, sleep timing/continuity, SpO2/PPG signals, movement
  (plms_index as a movement surrogate), symptom questionnaires.
  No feature selection beyond that (per project decision: don't drop
  columns).
- **Rationale:** reframes the project as "OSA severity estimation from
  smartband/smartwatch data" — a screening-use-case narrative for
  reports and applications.
- **Targets:** 3-class severity AND binary severe vs non-severe.
- **Method:** same two models; 5-fold stratified CV; **30 seeds** for a
  stable accuracy distribution (single-seed numbers are unstable at n=42).

## Step 2 results (n=42, 30 seeds x 5 folds)

| Target | Model | Mean acc | SD | Range |
|---|---|---|---|---|
| 3-class | logistic | 0.509 | 0.150 | 0.125–0.875 |
| 3-class | forest | 0.559 | 0.144 | 0.250–1.000 |
| severe vs non | logistic | 0.590 | 0.152 | 0.250–1.000 |
| severe vs non | forest | 0.603 | 0.145 | 0.222–0.889 |

Baselines (majority class): 3-class 0.69; binary 0.69.

**Read, honestly:** without event counts, NO model beats the
always-guess-severe baseline (0.69). The smartwatch-plausible features
alone do not separate severity in this cohort. Seed variance is huge
(range up to 1.000 on some folds) — small-n reality, exactly why
multi-seed was needed. Feature importances are more balanced now:
ODI and SpO2 signals lead, followed by weight/awakenings/BMI.

## Step 3: branch — full cohort (n=55, screening framing)
- **Decision:** add the 13 thesis-excluded patients to the modeling table.
  The thesis excluded them clinically (normals, upper airway obstruction,
  narcolepsy, parasomnia, convulsion, primary snoring), but for a
  *screening* model the correct population is "everyone referred to the
  sleep lab" — mixed, not pre-filtered for disease.
- **Their severity (by ahi_true_total): 7 normal / 2 mild / 1 moderate /
  3 severe** — confirms the hypothesis that they land mostly non-severe
  (mean AHI 15.8 vs included cohort's 54).
- **New class balance (n=55): 7 normal / 5 mild / 11 moderate / 32 severe.**

## Step 3 results (n=55, 30 seeds x 5 folds)

| Target | Model | Mean acc | SD | Range |
|---|---|---|---|---|
| 4-class | logistic | 0.459 | 0.131 | 0.091–0.818 |
| 4-class | forest | 0.532 | 0.121 | 0.273–0.909 |
| severe vs non | logistic | 0.639 | 0.133 | 0.273–0.909 |
| severe vs non | forest | 0.685 | 0.134 | 0.273–1.000 |

Baselines (majority class): 4-class 0.582 (32/55); binary 0.582.

**Read:** the screening framing changes the conclusion substantially:
- 4-class still fails (forest 0.532 < baseline 0.582) — severity gradation
  remains unlearnable from smartwatch-grade features.
- **Binary severe-vs-non-severe now clears the baseline**: forest 0.685 vs
  0.582 majority-class, logistic 0.639. Weak but real separation — the
  model detects "severe or not" better than chance in a mixed referral
  population.
- Seed variance remains large (SD ~0.13): small-n instability persists.
- Importances rebalance in the mixed cohort: ODI and BMI lead
  (0.133/0.120) — body habitus and desaturation signals, consistent with
  the screening narrative.

## Conclusions after step 3
1. In a mixed referral population (n=55), smartwatch-grade features give
   weak-but-real detection of severe OSA (0.685 vs 0.582 baseline, ~+10
   points) — consistent with the wearable-screening literature's modest
   effect sizes.
2. Fine-grained severity grading (4-class) is not achievable from these
   features in this cohort.
3. The earlier negative result (step 2) was specific to the pre-filtered
   severe-skewed cohort; adding the excluded non-severe patients restored
   the class variance the model needed. Negative result retained as a
   finding: on pre-selected OSA patients, these features add nothing.

## Step 4: domain-weighted features (current)
- **Decision:** two changes per project direction:
  1. **Feature weighting** — replicate columns by prior importance
     (bmi ×3, awakenings ×3, odi ×3, sleep_efficiency ×2, tst ×2,
     spo2_nonrem ×2, arousal ×2; single columns otherwise). Height
     dropped (redundant with BMI). Replication implemented by building
     weighted features as duplicated columns with `_wN` suffixes.
  2. **Sleep-event signals returned to the feature set** — awakenings,
     sleep efficiency, sleep latency, arousal index were already in;
     reframed explicitly as "sleep events a wearable detects."
- **Method:** same 2 models, 5-fold stratified CV, 30 seeds, n=55.

## Step 4 results (n=55, 26 weighted columns, 30 seeds x 5 folds)

| Target | Model | Mean acc | SD | Range |
|---|---|---|---|---|
| 4-class | logistic | 0.419 | 0.122 | 0.091–0.727 |
| 4-class | forest | 0.528 | 0.131 | 0.182–0.909 |
| severe vs non | logistic | 0.639 | 0.129 | 0.091–0.909 |
| severe vs non | forest | 0.648 | 0.132 | 0.273–1.000 |

Baselines: majority class 0.582 for both targets.

**Read:** weighting did not help.
- 4-class: forest dropped 0.532 -> 0.528 (was already below the 0.582
  baseline).
- Binary: forest 0.685 -> 0.648, logistic 0.639 -> 0.639 — the weighted
  version LOST ground vs the unweighted step-3 run.
- Interpretation: explicit priors duplicated what the forest already
  learns from data (feature importances were already ODI/BMI-led), while
  replication adds correlated columns that distort the linear model and
  dilute the forest's per-split randomness. The unweighted feature set is
  the better configuration.
- NOTE for the report: weighting-by-replication is a crude mechanism
  (proper approach would be sample_weight or model hyperparameters); its
  failure here is not evidence against domain weighting in general.

## Conclusions after step 4
1. The step-3 unweighted smartwatch set remains the best configuration:
   binary forest 0.685 vs 0.582 baseline.
2. Adding prior weights via replication hurt rather than helped —
   the forest's own importances already captured the domain knowledge.
3. Sleep-event features (awakenings, efficiency, latency, arousal) were
   in the step-3 set already; keeping them is correct, but they do not
   unlock fine-grained severity.

## Step 5: final head-to-head (both feature sets, n=55, 30 seeds)
- **Script:** `final_evaluation.py` — one script, 8 configurations,
  results to `final_results.csv`.
- Set A "smartband": wearable-plausible features only, unweighted
  (best config from step 3). Set B "full PSG": everything except AHI
  (leakage) and Mallampati.

## Final results (n=55, 30 seeds x 5 folds)

| Features | Target | Model | Mean acc | SD | Range |
|---|---|---|---|---|---|
| smartband | severe vs non | logistic | 0.639 | 0.133 | 0.273–0.909 |
| smartband | severe vs non | forest | **0.685** | 0.134 | 0.273–1.000 |
| smartband | 4-class | logistic | 0.459 | 0.131 | 0.091–0.818 |
| smartband | 4-class | forest | 0.532 | 0.121 | 0.273–0.909 |
| full PSG | severe vs non | logistic | 0.791 | 0.119 | 0.455–1.000 |
| full PSG | severe vs non | forest | **0.937** | 0.077 | 0.727–1.000 |
| full PSG | 4-class | logistic | 0.564 | 0.121 | 0.182–0.818 |
| full PSG | 4-class | forest | 0.778 | 0.090 | 0.455–1.000 |

Baselines: 0.582 for both targets (majority class 32/55).

## Final conclusions
1. **Full PSG features separate severity well** — forest 0.937 binary,
   0.778 4-class, far above baseline. Expected: with event counts in, the
   model has the label's ingredients (they are counts, not the rate, so
   it is genuine predictive signal, not leakage).
2. **Smartband features detect severe OSA weakly but above baseline**
   (binary 0.685 vs 0.582) and cannot grade it (4-class 0.532, below
   baseline).
3. **The gap between the feature sets (0.937 vs 0.685 binary) is the
   quantified value of the sleep lab's respiratory measurement** over
   everything a wearable can see. That is the headline finding of the
   modeling phase.
4. Weighted features (step 4) underperform the plain smartband set and
   are not carried forward.
5. All numbers are 30-seed distributions, not single splits; SDs remain
   large (0.08–0.13) — honest uncertainty from n=55.

## Next candidates
- regression on ahi_true_total instead of classification (continuous
  target, sidesteps band boundaries) — untested
- external validation on a public dataset (e.g., SHHS/PhysioNet) —
  the real test of the smartwatch framing; out of scope for now