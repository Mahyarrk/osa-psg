import pandas as pd

df = pd.read_excel("data_raw.xlsx", na_values="?")

for col in df.columns:
    vals = df[col].dropna().unique()[:3]
    samples = ", ".join(str(v) for v in vals)
    print(f"{col:12s} | {df[col].notna().sum():3d} values | {samples}")
print(df.dtypes)