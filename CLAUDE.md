# FD-Weekend-Sigt: instructies voor Claude Code

Webapp met een overzicht van alle FD-weekenden weg (2000 tot nu). Eigenaar: Patrick Mingaars.
De app is in het Nederlands; antwoord Patrick in het Nederlands.
Ondertitel: "Alle koeien uit de ouwe sloot, gewoon op een rijtje....".

## Opbouw

```
src/app.html          De hele app: HTML, CSS en JavaScript in één bestand
src/data.json         Deelnemers en weekenden (wordt in app.html ingebakken)
src/mapdata.json      Benelux-kaart: contouren, coördinaten van locaties en woonplaatsen
src/snap.json         Welke foto bij wie/wat hoort: {av:{persoonId:fotoId}, ph:{locatieKey:[fotoId,bron]}, ga:{editie:[[fotoId,bron],...]}}
public/img/<id>.jpg   Alle foto's (avatars, huizen, collages), max 1000 px
public/               Verder: PWA-iconen, manifest.webmanifest, _headers (noindex)
data/*.xlsx           De bron-sheet "Overzicht FD Weekenden 1.2.xlsx"
data/overrides.json   Handmatige aanvullingen die niet in de sheet staan (per editie; bv. anek_extra)
scripts/build.py      Bouwt dist/ (index.html met alles ingebakken, plus public/)
scripts/update_from_sheet.py   Werkt src/data.json bij vanuit de sheet
dist/                 Bouwresultaat; niet handmatig aanpassen
```

`app.html` bevat de markers `/*DATA*/null`, `/*MAP*/null` en `/*SNAP*/null`. Die vervangt build.py door de JSON-bestanden.

## Werkwijze

1. Pas `src/` aan (of zet een nieuwe sheet in `data/` en draai `python3 scripts/update_from_sheet.py`).
2. `python3 scripts/build.py`
3. Bekijk `dist/index.html` lokaal (bijvoorbeeld `python3 -m http.server -d dist`), ook op telefoonformaat (390 px breed).
4. Publiceren: commit en push naar `main` op GitHub (pmingaar/FD-Weekend-Sigt). Cloudflare (Workers & Pages, project `fd-weekend-sigt`) bouwt en publiceert dan automatisch.

Live adres: https://fd-weekend-sigt.patrick-7f3.workers.dev

## Data (src/data.json)

- `people[]`: `id, name, full, town, kid, born` (born = JJJJ-MM-DD, niet bij iedereen bekend).
- `weekends[]`: `ed, year, kids, cancelled, place, loc, web, org, act, anek, att{persoonId: 1 of 0.5}, datum` (tekst uit de sheet) en `date` (de zaterdag, JJJJ-MM-DD).
  Extra's per weekend, niet uit de sheet maar opgezocht:
  - `wx`: weer vr/za/zo op de locatie (Open-Meteo archive API).
  - `top40`: nummer 1 van de Top 40 die week (top40.nl).
  - `news`/`newsSrc`: 1 tot 3 nieuwsitems (NOS, nu.nl, AD, nl.wikipedia-maandoverzicht).
  - `stand`: Eredivisie-stand van Ajax, Feyenoord en ADO op de vrijdag van het weekend, berekend uit de uitslagen van football-data.co.uk (`/mmz4281/{seizoen}/N1.csv`). Vorm: `{season, final, abort?, ajax:[plek,punten,wedstrijden], fey:[...], ado:[...]|null}`; `null` = ADO speelde in de Keuken Kampioen Divisie. Juni-weekenden vallen na de laatste speelronde.
- Een weekend met een `date` in de toekomst toont als "binnenkort"-kaart en telt niet mee in ranglijst, kaart en km.

## Regels in de sheet

- Eerste weekend van het jaar is altijd het 2e weekend van juni, het tweede het 2e/3e weekend van november. Vanaf nov 2019 staan er exacte datums in.
- Onder de weekendtabel staat een herhaalde namenrij met daaronder de geboortedata.
- Correcties die de app toepast: editie 30 jaar 2121 → 2021; editie 40 heet "De Vilt" (niet "De Zilt"); de twee Charlottes heten in de sheet nu Charlotte vd Heinen (id `charlotte-vd-heinen`) en Charlotte Kleipool (`charlotte-kleipool`). Editie 1 (2000) is Gerritsen (moeder Jehee) in Putte (Woensdrecht, recreatiecentrum Hazeduinen); weer opnieuw opgehaald voor Putte.
- De SUM-formules in rij 2 van de sheet lopen tot het einde van de kolom en tellen daardoor de geboortedata mee; dat is een sheetprobleem, niet van de app.

## Functies in de app

Avatar per deelnemer (foto, anders initialen), "Ranking the FD-ers" (half aanwezig = 0,5), filters op persoon, jaar, editie, soort weekend en locatie, klikbare tijdlijn, Benelux-kaart met km vanaf woonplaats, per weekend: huisfoto, organisatie, activiteit, aanwezigen, gemiddelde leeftijd, albumlink, fotocollage, "Dat weekend" (weer, Top 40, voetbalstand, nieuws), anekdote als animatie met "Voor het laatst mee" (niet voor de laatste 2 gehouden weekenden), de Inge Venema-contest (knop met foto van Inge Venema, LinkedIn-connectie van Patrick; Inge zelf is "PNIV (Precies Niveau Inge Venema)"; klik toont 3 willekeurig getekende, verzonnen blonde dames (SVG, geen echte personen en geen FD-dames) met verzonnen namen, per tekening BIV of OIV kiezen, uitslag altijd 10 punten en gewonnen; Inge kent de grap), een verjaardagskalender (deze en volgende maand, knop "Verder" voor de rest, .ics-download voor de agenda), een blok met Spotify-playlists, en bij elk weekend waar Annet (Annie) mee was "Was Annie de weg kwijt?" (Heenweg / Terugreis / Zowel heen- als terugreis / Nee, ze reed met Bossie mee; vaste willekeurige keuze per editie, of een vast antwoord via `annie` in data/overrides.json).
Er is bewust geen mogelijkheid om via de app zelf anekdotes of media toe te voegen.

## Afspraken

- Getekende/cartoon-avatars zijn niet gewenst: gebruik echte foto's.
- Richards avatar is een uitsnede uit de Diever-selfie (editie 27); Patrick staat rechts op die foto.
- Gebruik geen officiële clublogo's; de badges in clubkleuren blijven.
- Geen foto's van kinderen in ongepaste situaties; twijfel je over wie er op een foto staat, vraag het.
- Typ nooit wachtwoorden; Patrick logt zelf in.
- Vraag eerst voordat je bestanden verwijdert.

## Nog open

- Geen huisfoto: Putte (2000), Ardennen, Hunzepark.
- Nog geen avatar: deelnemers met alleen een voornaam en de meeste kids.
- 15 deelnemers zonder geboortedatum (aanvullingen buiten de sheet staan in data/overrides.json onder "_people").
- Editie 41 (20 tot 22 nov 2026, Larikshoeve Leusden) is ingevuld op 21 nov: weer zondag is nog een verwachting (later vervangen door archiefdata), stand na 12 speelrondes 2026/27 (ADO weer in de Eredivisie, 17e). Annie-antwoord vast via overrides (`annie`).
- Volgende weekend: na afloop aanwezigen uit de sheet, dan `wx`, `top40`, `news` en `stand` opzoeken.
