"""
explore_spv_tables.py — extract the numeric matrices from SPSS .spv tables.

lightTableData.bin stores doubles at 22-byte strides. We scan for doubles
in plausible ranges (correlations |r|<=1, p-values 0..1, means/t-statistics)
and print them with offsets so the matrix structure can be reconstructed.

This one targets Output4.spv (Correlations: AHI total x ...).
Run:  uv run explore_spv_tables.py
"""

import struct
import zipfile

z = zipfile.ZipFile("/Users/mahyar/Downloads/Output4.spv")
raw = z.read("00000000013_lightTableData.bin")

print("doubles with |v|<=1.1 in tail region (correlation table cells):")
for i in range(2300, len(raw) - 8, 22):  # try fixed stride
    v = struct.unpack_from("<d", raw, i)[0]
    if abs(v) <= 1.1:
        print(f"  offset {i}: {v:.4f}")