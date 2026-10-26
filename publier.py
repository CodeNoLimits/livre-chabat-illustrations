#!/usr/bin/env python3
# Publie les pages validées (dossier LIVRAISON_IMAGES_GEMINI_2026-10-26) sur le site GitHub Pages d'Avraham.
# Ne pousse que si quelque chose a changé. Usage : publier.py
import json, pathlib, re, subprocess, datetime, os
ICI = pathlib.Path(__file__).resolve().parent
PROJET = ICI.parent
LIV = PROJET / "LIVRAISON_IMAGES_GEMINI_2026-10-26"
TITRES = {it["n"]: it["titre"].strip(" .&+") for it in json.load(open(PROJET / "03_DOCS/avraham_dessin_matiere_2026-10-25/correspondance.json"))}
TOTAL = len(list((PROJET / "04_ASSETS/images_v10_grok_2026-10-26/livre/consignes").glob("L*.txt")))
def propre(t):
    t = re.sub(r"\s*\((Talmud|Conte)[^)]*\)?", "", t).strip()
    return t[:1].upper() + t[1:]
pages = []
for src in sorted(LIV.glob("page*.png")):
    m = re.match(r"page(\d+)_", src.name)
    if not m: continue
    n = int(m.group(1)); dst = ICI / "img" / f"page{n:02d}.jpg"
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "86", str(src), "--out", str(dst)], capture_output=True, check=True)
    pages.append({"page": n, "titre": propre(TITRES.get(n, src.stem)), "fichier": dst.name, "v": int(src.stat().st_mtime)})
maj = datetime.datetime.now().strftime("%d/%m à %H:%M")
man = {"total": TOTAL, "maj": maj, "pages": sorted(pages, key=lambda p: p["page"])}
ancien = json.loads((ICI / "manifest.json").read_text()) if (ICI / "manifest.json").exists() else {}
if ancien.get("pages") == man["pages"]:
    print("rien de nouveau"); raise SystemExit
(ICI / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1))
g = lambda *a: subprocess.run(["git", "-C", str(ICI), *a], capture_output=True, text=True)
g("add", "-A"); r = g("commit", "-m", f"Pages illustrées : {len(pages)}/{TOTAL} ({maj})")
p = g("push", "-q", "origin", "HEAD:main")
print(f"{len(pages)}/{TOTAL} pages publiées", "(poussé)" if p.returncode == 0 else f"ÉCHEC push : {p.stderr[:200]}")
