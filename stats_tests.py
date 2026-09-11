"""
stats_tests.py — reproduce the thesis's inferential statistics (Tables 8-13)
and re-test the core REM vs non-REM hypothesis with the correct paired test.

Run:  uv run stats_tests.py
"""

import pandas as pd
from scipy import stats

from clean import load_clean


def main() -> None:
    df = load_clean()
    inc = df[~df["excluded"]].copy()
    inc["ahi_total"] = inc["ahi_rem"] + inc["ahi_nonrem"]

    print("=== Core hypothesis: AHI REM vs AHI non-REM ===")
    t, p = stats.ttest_rel(inc["ahi_rem"], inc["ahi_nonrem"])
    print(f"  paired t-test: t={t:.3f}, p={p:.5f} "
          f"(mean {inc['ahi_rem'].mean():.2f} vs {inc['ahi_nonrem'].mean():.2f})")

    print("=== Table 8: ESS correlations ===")
    # thesis Table 8 (r=-0.305) reproduces as the correlation WITHIN the
    # ESS>=8 group; full-cohort ESS x AHI is r=0.055.
    sub = inc[inc["ess_total"] >= 8]
    r, p = stats.pearsonr(sub["ess_total"], sub["ahi_total"])
    ok = abs(r - (-0.305)) < 0.03
    print(f"  [{'PASS' if ok else 'FAIL'}] within ESS>=8 (n={len(sub)}):        r={r:.3f}  p={p:.4f}  (thesis r=-0.305, p=0.138)")
    r, p = stats.pearsonr(inc["ess_total"], inc["ahi_total"])
    print(f"  full cohort ESS x AHI total:        r={r:.3f}  p={p:.4f}")

    print("=== Table 9: arousal index vs AHI ===")
    for label, col, rw in [
        ("arousal x AHI REM", "ahi_rem", 0.271),
        ("arousal x AHI non-REM", "ahi_nonrem", 0.366),
        ("arousal x AHI total", "ahi_total", 0.358),
    ]:
        r, p = stats.pearsonr(inc["arousal_index"], inc[col])
        ok = abs(r - rw) < 0.03
        print(f"  [{'PASS' if ok else 'FAIL'}] {label:35s} r={r:.3f}  p={p:.4f}  (thesis r={rw})")

    print("=== Table 10/11: ODI correlations ===")
    pairs = [
        ("ODI x AHI total", "odi", "ahi_total", 0.570),
        ("ODI x SpO2 REM", "odi", "spo2_rem_mean", -0.123),
        ("ODI x SpO2 non-REM", "odi", "spo2_nonrem_mean", -0.057),
        ("SpO2 REM x AHI total", "spo2_rem_mean", "ahi_total", -0.358),
        ("SpO2 non-REM x AHI total", "spo2_nonrem_mean", "ahi_total", -0.271),
    ]
    for label, col_a, col_b, rw in pairs:
        pair = inc[[col_a, col_b]].dropna()  # pairwise NaN handling
        r, p = stats.pearsonr(pair[col_a], pair[col_b])
        ok = abs(r - rw) < 0.03
        print(f"  [{'PASS' if ok else 'FAIL'}] {label:35s} r={r:.3f}  p={p:.4f}  (thesis r={rw})")

    print("=== Table 13: BMI>=30 subgroup ===")
    heavy = inc[inc["bmi"] >= 30]
    print(f"  n = {len(heavy)}  (thesis says 21)")
    t, p = stats.ttest_rel(heavy["ahi_rem"], heavy["ahi_nonrem"])
    print(f"  REM AHI {heavy['ahi_rem'].mean():.2f} +- {heavy['ahi_rem'].std():.2f}")
    print(f"  nonREM AHI {heavy['ahi_nonrem'].mean():.2f}  (thesis 64.26)")
    print(f"  paired t={t:.3f}  p={p:.5f}  (thesis printed t=7.89 from a one-sample test)")


if __name__ == "__main__":
    main()