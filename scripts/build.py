#!/usr/bin/env python3
"""Bouwt dist/ : één index.html (app + data ingebakken) plus foto's en PWA-bestanden.

Gebruik:  python3 scripts/build.py
Daarna staat de complete site in dist/ (klaar voor Cloudflare Pages).
"""
import json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, PUB, DIST = ROOT / "src", ROOT / "public", ROOT / "dist"

HEAD = ('<link rel="manifest" href="manifest.webmanifest">'
        '<link rel="apple-touch-icon" href="icon-180.png">'
        '<meta name="theme-color" content="#1f5a40">'
        '<meta name="apple-mobile-web-app-capable" content="yes">'
        '<meta name="apple-mobile-web-app-title" content="FD-Sigt">')

def main():
    app = (SRC / "app.html").read_text(encoding="utf-8")
    data = (SRC / "data.json").read_text(encoding="utf-8")
    json.loads(data)  # controle: geldige JSON
    data = data.replace("</", "<\\/")  # voorkomt dat '</script>' in tekst de pagina breekt
    mapd = (SRC / "mapdata.json").read_text(encoding="utf-8")
    snap = (SRC / "snap.json").read_text(encoding="utf-8")
    for marker in ("/*DATA*/null", "/*MAP*/null", "/*SNAP*/null"):
        assert marker in app, f"marker {marker} ontbreekt in app.html"
    html = (app.replace("/*DATA*/null", data)
               .replace("/*MAP*/null", mapd)
               .replace("/*SNAP*/null", snap))

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(PUB, DIST)
    (DIST / "index.html").write_text(html.replace("</head>", HEAD + "</head>", 1), encoding="utf-8")

    # controle: bestaan alle foto's waar snap.json naar verwijst?
    s = json.loads(snap)
    ids = set(s.get("av", {}).values()) | {v[0] for v in s.get("ph", {}).values()} \
        | {g[0] for v in s.get("ga", {}).values() for g in v}
    missing = [i for i in ids if not (DIST / "img" / f"{i}.jpg").exists()]
    if missing:
        print("LET OP: ontbrekende foto's in public/img:", missing)
    print(f"Klaar: {DIST/'index.html'} ({len(html)//1024} kB), {len(ids)} foto's gekoppeld")

if __name__ == "__main__":
    main()
