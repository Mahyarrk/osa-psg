# osa-psg

**Reanalysis and reproducibility audit of a sleep-medicine MD thesis — from raw polysomnography data to machine learning, in Python.**

Author: **Dr Mahyar Mirzazadeh, M.D.** — [LinkedIn](https://www.linkedin.com/in/mahyar-mirzazadeh-550b3b166)

## What this is

My MD thesis (defended 2023, Qazvin University of Medical Sciences) studied
whether obstructive sleep apnea (OSA) severity differs between REM and
non-REM sleep. Of 55 polysomnography (PSG) reports, 42 met the inclusion
criteria and formed the study cohort. The original analysis was done in
SPSS. Now — learning Python — I rebuilt the entire analysis from the raw
data, audited it, and took it further than the original study could go.

This repository is the complete pipeline: data cleaning, thesis
reproduction, statistical audit, a derived clinical index, and a
machine-learning study asking what a consumer smartwatch can and cannot
see of OSA severity.

**AI disclosure:** AI tooling (Claude, via the Hermes agent framework) was
used for code drafting and SPSS-output forensics. All scientific decisions —
study design, column identification, exclusion criteria, statistical
interpretation, and modeling strategy — were made and verified by the author.

## Key results

| Phase | Result |
|---|---|
| Reproduction | **99/99** descriptive statistics from the thesis reproduce exactly |
| Audit | One published test statistic traced to a different test than claimed (details in `report.md`); the underlying data is intact |
| AHI derivation | True total AHI recovered from event counts (AASM definition), validated two independent ways |
| Machine learning | Sleep-lab features predict OSA severity at **0.937** accuracy; wearable-plausible features reach **0.685** vs a 0.582 baseline — a 25-point quantification of what the sleep lab adds |

## The pipeline

```
data_raw.xlsx                    # 55 PSG reports (private, git-ignored)
   │ clean.py                    # decode q-columns, apply exclusions (n=42)
   ▼
data_clean.csv / data_included.csv
   │ verify_tables.py            # 99-check acceptance test vs thesis tables
   │ stats_tests.py              # correlations & t-tests (thesis Tables 8–13)
   │ build_model_table.py        # AHI derivation + severity bands (n=55)
   ▼
data_model.csv
   │ final_evaluation.py         # 8 configurations × 30 seeds
   ▼
final_results.csv                # every number in the results table
```

## How to run

```bash
git clone https://github.com/mahyarrk/osa-psg.git
cd osa-psg
uv sync                # or: pip install pandas scipy scikit-learn openpyxl
uv run clean.py
uv run verify_tables.py    # → 99 PASS
uv run final_evaluation.py # → the results table
```

Requires Python 3.12+. The raw dataset belongs to the sleep clinic and is
not distributed (git-ignored).

## Files

| File | Purpose |
|---|---|
| `rename_map.py` | validated column dictionary (single source of truth) |
| `clean.py` | load → decode → exclusions → CSVs |
| `verify_tables.py` | 99-check acceptance test vs thesis Tables 1–7 |
| `stats_tests.py` | recomputed correlations and t-tests |
| `explore_table13.py` | forensic reconstruction of one published test statistic |
| `build_model_table.py` | total-AHI derivation + severity bands |
| `final_evaluation.py` | the final head-to-head evaluation |
| `report.md` | full writeup: methods, discrepancies, results |
| `modeling_log.md` | every modeling decision, including negative results |

## The two feature sets

- **Smartband-plausible (22 features):** only signals a consumer wearable
  genuinely measures — body metrics (age, sex, height, weight, BMI),
  sleep timing/continuity (total sleep time, latency, awakenings,
  efficiency), oxygenation (mean SpO2 awake/REM/non-REM, ODI), movement
  (arousal index, PLMS index), and symptom questionnaires.
- **Full PSG (36 features):** the smartband set **plus** the eight raw
  respiratory event counts (obstructive/central/mixed apneas and
  hypopneas, each split by REM/non-REM) and the hypnotic-use symptom —
  but still no AHI columns (those define the label — target leakage) and
  no Mallampati (44/55 missing).

Both sets see the same 55 patients (the full referral cohort) and the
same severity target, derived from the AASM-definition total AHI.

## Findings in brief

1. **The thesis's descriptive statistics reproduce completely** — 99/99
   published values recomputed from raw data. The data foundation is sound.
2. **One inferential claim does not survive re-analysis.** A paired
   REM-vs-non-REM comparison shows no significant difference (t≈0.23,
   p≈0.82); the published t-value traces to a one-sample test visible in
   the archived SPSS outputs. The physiological question stays open at
   this sample size.
3. **Severity is gradable from full PSG features (0.937 severe-vs-not,
   0.778 four-class) but only weakly detectable from smartwatch-grade
   signals (0.685 binary) — and not gradable at all.** The gap measures
   what the sleep lab's respiratory measurement adds over everything a
   wearable can see.
4. **Wearability assumption, disclosed:** the smartband set assumes
   *perfect fidelity* of its signals — the model received PSG-grade SpO2
   and PSG-scored awakenings, while real devices (Apple Watch breathing-
   disturbance notifications, Galaxy Watch apnea detection) sample SpO2
   intermittently and infer sleep stages without EEG. Real-world wearable
   performance will therefore sit below 0.685; that figure is an
   optimistic ceiling. The full-PSG set contains typed, stage-localized
   event counts that no current wearable can produce, so the 25-point gap
   is the irreducible value of laboratory respiratory measurement.

## Notes

- The raw dataset contains patient identifiers and is **not** in this
  repository. Public distribution of de-identified data is pending an
  ethics discussion.
- A reproducibility short paper is in preparation.
- Feedback welcome — this project was built as a first serious Python
  effort, and code review is welcome.