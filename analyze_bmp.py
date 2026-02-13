"""
Analyze .bmp image files in the TrentinGrana directory structure.
"""
import os
import re
from collections import Counter, defaultdict

BASE = r"c:\Users\nicol\Desktop\CheeseCaptioningAIFQC\07_captioning risultati grana Trentino\TrentinGrana"

YEAR_DIRS = [
    "2018-2019_Trentingrana",
    "2019-2020_Trentingrana",
    "2020-2021_Trentingrana",
    "2021-2022_Trentingrana",
]

# -- Collect all .bmp files per year --
files_by_year = {}
for yd in YEAR_DIRS:
    year_path = os.path.join(BASE, yd)
    bmp_files = []
    for root, dirs, fnames in os.walk(year_path):
        for f in fnames:
            if f.lower().endswith(".bmp"):
                bmp_files.append(f)
    files_by_year[yd] = sorted(bmp_files)

# 1. Total count
total = sum(len(v) for v in files_by_year.values())
print("=" * 80)
print(f"  TOTAL .bmp FILES: {total}")
print("=" * 80)

# 2. Count per year
print("\n-- COUNT PER YEAR DIRECTORY --")
for yd in YEAR_DIRS:
    print(f"  {yd:40s}  {len(files_by_year[yd]):>5d} files")

# 3. Example filenames from each year
print("\n-- EXAMPLE FILENAMES (up to 8 per year) --")
for yd in YEAR_DIRS:
    print(f"\n  [{yd}]")
    for fname in files_by_year[yd][:8]:
        print(f"    {fname}")
    if len(files_by_year[yd]) > 8:
        print(f"    ... and {len(files_by_year[yd]) - 8} more")

# 4. Identify naming patterns / suffixes
print("\n-- NAMING PATTERN ANALYSIS --")

all_files = []
for flist in files_by_year.values():
    all_files.extend(flist)

keyword_counter = Counter()
suffix_counter = Counter()

for f in all_files:
    name = os.path.splitext(f)[0]
    for kw in ["GRANA", "FETTA", "FORMA", "CROSTA", "PASTA", "OCCHIATURA"]:
        if kw in name.upper():
            keyword_counter[kw] += 1
    m = re.search(r'_([A-Z])$', name, re.IGNORECASE)
    if m:
        suffix_counter[f"_{m.group(1).upper()}"] += 1

print("\n  Keywords found in filenames:")
for kw, cnt in keyword_counter.most_common():
    print(f"    {kw:20s} -> {cnt:>5d} files")

print("\n  Single-letter suffixes (_A, _B, ...) at end of filename:")
for sf, cnt in sorted(suffix_counter.items()):
    print(f"    {sf:20s} -> {cnt:>5d} files")

# Broader pattern detection
pattern_examples = defaultdict(list)
for f in all_files:
    name = os.path.splitext(f)[0]
    pattern = re.sub(r'\d+', '#', name)
    if len(pattern_examples[pattern]) < 2:
        pattern_examples[pattern].append(f)

pattern_freq = Counter()
for f in all_files:
    name = os.path.splitext(f)[0]
    pattern = re.sub(r'\d+', '#', name)
    pattern_freq[pattern] += 1

print(f"\n  Top naming patterns (digits replaced with #):")
for pat, cnt in pattern_freq.most_common(15):
    examples = pattern_examples[pat]
    print(f"    Pattern: {pat}")
    print(f"      Count: {cnt}   Examples: {examples}")

# 5. Sessions (Seduta) per year
print("\n-- SESSIONS (Seduta) PER YEAR --")
for yd in YEAR_DIRS:
    sedute = set()
    for f in files_by_year[yd]:
        m = re.search(r'Seduta[_ ]?(\d+)', f, re.IGNORECASE)
        if m:
            sedute.add(int(m.group(1)))
    sedute_sorted = sorted(sedute)
    print(f"\n  [{yd}]")
    print(f"    Number of distinct Seduta values: {len(sedute_sorted)}")
    if sedute_sorted:
        print(f"    Seduta numbers: {sedute_sorted}")

# Also show subdirectory structure
print("\n-- SUBDIRECTORY STRUCTURE (Seduta folders) --")
for yd in YEAR_DIRS:
    year_path = os.path.join(BASE, yd)
    subdirs = []
    for item in sorted(os.listdir(year_path)):
        full = os.path.join(year_path, item)
        if os.path.isdir(full):
            bmp_count = sum(1 for _, _, fns in os.walk(full) for fn in fns if fn.lower().endswith('.bmp'))
            subdirs.append((item, bmp_count))
    print(f"\n  [{yd}]  ({len(subdirs)} subdirectories)")
    for sd, bc in subdirs:
        print(f"    {sd:50s}  {bc:>4d} .bmp files")

print("\n" + "=" * 80)
print("  ANALYSIS COMPLETE")
print("=" * 80)
