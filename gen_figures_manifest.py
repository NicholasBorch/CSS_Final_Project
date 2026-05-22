"""
gen_figures_manifest.py
-----------------------
Scans project_data/figures/<subfolder>/ and writes `figures.js` next to index.html.
Run from the repo root, or paste into a notebook cell. Re-run after adding figures.

It also detects a DECADE token in each filename (e.g. network_1960s.png -> "1960s").
Figures with a decade power (a) the per-section decade toggle and (b) the global
"Explore by decade" view. Files with no decade token show as ordinary figures.
"""
import os, re, json

FIG_DIR = "project_data/figures"     # adjust if needed
OUT     = "figures.js"
IMG_EXT = (".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp")

SECTIONS = [
    ("stats",                "Basic statistics"),
    ("network",              "The collaboration network"),
    ("part1",                "Part 1 — The globalisation gap"),
    ("brokers",              "Brokers & corridors"),
    ("fingerprints",         "Part 2 — National fingerprints"),
    ("communities_thematic", "Part 3 — Thematic communities"),
    ("communities_collab",   "Part 3 — Collaboration communities"),
    ("bridge",               "Part 4 — Bridging the lenses"),
]

# matches 1920 / 1920s / 1960 / 2000 / 2020s ... -> canonical "1920s"
DECADE_RE = re.compile(r'(?<!\d)((?:18|19|20)\d0)s?(?!\d)')

def detect_decade(name):
    m = DECADE_RE.search(name)
    return f"{m.group(1)}s" if m else None

def pretty(name):
    base = os.path.splitext(name)[0].replace("_", " ").replace("-", " ").strip()
    return base[:1].upper() + base[1:] if base else name

def figures_in(folder):
    d = os.path.join(FIG_DIR, folder)
    if not os.path.isdir(d):
        return []
    out = []
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(IMG_EXT):
            continue
        item = {"src": f"{FIG_DIR}/{folder}/{f}".replace("\\", "/"), "caption": pretty(f)}
        dec = detect_decade(f)
        if dec:
            item["decade"] = dec
        out.append(item)
    return out

sections, seen, all_decades = [], set(), set()
def add(folder, title):
    figs = figures_in(folder)
    if figs:
        sections.append({"id": folder, "title": title, "figures": figs})
        seen.add(folder)
        for f in figs:
            if f.get("decade"):
                all_decades.add(f["decade"])

for folder, title in SECTIONS:
    add(folder, title)
if os.path.isdir(FIG_DIR):
    for folder in sorted(os.listdir(FIG_DIR)):
        if folder not in seen and os.path.isdir(os.path.join(FIG_DIR, folder)):
            add(folder, pretty(folder))

decades = sorted(all_decades, key=lambda d: int(d[:4]))
manifest = {"sections": sections, "decades": decades}

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("const FIGURES = " + json.dumps(manifest, indent=2, ensure_ascii=False) + ";\n")

n_fig = sum(len(s["figures"]) for s in sections)
n_dec = sum(1 for s in sections for f in s["figures"] if f.get("decade"))
print(f"Wrote {OUT}: {n_fig} figures ({n_dec} decade-tagged) across {len(sections)} sections.")
print(f"Decades found: {decades or '(none — no decade tokens in filenames)'}")
for s in sections:
    d = sorted({f['decade'] for f in s['figures'] if f.get('decade')}, key=lambda x:int(x[:4]))
    print(f"  · {s['title']:<38} {len(s['figures'])} figs  {('decades '+','.join(d)) if d else ''}")
