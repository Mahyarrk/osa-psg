"""
list_spv_procedures.py — list every procedure in each SPV file, so we know
which output file holds the Table 13 test (the t=7.89 question).

Run:  uv run list_spv_procedures.py
"""

import re
import zipfile
from collections import Counter

for f in ["Output1.spv", "Output2.spv", "Output3.spv", "Output4.spv"]:
    z = zipfile.ZipFile("/Users/mahyar/Downloads/" + f)
    heads = sorted(
        (n for n in z.namelist() if n.endswith("_heading.xml")),
        key=lambda s: int(re.search(r"\d+", s.split("/")[-1]).group(0)),
    )
    titles = []
    for n in heads:
        data = z.read(n).decode("utf8", "ignore")
        m = re.findall(r">([A-Za-z][A-Za-z0-9 ()-]{2,40})<", data)
        titles.append(m[1] if len(m) > 1 else (m[0] if m else "?"))
    print(f, dict(Counter(titles)))