"""
extract_spv.py — dump all table text from the four SPSS output files.

.spv = zip archive. Table cell text lives in lightTableData.bin but is
usually ALSO present as plain text inside the part's XML (in <text>
elements). This prints every readable string in document order.

Run:  uv run extract_spv.py [Output1|Output2|Output3|Output4|all]
"""

import re
import sys
import zipfile


def dump(path: str, max_items: int = 400) -> None:
    z = zipfile.ZipFile(path)
    parts = sorted(
        (n for n in z.namelist() if n.endswith(".xml") and "outputViewer" in n),
        key=lambda n: int(re.search(r"\d+", n.split("/")[-1]).group(0)),
    )
    for n in parts:
        data = z.read(n).decode("utf8", "ignore")
        texts = re.findall(r">([^<>]{3,300})<", data)
        keep = []
        for t in texts:
            t = t.strip()
            if not t:
                continue
            if t.startswith(("p{", "0000", "<?", "grid", "table", "column", "row", "cell", "text")):
                continue
            if "font" in t or "color" in t or "decoration" in t:
                continue
            keep.append(t)
        if keep:
            print(f"--- {n.split('/')[-1]} ---")
            for t in keep[:max_items]:
                print("   ", t)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    files = (
        ["Output1.spv", "Output2.spv", "Output3.spv", "Output4.spv"]
        if which == "all"
        else [which + ".spv"]
    )
    for f in files:
        print("=" * 25, f, "=" * 25)
        dump("/Users/mahyar/Downloads/" + f)