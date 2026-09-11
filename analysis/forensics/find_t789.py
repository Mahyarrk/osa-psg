"""
find_t789.py — search every T-Test / Oneway / GLM table in the SPV files
for a t-value near 7.89, to find exactly which SPSS procedure produced it.

Run:  uv run find_t789.py
"""

import re
import struct
import zipfile

FILES = ["Output1.spv", "Output2.spv", "Output3.spv", "Output4.spv"]


def scan_tables(path: str) -> None:
    z = zipfile.ZipFile(path)
    tables = sorted(
        (n for n in z.namelist() if "lightTableData" in n),
        key=lambda s: int(re.search(r"\d+", s.split("/")[-1]).group(0)),
    )
    for n in tables:
        raw = z.read(n)
        hits = []
        for i in range(0, len(raw) - 8):
            v = struct.unpack_from("<d", raw, i)[0]
            if 6.5 < abs(v) < 9.5:  # hunting t≈7.89
                hits.append((i, round(v, 3)))
        if hits:
            # identify the table's variables from string runs
            runs = re.findall(rb"[\x20-\x7e]{3,}", raw)
            names = [
                r.decode() for r in runs
                if re.fullmatch(rb"q\d+ ?|AHItotal|ODI|arousal|REM|NREM", r)
            ]
            print(f"{path} :: {n} :: vars~{names[:8]} :: hits {hits}")


if __name__ == "__main__":
    for f in FILES:
        scan_tables("/Users/mahyar/Downloads/" + f)