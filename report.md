# Reanalysis of an OSA Thesis Dataset: A Reproducibility Audit

**Project:** `osa-psg` — Python/pandas reanalysis of a 2023 sleep-medicine MD thesis
**Cohort:** 55 adult PSG reports (OSA + PLMD referrals, Qazvin, 1395–1400); thesis cohort 42 (32 M / 10 F); full modeling cohort 55
**Author:** Dr Mahyar Mirzazadeh, M.D. — thesis author (defended 2023).
SPSS statistical analyses were performed by the thesis supervisor,
Dr. Soleymannejad. AI tooling was used for code drafting and SPSS-output
forensics; all scientific decisions in this reanalysis — column
identification, exclusion criteria, statistical interpretation, modeling
strategy — were made and verified by the author.

---

## 1. Why

The thesis examined whether AHI differs between REM and non-REM sleep in
obstructive sleep apnea. The original analysis was done in SPSS; this
reanalysis rebuilds the entire pipeline in Python (pandas, scipy) so that
every published number can be recomputed from the raw data, and so the
dataset can support future machine-learning work.

The goal is reproduction and quality improvement — the thesis was produced
under real clinical-workload constraints, and this audit is done in that
spirit: verify what reproduces, understand what does not, and document it
plainly.

## 2. Data and pipeline

- **Source:** `data_raw.xlsx` (55 rows × 47 columns) — patient-level PSG
  report data. Kept private; contains identifying information.
- **Column decode:** every q1–q44 column was identified against the thesis's
  published statistics (mean, SD, and sex-split per variable). All 47
  columns are accounted for and verified. See `rename_map.py`.
- **Cleaning:** `clean.py` applies the thesis's exclusion criteria
  (13 patients: 4 upper-airway obstruction, 4–5 normal studies, 1 primary
  snoring, 2 narcolepsy referrals, 1 convulsion referral, 1 parasomnia),
  leaving exactly the thesis cohort of 42 (32 M / 10 F). Two exclusions were
  recoverable only through statistical triangulation against the thesis's
  published tables (age, BMI, symptom counts); this is documented in the
  exclusion table.
- **Verification:** `verify_tables.py` recomputes every descriptive statistic
  in thesis Tables 1, 2, 3, 4, 6, and 7 — **99/99 checks reproduce the
  published values** to rounding tolerance.

## 3. Inferential statistics: what reproduces

`stats_tests.py` recomputes the thesis's correlation analyses (Tables 8–11)
with scipy. Reproduced essentially exactly:

| Relationship | Thesis | This reanalysis |
|---|---|---|
| Arousal index × AHI REM | r = 0.271, p = 0.08 | r = 0.271, p = 0.082 |
| Arousal index × AHI non-REM | r = 0.366, p = 0.017 | r = 0.366, p = 0.017 |
| Arousal index × AHI total | r = 0.358, p = 0.02 | r = 0.349, p = 0.023 |
| ODI × mean SpO2 REM | r = −0.123, p = 0.457 | r = −0.123, p = 0.457 |
| ODI × mean SpO2 non-REM | r = −0.057, p = 0.719 | r = −0.057, p = 0.719 |
| SpO2 non-REM × AHI total | r = −0.271, p = 0.083 | r = −0.276, p = 0.077 |
| ESS × AHI (within ESS≥8) | r = −0.305, p = 0.138 | r = −0.325, p = 0.112 |

The BMI≥30 subgroup (thesis Table 13) reproduces exactly as well:
n = 21, REM AHI 66.23 ± 43.66 (thesis: 66.22 ± 43.66), non-REM AHI 64.27
(thesis: 64.26).

## 4. Discrepancies found

Three discrepancies surfaced. None undermines the dataset, which is intact
and internally consistent throughout.

### 4.1 Two transcription slips in Table 6 (AHI REM row)

The published overall mean for AHI REM (59.92) is not the average of the
table's own sex-split values (M 52.27, F 63.39 → weighted mean 54.92, which
the data confirms). The female SD appears as 31.04 where the data gives
41.04. The per-sex values — the numbers the table is actually built on —
match the data exactly, so these are presentation-layer slips only.

### 4.2 Table 13: the test statistic and the claim refer to different tests

Table 13 reports "One-Sample T Test … t = 7.89, df = 20, p = 0.0001" and the
accompanying text reads this as evidence that REM AHI exceeded non-REM AHI.

