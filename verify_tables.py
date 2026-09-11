"""
verify_tables.py — acceptance test: reproduce thesis Tables 1, 2, 3, 4, 6, 7.

Each check computes a statistic from the 42 included patients and compares
it to the number printed in the thesis. If any FAIL appears, either the
exclusion list or the column mapping is wrong — debug before any analysis.

Run:  uv run verify_tables.py
"""

import pandas as pd

from clean import load_clean

TOL = 0.06  # thesis rounds to 2 decimals; allow tiny drift


def check(label: str, got: float, want: float) -> None:
    ok = abs(got - want) <= TOL
    flag = "PASS" if ok else "FAIL"
    print(f"  [{flag}] computed {got:8.2f} | thesis {want:8.2f}  {label}")


def main() -> None:
    df = load_clean()
    inc = df[~df["excluded"]]
    m = inc[inc["sex_label"] == "male"]
    f = inc[inc["sex_label"] == "female"]

    print("=== Table 1: age ===")
    check("male age mean", m["age_years"].mean(), 45.13)
    check("male age SD", m["age_years"].std(), 9.387)
    check("female age mean", f["age_years"].mean(), 50.50)
    check("female age SD", f["age_years"].std(), 12.501)

    print("=== Table 2: BMI ===")
    check("male BMI mean", m["bmi"].mean(), 30.09)
    check("male BMI SD", m["bmi"].std(), 4.83)
    check("female BMI mean", f["bmi"].mean(), 32.32)
    check("female BMI SD", f["bmi"].std(), 3.22)
    check("all BMI mean", inc["bmi"].mean(), 30.62)
    check("all BMI SD", inc["bmi"].std(), 4.57)

    print("=== Table 3: symptoms (yes = 2) ===")
    sym = [  # (column, thesis male yes, thesis female yes)
        ("snoring", 30, 8), ("apnea_feeling", 20, 9), ("night_sweats", 6, 2),
        ("morning_headache", 6, 1), ("poor_concentration", 13, 1),
        ("sleep_talking", 0, 1), ("night_terrors", 4, 0),
    ]
    for col, mm, ff in sym:
        my = int((m[col] == 2).sum())
        fy = int((f[col] == 2).sum())
        ok = (my, fy) == (mm, ff)
        print(f"  [{'PASS' if ok else 'FAIL'}] {col}: {my}M/{fy}F | thesis {mm}M/{ff}F")

    print("=== Table 4: TST by sex ===")
    check("male TST mean", m["tst_min"].mean(), 362.04)
    check("male TST SD", m["tst_min"].std(), 74.34)
    check("female TST mean", f["tst_min"].mean(), 380.36)
    check("female TST SD", f["tst_min"].std(), 51.55)

    print("=== Table 6: PSG indices, overall ===")
    psg = [  # (column, thesis mean, thesis SD)
        ("sleep_latency_min", 17.27, 15.75),
        ("awakenings_count", 27.0, 14.26),
        ("sleep_efficiency_pct", 77.97, 12.15),
        ("arousal_index", 19.12, 20.18),
        ("plms_index", 1.72, 4.25),
        ("ahi_nonrem", 53.61, 33.72),
        ("obstructive_apnea_rem", 21.95, 31.30),
        ("central_apnea_rem", 1.29, 2.69),
        ("mixed_apnea_rem", 1.98, 9.40),
        ("obstructive_apnea_nonrem", 146.33, 157.43),
        ("central_apnea_nonrem", 6.81, 7.8),
        ("mixed_apnea_nonrem", 8.40, 18.62),
        ("hypopnea_rem", 20.0, 23.0),
        ("hypopnea_nonrem", 118.21, 82.01),
        ("spo2_awake_mean", 92.01, 3.33),
        ("spo2_rem_mean", 90.78, 4.12),
        ("spo2_nonrem_mean", 90.54, 4.20),
        ("odi", 26.93, 26.20),
    ]
    for col, tmean, tsd in psg:
        check(f"{col} mean", inc[col].mean(), tmean)
        check(f"{col} SD", inc[col].std(), tsd)
    # ahi_rem overall: thesis's own overall row (59.92) is internally
    # inconsistent with its M/F values — checked via sex split below.

    print("=== Table 6/7: sex-split means ===")
    sex_checks = [  # (column, male mean, female mean)
        ("ahi_rem", 52.27, 63.39),
        ("ahi_nonrem", 50.90, 62.30),
        ("arousal_index", 14.41, 34.17),
        ("plms_index", 2.14, 0.36),
        ("sleep_latency_min", 17.56, 16.37),
        ("awakenings_count", 28.62, 21.8),
        ("sleep_efficiency_pct", 77.48, 79.54),
        ("obstructive_apnea_rem", 21.00, 25.00),
        ("central_apnea_rem", 1.0, 2.2),
        ("mixed_apnea_rem", 0.53, 6.6),
        ("obstructive_apnea_nonrem", 123.31, 220.0),
        ("central_apnea_nonrem", 7.34, 5.1),
        ("mixed_apnea_nonrem", 2.81, 26.3),
        ("hypopnea_rem", 20.5, 18.4),
        ("hypopnea_nonrem", 123.34, 101.8),
        ("spo2_awake_mean", 91.52, 93.58),
        ("spo2_rem_mean", 90.50, 91.59),
        ("spo2_nonrem_mean", 90.44, 90.86),
        ("odi", 24.21, 35.61),
        ("ess_total", 9.12, 12.20),  # Table 7
    ]
    for col, mm, ff in sex_checks:
        check(f"{col} male mean", m[col].mean(), mm)
        check(f"{col} female mean", f[col].mean(), ff)

    print("=== Table 7: ESS SD ===")
    check("male ESS SD", m["ess_total"].std(), 6.22)
    check("female ESS SD", f["ess_total"].std(), 3.88)


if __name__ == "__main__":
    main()