# FD-Weekend-Sigt

Alle koeien uit de ouwe sloot, gewoon op een rijtje....

## Snel starten

```
python3 scripts/build.py                    # bouwt dist/
python3 -m http.server -d dist 8000         # bekijk op http://localhost:8000
```

Nieuwe versie van de sheet? Zet hem in `data/` en draai:

```
pip install openpyxl
python3 scripts/update_from_sheet.py "data/Overzicht FD Weekenden 1.2.xlsx"
python3 scripts/build.py
```

## Online zetten (Cloudflare Pages)

- Eenmalig: `npx wrangler pages deploy dist --project-name fd-weekend-sigt`, of koppel deze map als GitHub-repo aan Cloudflare Pages met build command `python3 scripts/build.py` en output directory `dist`.
- Daarna ziet iedereen met de link elke nieuwe versie. Op de telefoon: openen in de browser en "Zet op beginscherm".

Zie `CLAUDE.md` voor de opbouw en de afspraken.
