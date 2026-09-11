import pandas as pd

# Load the raw PSG spreadsheet
df = pd.read_excel("data_raw.xlsx")

# Shape: rows x columns
print("shape:", df.shape)

# First 3 rows, first 8 columns only (raw peek)
print(df.iloc[:3, :8])

# How many missing-ish values per column
print(df.isin(["?", "null", "Null", None]).sum())
