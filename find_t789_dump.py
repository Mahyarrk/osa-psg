"""
inspect_t789.py — Output3 table 00000000234 has t=-7.922 on q30/q31.
Dump that table's full numeric content to see exactly what SPSS computed
(the candidate for thesis Table 13's t=7.89).

Run:  uv run find_t789.py 2>/dev/null (context) then this file.
"""

import re
import struct
import zipfile

z = zipfile.ZipFile("/Users/mahyar/Downloads/Output3.spv")
raw = z.read("00000000234_lightTableData.bin")

runs = [r.decode() for r in re.findall(rb"[\x20-\x7e]{3,}", raw)]
keep = [
    s for s in runs
    if not s.startswith(("SansSerif", "#", "Default", "en_US", "windows", "XXX", "-,,,", ".,-C"))
]
print("text runs:")
for s in keep[:40]:
    print("  ", s)

print("\ndoubles:")
vals = []
for i in range(0, len(raw) - 8):
    v = struct.unpack_from("<d", raw, i)[0]
    if v != 0 and abs(v) < 1e7 and abs(v) > 1e-4:
        vals.append((i, round(v, 3)))
for x in vals:
    print("  ", x)