Reconstruction from the archived SPSS output (`.spv` files, included with
this project) shows the arithmetic precisely:

- A one-sample t-test of **AHI non-REM against 0** in the BMI≥30 group
  returns t = 7.897 — the source of the published 7.89.
- The **paired** t-test of AHI REM vs non-REM in the same subgroup — the
  test the research question calls for — gives t ≈ 0.23, p ≈ 0.82
  (n = 21), i.e. no significant difference.
- The paired test on the full cohort (visible in the archived SPSS output)
  likewise shows no significant difference (mean difference 1.31, t = 0.286).

The descriptive direction (REM AHI slightly higher on average: 66.2 vs 64.3
in the obese subgroup; 54.9 vs 53.6 overall) is real in the data, but the
between-stage difference does not reach statistical significance under the
appropriate paired test. This is an easy slip to make in SPSS, where
one-sample and paired dialogs sit side by side — the archived output shows
both were run in the same session.

A constructive reading: the cohort's REM-vs-non-REM difference is small and
underpowered at n = 42; the thesis's qualitative observation (REM events
concentrated in a short stage) remains physiologically interesting and worth
re-examination in a larger sample.

### 4.3 Two correlation cells with small, unexplained offsets

- ODI × AHI total: published r = 0.570; recomputed r = 0.627. (ODI × AHI
  REM gives 0.560 — close to the published value, so a mislabeled row is
  plausible but unconfirmed.)
- SpO2 REM × AHI total: published r = −0.358; recomputed −0.424 (n = 39;
  four patients had no REM sleep, so subset choices matter here).

Both are flagged as open items rather than resolved.

## 5. Total AHI: derivation

The dataset stores stage-specific rates (REM AHI, non-REM AHI), not a total.
These cannot be summed (rates with different denominators). The AASM
definition — total apneas + hypopneas per hour of sleep — was applied to the
raw event counts:

    ahi_true_total = (all apnea and hypopnea counts) / (total sleep time in hours)

