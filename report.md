# Reanalysis of an OSA Thesis Dataset: A Reproducibility Audit

**Project:** `osa-psg` — Python/pandas reanalysis of a 2022 sleep-medicine MD thesis
**Cohort:** 55 adult PSG reports (OSA + PLMD referrals, Qazvin, 1395–1400), 42 included (32 M / 10 F)
**Author of this audit:** Dr. Mahyar Mirzazadeh (thesis co-author), with a Python agent
**Status:** week 1 of a 30-day reanalysis sprint

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

## 5. Limitations of this reanalysis

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

## 6. What this repo contains

| File | Purpose |
|---|---|
| `rename_map.py` | validated column dictionary (single source of truth) |
| `clean.py` | load → decode → exclusions → `data_clean.csv` / `data_included.csv` |
| `verify_tables.py` | 99-check acceptance test vs thesis Tables 1–7 |
| `stats_tests.py` | recomputed correlations and t-tests (Tables 8–13) |
| `explore_table13.py` | the Table 13 forensic reconstruction |
| `extract_spv.py`, `find_t789.py`, `match_output4.py` | SPSS `.spv` extraction tooling |

All data files are git-ignored; only code is version-controlled.

## 7. Next steps

- Week 2: severity prediction from PSG features (scikit-learn), using the
  same cleaned dataset.
- A short write-up of §4 as a standalone reproducibility report, suitable
  for a blog post or a letter to the original journal if the co-authors
  wish.