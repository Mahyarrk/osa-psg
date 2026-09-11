"""
explore_table13.py — what test produced the thesis's t=7.89 (df=20, p=0.0001)?

The thesis header says "One-Sample T Test" for Table 13. A paired t-test on
AHI REM vs non-REM in the BMI>30 group gives t=0.23 (p=0.82) — nowhere near
7.89. This script tests the one-sample interpretation: AHI total vs mu=7.5.

Run:  uv run explore_table13.py
"""

import math

import pandas as pd
from scipy import stats

from clean import load_clean

inc = load_clean()
inc = inc[~inc["excluded"]].assign(ahi_total=lambda d: d["ahi_rem"] + d["ahi_nonrem"])
heavy = inc[inc["bmi"] >= 30]  # n=21

print(f"n = {len(heavy)}")
print(f"AHI total: mean {heavy['ahi_total'].mean():.2f}  SD {heavy['ahi_total'].std():.2f}")
print(f"AHI REM  : mean {heavy['ahi_rem'].mean():.2f}  SD {heavy['ahi_rem'].std():.2f}  (thesis 66.22+-43.66)")
print(f"AHI nonREM: mean {heavy['ahi_nonrem'].mean():.2f}  (thesis 64.26+-37.29)")

t = stats.ttest_1samp(heavy["ahi_total"], 7.5)
print(f"\none-sample t-test AHI total vs mu=7.5: t={t[0]:.2f}  p={t[1]:.6f}  <- thesis t=7.89")

d = heavy["ahi_rem"] - heavy["ahi_nonrem"]
t_paired = d.mean() / (d.std() / math.sqrt(21))
print(f"\npaired t REM vs nonREM: mean diff {d.mean():.2f}, SD {d.std():.2f} -> t={t_paired:.3f}")
print("=> The thesis's claim 'REM AHI significantly > non-REM, t=7.89' is NOT")
print("   supported by a paired test; t=7.89 matches a one-sample test of")
print("   AHI total against mu=7.5 (an OSA-severity null), a different question.")