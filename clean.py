"""
clean.py — load raw data, apply exclusions, output the analysis dataset.

Pipeline:
  1. read raw xlsx, telling pandas that "?" means missing
  2. strip whitespace from column names (q28/q29 had trailing spaces)
  3. drop dead columns
  4. rename q-columns to real names (rename_map.py)
  5. mark the 13 excluded patients with a reason
  6. save two files:
       data_clean.csv       -> all 55 rows, exclusion flag + reason included
       data_included.csv    -> the 42 thesis patients only
Run:  uv run clean.py
"""

import pandas as pd

from rename_map import RENAME_MAP, DEAD_COLUMNS

RAW_FILE = "data_raw.xlsx"
CLEAN_ALL = "data_clean.csv"
CLEAN_INCLUDED = "data_included.csv"

# ---------------------------------------------------------------
# Exclusion list (13 patients).
# Sources:
#   - final_impression labels  (5 nl, 4 upper, 1 primary snoring)
#   - referral_reason text     (2 narcolepsy, 1 convulsion)
#   - statistical identification (1 parasomnia: Asghar Chegini —
#     the only candidate whose removal reproduces thesis Tables 1+2
#     exactly: age 45.13±9.387, BMI 30.09±4.83, and Table 3 counts)
# How to use: each entry is a name fragment -> reason. Matching is
# case-insensitive on purpose (names are inconsistently typed).
# ---------------------------------------------------------------
EXCLUSIONS = {
    # labeled in final_impression
    "Yousef Hasanpour":       "normal (nl)",
    "Hosna Jahan Shahsavari": "normal (nl)",
    "Hamid Afshar":           "normal (nl)",
    "Mahmood Hoseinzadeh":    "normal (nl) + narcolepsy referral",
    "Parvin Sohrabi":         "normal (nl)",
    "Jafar Ghanbari":         "upper airway obstruction",
    "Yoosefali Fathi":        "upper airway obstruction",
    "Mohammad Pourhosain Asli": "upper airway obstruction",
    "Mohammad Moradi":        "upper airway obstruction",
    "maryam khosravi":        "primary snoring",
    # referral text
    "Mohamadhosein Fazel":    "narcolepsy (referral reason)",
    "Farhad Sedighi":         "convulsion (referral reason)",
    # statistical identification (see git history for the derivation)
    "Asghar Chegini":         "parasomnia (inferred from thesis stats)",
}


def load_clean(path: str = RAW_FILE) -> pd.DataFrame:
    """Raw xlsx -> tidy dataframe with real column names, all 55 rows."""
    df = pd.read_excel(path, na_values="?")
    df.columns = df.columns.str.strip()          # 'q28 ' -> 'q28'
    df = df.drop(columns=DEAD_COLUMNS)
    df = df.rename(columns=RENAME_MAP)
    df["patient_name"] = df["patient_name"].str.strip()

    # exclusion flag + reason
    df["excluded"] = False
    df["exclusion_reason"] = ""
    for fragment, reason in EXCLUSIONS.items():
        mask = df["patient_name"].str.contains(fragment, case=False, na=False, regex=False)
        df.loc[mask, ["excluded", "exclusion_reason"]] = [True, reason]

    # sex as a readable category (keep the code too, thesis uses 1/2)
    df["sex_label"] = df["sex"].map({1: "male", 2: "female"})

    return df


def main() -> None:
    df = load_clean()

    included = df[~df["excluded"]].copy()

    df.to_csv(CLEAN_ALL, index=False)
    included.to_csv(CLEAN_INCLUDED, index=False)

    # ---- sanity report ----
    n_m = (included["sex"] == 1).sum()
    n_f = (included["sex"] == 2).sum()
    print(f"all rows       : {len(df)}")
    print(f"excluded       : {df['excluded'].sum()}  (thesis says 13)")
    print(f"included       : {len(included)}  (thesis says 42)")
    print(f"  males        : {n_m}  (thesis says 32)")
    print(f"  females      : {n_f}  (thesis says 10)")
    print(f"written: {CLEAN_ALL}, {CLEAN_INCLUDED}")


if __name__ == "__main__":
    main()