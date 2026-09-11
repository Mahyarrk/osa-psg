"""
rename_map.py — the single source of truth for column names.

Every analysis script imports RENAME_MAP from here, so if we ever
rename a variable, we change it in ONE place, not five.

Naming convention: short snake_case, unit or stage suffix where needed.
REM/non-REM suffixes follow the thesis table wording.
"""

RENAME_MAP = {
    "n": "patient_name",
    # --- demographics ---
    "q1": "sex",              # 1 = male, 2 = female
    "q2": "age_years",
    "q3": "height_cm",
    "q4": "weight_kg",
    "q5": "bmi",
    # --- history / referral ---
    "q8": "mallampati_score",
    "q9": "referral_reason",
    "q10": "comorbidities",
    # --- symptoms (1 = no, 2 = yes) ---
    "q11": "snoring",
    "q12": "apnea_feeling",
    "q13": "night_sweats",
    "q14": "morning_headache",
    "q15": "poor_concentration",
    "q16": "mva_history",          # motor-vehicle accident
    "q17": "sleep_talking",
    "q18": "night_terrors",
    "q19": "sleepwalking",
    "q20": "sleep_attacks",
    "q21": "sleep_paralysis",
    "q22": "hypnotic_use",
    # --- PSG: basic architecture ---
    "q24": "tst_min",              # total sleep time
    "q25": "sleep_latency_min",
    "q26": "awakenings_count",
    "q27": "sleep_efficiency_pct",
    "q28": "arousal_index",
    "q29": "plms_index",
    "q30": "ahi_rem",
    "q31": "ahi_nonrem",
    # --- PSG: event counts (raw counts, not rates) ---
    "q32": "obstructive_apnea_rem",
    "q33": "central_apnea_rem",
    "q34": "mixed_apnea_rem",
    "q38": "hypopnea_rem",
    "q35": "obstructive_apnea_nonrem",
    "q36": "central_apnea_nonrem",
    "q37": "mixed_apnea_nonrem",
    "q39": "hypopnea_nonrem",
    # --- PSG: oxygenation ---
    "q40": "spo2_awake_mean",
    "q41": "spo2_rem_mean",
    "q42": "spo2_nonrem_mean",
    "q43": "odi",                  # oxygen desaturation index
    # --- questionnaire ---
    "q44": "ess_total",            # Epworth Sleepiness Score
    # --- final impression (free text: nl / upper / primary snoring) ---
    "Unnamed: 46": "final_impression",
}

# Columns that exist in the raw sheet but carry no data -> dropped on load.
DEAD_COLUMNS = ["Unnamed: 0", "q6", "q7", "q23"]

# Symptom yes/no columns, for coding (1 = no, 2 = yes -> later bool)
SYMPTOM_COLUMNS = [
    "snoring", "apnea_feeling", "night_sweats", "morning_headache",
    "poor_concentration", "mva_history", "sleep_talking", "night_terrors",
    "sleepwalking", "sleep_attacks", "sleep_paralysis", "hypnotic_use",
]