Two independent validations: (1) a weighted-average reconstruction from the
stage AHIs (using the cohort's REM share) predicts 53.7 vs the
count-derived 54.05; (2) the derived quantity correlates with ODI at
r = 0.58–0.64, within the expected range. The thesis's own "AHI total"
variable cannot be uniquely reconstructed from archived outputs (see §4.2);
its correlations reproduce under either construction. The severity target
for the modeling phase (§7) uses the AASM-derived value.

## 6. Limitations of this reanalysis

1. **Sleep-stage percentages** (thesis Tables 12 and 14: N1/N2/N3/REM
   proportions) are not present in the spreadsheet or the archived SPSS
   dataset; those analyses could not be independently recomputed.
2. **Final OSA severity grades** (used for one chart and one correlation)
   were likewise not in the dataset.
3. Two exclusion identities were recovered statistically rather than from
   records (patient files are no longer available); both identifications
   reproduce the published demographics exactly, but they remain
   inferences.
4. Dataset is small (n = 42); all conclusions carry the corresponding
   uncertainty.

## 7. Modeling: predicting severity, and what a smartwatch can see

After reproduction, the project branched into machine learning
(`modeling_log.md` documents every step, including two negative results).

**Target derivation.** Severity bands were assigned from the AASM-derived
total AHI (§5): Normal <5, Mild 5–14, Moderate 15–29, Severe ≥30.
The full cohort of 55 was used for modeling — the 13 thesis-excluded
patients return, because a screening model's correct population is
"everyone referred to the sleep lab," not a pre-filtered disease group.
Their profile (7 normal / 2 mild / 1 moderate / 3 severe) makes the mixed
cohort: 7 normal / 5 mild / 11 moderate / 32 severe.

**Leakage control.** No AHI column (any construction) was available to the
models: severity is *defined* by total AHI, so a model that sees AHI would
re-derive its own label and report a fake score. Event *counts* were
allowed — they are the ingredients, not the rate, so using them is genuine
prediction.

**Protocol.** Two feature sets × two targets × two models, 5-fold
stratified cross-validation, **30 random seeds** per configuration (single
splits proved unstable at this n: fold accuracies ranged up to 1.0 by
seed). Majority-class baseline: 0.582.

| Features | Target | Model | Accuracy (30 seeds) |
|---|---|---|---|
| Smartband-plausible | severe vs non-severe | random forest | **0.685 ± 0.134** |
| Smartband-plausible | severe vs non-severe | logistic | 0.639 ± 0.133 |
| Smartband-plausible | 4-class severity | random forest | 0.532 ± 0.121 |
| Smartband-plausible | 4-class severity | logistic | 0.459 ± 0.131 |
| Full PSG | severe vs non-severe | random forest | **0.937 ± 0.077** |
| Full PSG | severe vs non-severe | logistic | 0.791 ± 0.119 |
| Full PSG | 4-class severity | random forest | **0.778 ± 0.090** |
| Full PSG | 4-class severity | logistic | 0.564 ± 0.121 |

**The two feature sets.**

- *Smartband-plausible (22 features):* only signals a consumer wearable
  genuinely measures — body metrics (age, sex, height, weight, BMI),
  sleep timing/continuity (total sleep time, latency, awakenings,
  efficiency), oxygenation (mean SpO2 awake/REM/non-REM, ODI), movement
  (arousal index, PLMS index), and symptom questionnaires. No event
  counts, no stage-specific AHI, no Mallampati.
- *Full PSG (36 features):* the smartband set **plus** the eight raw
  respiratory event counts (obstructive/central/mixed apneas and
  hypopneas, each split by REM/non-REM) and the hypnotic-use symptom —
  but still **no** AHI columns, since those define the label (see
  leakage control above), and no Mallampati (44/55 missing).

**The wearability assumption, disclosed.** The smartband set assumes
*perfect fidelity* of these signals: the model received PSG-grade SpO2
and PSG-scored awakenings, while real devices (Apple Watch breathing-
disturbance notifications, Galaxy Watch sleep apnea detection) sample
SpO2 intermittently, infer sleep stages without EEG, and detect
disturbances through proxy signals. Real-world wearable performance will
therefore sit **below** our 0.685 — that figure is an optimistic ceiling.
The full-PSG set, by contrast, includes typed, stage-localized event
counts (obstructive/central/mixed × REM/non-REM) that no current wearable
can produce; assuming a "fully accurate" consumer disturbance
notification would not bridge this, because it would amount to handing
the model the aggregate it is supposed to predict. The 25-point gap
between the sets is thus the irreducible value of laboratory respiratory
measurement — and this study's smartwatch framing extends only to the
smartband set.

**Binary-task sensitivity and specificity (30-seed distributions).**
For the severe-vs-non-severe task, accuracy alone hides the clinical
trade-off, so each seed's pooled predictions were also scored for
sensitivity (severe patients correctly flagged) and specificity
(non-severe patients correctly cleared). Averages over 30 seeds:

| Features | Model | Accuracy | Sensitivity (severe) | Specificity (non-severe) |
|---|---|---|---|---|
| Smartband | logistic | 0.639 ± 0.046 | 0.683 ± 0.052 | 0.578 ± 0.074 |
| Smartband | random forest | 0.685 ± 0.040 | 0.750 ± 0.058 | 0.594 ± 0.064 |
| Full PSG | logistic | 0.791 ± 0.030 | 0.802 ± 0.046 | 0.775 ± 0.044 |
| Full PSG | random forest | 0.937 ± 0.033 | 0.974 ± 0.029 | 0.886 ± 0.060 |

(Here the ± is the standard deviation *across the 30 seed-level values* —
smaller than the fold-to-fold spread quoted earlier, because each seed's
value is already pooled over 55 out-of-fold predictions.)

Read clinically: the smartband forest catches 75% of severe patients but
clears only ~59% of non-severe ones — a triage profile: few missed cases,
many false alarms, every positive going to the sleep lab anyway. The
full-PSG forest (0.974 / 0.886) approaches diagnostic-grade performance
on both axes. The `class_weight="balanced"` setting deliberately trades
specificity for sensitivity in both models.

**How the accuracy scores are calculated.** Every patient is predicted
exactly once per seed by a model that never saw them during that fold's
training: the 55 patients are split into 5 stratified folds; the model
trains on 4 folds and predicts the held-out one; rotation assigns every
patient to the holdout exactly once. Each patient's predicted class is
compared to the truth derived from their total AHI; accuracy is the share
of correct predictions (32+23 = 55 comparisons per seed). The reported
number is the mean of 30 such accuracies (one per random fold split),
with the standard deviation across seeds as the uncertainty. Sensitivity
and specificity decompose the same confusion counts by true class.
No patient is ever scored by a model that trained on them; imputation
and scaling are fitted inside each fold's training data only.

**ROC-AUC (30-seed distributions).** Accuracy and sens/spec describe the
model at one decision cutoff; ROC-AUC measures the quality of the
underlying *ranking*, independent of any cutoff. It answers: if one random
severe and one random non-severe patient are picked, how often does the
model assign the severe patient the higher severity probability? 0.5 =
chance, 1.0 = perfect ordering.

| Features | Model | ROC-AUC |
|---|---|---|
| Smartband | logistic | 0.669 ± 0.040 |
| Smartband | random forest | **0.740 ± 0.037** |
| Full PSG | logistic | 0.865 ± 0.031 |
| Full PSG | random forest | **0.989 ± 0.009** |

Two readings: the smartband forest's discrimination (0.740) is
meaningfully better than its accuracy (0.685) suggests — the class
weighting costs accuracy at the 0.5 cutoff, not ranking ability. And the
full-PSG forest's 0.989 (SD 0.009 — the most stable number in this study)
is near-perfect pair-ranking, threshold-independent confirmation of the
0.937 accuracy. AUC is unaffected by class balance, which makes these
four values directly comparable.

**Findings.**

1. **Full PSG features predict severity well** (0.937 binary, 0.778
   4-class, vs 0.582 baseline). The model sees event counts, not the rate
   formula, so this is genuine signal.
2. **Smartwatch-grade features detect severe OSA weakly but above
   baseline** (0.685 vs 0.582) and cannot grade severity (4-class below
   baseline). Their strongest signals: ODI and BMI.
3. **The 25-point gap between feature sets is the quantified value of the
   sleep lab's respiratory measurement** over everything a wearable can
   see. Wearables see the consequences of OSA; the lab measures its cause.
4. Two documented negative results along the way: on the pre-filtered
   42-patient OSA cohort, smartwatch features added nothing (all models
   below baseline — the cohort's severity skew left nothing to learn);
   and prior-importance feature weighting by column replication hurt
   rather than helped.
5. Methodological note: at n = 55, single-seed evaluations were unstable
   (fold accuracies up to 1.0); the multi-seed protocol is what makes the
   numbers above quotable.

## 8. What this repo contains

| File | Purpose |
|---|---|
| `rename_map.py` | validated column dictionary (single source of truth) |
| `clean.py` | load → decode → exclusions → `data_clean.csv` / `data_included.csv` |
| `verify_tables.py` | 99-check acceptance test vs thesis Tables 1–7 |
| `stats_tests.py` | recomputed correlations and t-tests (Tables 8–13) |
| `explore_table13.py` | the Table 13 forensic reconstruction |
| `extract_spv.py`, `find_t789.py`, `match_output4.py` | SPSS `.spv` extraction tooling |
| `build_model_table.py` | AHI derivation + severity bands → `data_model.csv` |
| `train_severity_model.py` | smartwatch-feature modeling (current feature set) |
| `final_evaluation.py` | final head-to-head: 8 configurations × 30 seeds → `final_results.csv` |
| `modeling_log.md` | the complete modeling decision trail, incl. negative results |

All data files are git-ignored; only code is version-controlled.

## 9. Conclusions

1. The thesis's descriptive statistics reproduce completely (99/99 checks)
   from the raw dataset — the data foundation is sound.
2. One published inferential claim (Table 13) does not survive re-analysis
   with the appropriate paired test; the published t-value traces to a
   one-sample test present in the archived SPSS output. The REM-vs-non-REM
   direction remains descriptively real but is not significant at this
   sample size.
3. Total AHI is recoverable from event counts and validated two ways;
   severity bands follow AASM cutoffs.
4. In a mixed referral cohort, wearable-grade features detect severe OSA
   above chance but cannot grade severity; the sleep lab's respiratory
   measurement accounts for a quantified 25-point accuracy gap.

## 10. Next steps

- Continuous-target regression on total AHI (sidesteps band boundaries).
- External validation on a public sleep dataset (SHHS/PhysioNet) — the
  real test of the smartwatch screening framing.
- A standalone short paper is possible from §4 (reproducibility audit) +
  §7 (modeling), pending co-author discussions.