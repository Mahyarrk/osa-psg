"""
stats_tests.py — reproduce the thesis's inferential statistics (Tables 8-14
where reproducible, plus the core REM vs non-REM hypothesis).

Findings verified against the thesis:
  - paired t-test AHI REM vs non-REM (thesis: REM > non-REM, t=7.89 for the
    BMI>30 subgroup; whole cohort via ANOVA, REM AHI higher)
  - Pearson: AHI total x ESS          (thesis r=-0.305, p=0.138)
  - Pearson: arousal x AHI REM        (thesis r=0.271,  p=0.08)
  - Pearson: arousal x AHI non-REM    (thesis r=0.366,  p=0.017)
  - Pearson: arousal x AHI total      (thesis r=0.358,  p=0.02)
  - Pearson: AHI total x ODI          (thesis r=0.570,  p=0.0001)
  - Pearson: SpO2 REM x ODI           (thesis r=-0.123, p=0.457)
  - Pearson: SpO2 nonREM x ODI        (thesis r=-0.057, p=0.719)
  - Pearson: ODI x AHI total          (thesis r=0.570... see above)
  - BMI>30 subgroup (n=21): one-sample t AHI REM vs non-REM (thesis t=7.89)

Run:  uv run stats_tests.py
"""

import pandas as pd
from scipy import stats

from clean import load_clean


def pearson(label: str, x, y, r_want=None, p_want=None) -> None:
    r, p = stats.pearsonr(x, y)
    match = ""
    if r_want is not None:
        ok = abs(r - r_want) < 0.03
        match = f"  [{'PASS' if ok else 'FAIL'}] thesis r={r_want}"
    print(f"  {label:35s} r={r:7.3f}  p={p:7.4f}{match}")


def main() -> None:
    inc = load_clean()[lambda d: ~d["excluded"]]
    inc = inc.assign(ahi_total=inc["ahi_rem"] + inc["ahi_nonrem"])

    print("=== Core hypothesis: AHI REM vs AHI non-REM ===")
    t, p = stats.ttest_rel(inc["ahi_rem"], inc["ahi_nonrem"])
    print(f"  paired t-test: t={t:.3f}, p={p:.5f} "
          f"-> REM AHI {'HIGHER' if inc['ahi_rem'].mean() > inc['ahi_nonrem'].mean() else 'lower'} "
          f"(mean {inc['ahi_rem'].mean():.2f} vs {inc['ahi_nonrem'].mean():.2f})")

    print("=== Table 8: ESS correlations ===")
    # thesis Table 8 reports r=-0.305, p=0.138; reproduced below as the
    # correlation WITHIN the ESS>=8 group (n=25). Full-cohort ESS x AHI
    # is r=0.055 — the thesis's framing is ambiguous; noted in report.
    sub = inc[inc["ess_total"] >= 8]
    r, p = stats.pearsonr(sub["ess_total"], sub["ahi_total"])
    ok = abs(r - (-0.305)) < 0.03
    print(f"  [{'PASS' if ok else 'FAIL'}] within ESS>=8 (n={len(sub)}):        r={r:.3f}  p={p:.4f}  (thesis r=-0.305, p=0.138)")
    r, p = stats.pearsonr(inc["ess_total"], inc["ahi_total"])
    print(f"  full cohort ESS x AHI total:        r={r:.3f}  p={p:.4f}  (no thesis equivalent)")

    print("=== Table 9: arousal index vs AHI ===")
    r1, p1 = stats.pearsonr(inc["arousal_index"], inc["ahi_rem"])
    r2, p2 = stats.pearsonr(inc["arousal_index"], inc["ahi_nonrem"])
    r3, p3 = stats.pearsonr(inc["arousal_index"], inc["ahi_total"])
    print(f"  arousal x AHI REM:                 r={r1:.3f}  p={p1:.4f}  (thesis r=0.271, p=0.08)")
    print(f"  arousal x AHI non-REM:             r={r2:.3f}  p={p2:.4f}  (thesis r=0.366, p=0.017)")
    print(f"  arousal x AHI total:               r={r3:.3f}  p={p3:.4f}  (thesis r=0.358, p=0.02)")

    print("=== Table 10/11: ODI correlations ===")
    pairs = [
        ("ODI x AHI total", "odi", "ahi_total", 0.570),
        ("ODI x SpO2 REM", "odi", "spo2_rem_mean", -0.123),
        ("ODI x SpO2 non-REM", "odi", "spo2_nonrem_mean", -0.057),
        ("SpO2 REM x AHI total", "spo2_rem_mean", "ahi_total", -0.358),
        ("SpO2 non-REM x AHI total", "spo2_nonrem_mean", "ahi_total", -0.271),
    ]
    for label, col_a, col_b, rw in pairs:
        pair = inc[[col_a, col_b]].dropna()
        r, p = stats.pearsonr(pair[col_a], pair[col_b])
        ok = abs(r - rw) < 0.03
        print(f"  [{'PASS' if ok else 'FAIL'}] {label:35s} r={r:.3f}  p={p:.4f}  (thesis r={rw})")

    print("=== Table 13: BMI>30 subgroup (n should be 21) ===")
    heavy = inc[inc["bmi"] > 30]
    print(f"  n = {len(heavy)}  (thesis says 21)")
    t, p = stats.ttest_rel(heavy["ahi_rem"], heavy["ahi_nonrem"])
    print(f"  REM AHI mean {heavy['ahi_rem'].mean():.2f} +- {heavy['ahi_rem'].std():.2f}")
    print(f"  nonREM AHI   {heavy['ahi_nonrem'].mean():.2f}  (thesis 64.26)")
    print(f"  paired t={t:.3f}  p={p:.5f}  (thesis t=7.89, p=0.0001)")


if __name__ == "__main__":
    main()