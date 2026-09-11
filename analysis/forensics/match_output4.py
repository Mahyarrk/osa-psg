"""
match_output4.py — match the SPSS Output4 correlation matrix (q44, q30, q31,
AHItotal) against our computed values, to see exactly which numbers the
thesis author got and whether they equal ours.

Run:  uv run match_output4.py
"""

import pandas as pd
from scipy import stats

from clean import load_clean

inc = load_clean()
inc = inc[~inc["excluded"]].assign(
    q30=lambda d: d["ahi_rem"],
    q31=lambda d: d["ahi_nonrem"],
    q44=lambda d: d["ess_total"],
    AHItotal=lambda d: d["ahi_rem"] + d["ahi_nonrem"],
)

# SPSS Output4 cells (from the binary): r, p pairs
spv_cells = [
    (-0.1738, 0.4278), (-0.2102, 0.3357), (-0.2198, 0.3137),
    (0.6096, 0.002), (0.66, 0.0006), (0.0126, 0.9932),
]

pairs = [
    ("q44", "q30"), ("q44", "q31"), ("q44", "AHItotal"),
    ("q30", "q31"), ("q30", "AHItotal"), ("q31", "AHItotal"),
]
print("our computations vs SPSS output cells:")
ours = []
for a, b in pairs:
    r, p = stats.pearsonr(inc[a], inc[b])
    ours.append((a, b, r, p))
    print(f"  {a:9s} x {b:9s}: r={r:8.4f}  p={p:8.4f}")

print("\nSPSS cells (order as stored):")
for r, p in spv_cells:
    print(f"  r={r:8.4f}  p={p:8.4f}")