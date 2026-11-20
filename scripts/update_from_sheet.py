"""Werkt src/data.json bij vanuit de sheet.

Gebruik:  python3 scripts/update_from_sheet.py "data/Overzicht FD Weekenden 1.2.xlsx"

Neemt uit de sheet: edities, plaats, locatie, website, organisatie, activiteit,
anekdote, aanwezigheid en geboortedata (rij onder de herhaalde namenrij).
Behoudt uit de bestaande data.json: datum (date), weer (wx), Top 40, nieuws,
voetbalstand, volledige namen en woonplaatsen. Nieuwe weekenden krijgen die
extra's NIET automatisch; zie CLAUDE.md.
"""
import openpyxl, json, sys, datetime
from pathlib import Path
OUT=Path(__file__).resolve().parent.parent/'src'/'data.json'
from openpyxl.utils import column_index_from_string as ci
wb=openpyxl.load_workbook(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parent.parent/'data'/'Overzicht FD Weekenden 1.2.xlsx',data_only=True); ws=wb['Allen']
hdr=[c.value for c in ws[1]]; hdr=[hdr[0]]+hdr[2:]
adult=range(ci('M')-1, ci('AN')); kid=range(ci('AP')-1, ci('BE'))
full={'Dirk':('Dirk Heessels','Den Haag'),'Suus':('Susanne Schippers','Den Haag'),'Aimée':('Aimée Schippers','Den Haag'),'Duco':('Duco Schippers','Den Haag'),
'Victor':('Victor Lamboo','Den Haag'),'Lizzy':('Lizzy Lamboo','Den Haag'),'Lucas':('Lucas Lamboo','Den Haag'),'Mark':('Mark Jehee','Leidschendam'),
'Anneke':('Anneke Jehee','Leidschendam'),'Niels':('Niels Jehee','Leidschendam'),'Luc':('Luc Jehee','Leidschendam'),'Patrick':('Patrick Mingaars','Voorburg'),
'Marije':('Marije de Wit','Voorburg'),'Pepijn':('Pepijn Mingaars','Voorburg'),'Faber':('Faber Mingaars','Voorburg'),'Linde':('Linde Mingaars','Voorburg'),
'Wendy':('Wendy Ruijgrok','Berkel en Rodenrijs'),'René':('René van Loenen','Berkel en Rodenrijs'),'Vera':('Vera van Loenen','Berkel en Rodenrijs'),'Tijs':('Tijs van Loenen','Berkel en Rodenrijs'),
'Henk':('Henk Nulkes','Maarssen'),'Jesse':('Jesse Nulkes','Maarssen'),'Martijn':('Martijn Boss','Heemstede-Aerdenhout'),'Annet':('Annet Beentjes','Heemstede-Aerdenhout'),
'Nout':('Nout Boss','Heemstede-Aerdenhout'),'Roos':('Roos Boss','Heemstede-Aerdenhout'),'Alice':('Alice van Zurk','Alphen aan de Rijn'),'Richard':('Richard Vons','Alphen aan de Rijn'),
'Tim':('Tim Vons','Alphen aan de Rijn'),'Lars':('Lars Vons','Alphen aan de Rijn')}
people=[];seen={}
IDS={}  # eventueel vaste ids per kolomnaam, bv. {'Naam in sheet':'id'}
def key(n):
    if n in IDS: return IDS[n]
    import unicodedata
    k=unicodedata.normalize('NFKD',n).encode('ascii','ignore').decode().lower().replace(' ','-')
    if k in seen: seen[k]+=1; k=f"{k}-{seen[k]}"
    else: seen[k]=1
    return k
cols=[]
for i in list(adult)+list(kid):
    n=hdr[i].strip(); k=key(n); f,w=full.get(n,(n,''))
    people.append(dict(id=k,name=n,full=f,town=w,kid=i in kid)); cols.append(i)
people0=list(people)
for p in people:
    if p['name']=='Charlotte': p['full']='Charlotte' + (' (1)' if p['id']=='charlotte' else ' (2)'); p['name']=p['full']
weekends=[]
for r in ws.iter_rows(min_row=3, values_only=True):
    if r[0] is None and r[2] is None: break  # einde weekendtabel (daaronder: geboortedata)
    datum=r[1]; r=(r[0],)+tuple(r[2:])
    if r[1] is None: continue
    ed,yr,kids,plaats,loc,web,org,act,anek=r[:9]
    if plaats and 'Geannuleerd' in str(plaats):
        weekends.append(dict(ed=None,year=yr,kids=False,cancelled=True,place='Geannuleerd (corona)',loc='',web='',org='',act='',anek='',att={},datum=None));continue
    if yr==2121: yr=2021
    clean=lambda v: None if v in (None,'?','=') else str(v).strip()
    web=clean(web)
    if web and not web.startswith('http'): web='https://www.camping-drenthe.nl' if 'camping-drenthe' in web else None
    att={}
    for p,i in zip(people,cols):
        v=r[i]
        if isinstance(v,(int,float)) and v>0: att[p['id']]=v
    weekends.append(dict(ed=ed,year=yr,kids=kids=='Y',cancelled=False,place=clean(plaats),loc=clean(loc),web=web,org=clean(org),act=clean(act),anek=clean(anek),att=att,datum=(str(datum).strip() if datum else None)))
used={k for w in weekends for k in w['att']}
people=[p for p in people if p['id'] in used]

# geboortedata: rij direct onder een herhaalde namenrij
names_row=None
for row in ws.iter_rows(min_row=3):
    vals=[c.value for c in row]
    if vals[0] is None and any(isinstance(v,str) and v.strip()=='Mark' for v in vals[10:16]):
        names_row=row[0].row
if names_row:
    raw=[c.value for c in ws[names_row+1]]; raw=[raw[0]]+raw[2:]
    pid=dict(zip([p['id'] for p in people0],cols))
    for p in people:
        v=raw[pid[p['id']]]
        if isinstance(v,datetime.datetime): p['born']=v.date().isoformat()

# samenvoegen met bestaande data
old=json.load(open(OUT,encoding='utf-8')) if OUT.exists() else {'people':[],'weekends':[]}
op={p['id']:p for p in old['people']}
for p in people:
    o=op.get(p['id'])
    if o:
        for k in ('name','full','town'):
            if o.get(k): p[k]=o[k]
oe={(w.get('ed'),w.get('year')):w for w in old['weekends']}
KEEP=('date','wx','top40','news','newsSrc','stand')
for i,w in enumerate(weekends):
    o=oe.get((w['ed'],w['year'])) or (old['weekends'][i] if i<len(old['weekends']) else None)
    if o:
        for k in KEEP:
            if k in o: w[k]=o[k]
    if w['ed']==40: w['loc']='De Vilt'  # handmatige correctie
    if not w.get('date') and not w['cancelled']:
        print('LET OP: geen datum (date) voor editie',w['ed'],w['year'],repr(w.get('datum')),'- vul handmatig in als JJJJ-MM-DD (de zaterdag)')
# handmatige aanvullingen (data/overrides.json)
OV=Path(__file__).resolve().parent.parent/'data'/'overrides.json'
if OV.exists():
    ov=json.load(open(OV,encoding='utf-8'))
    for w in weekends:
        o=ov.get(str(w['ed']))
        if not o: continue
        if o.get('anek_extra'):
            w['anek']=((w.get('anek') or '').rstrip('. ')+'. '+o['anek_extra']).lstrip('. ')
        for k,v in o.items():
            if k!='anek_extra': w[k]=v
json.dump(dict(people=people,weekends=weekends),open(OUT,'w',encoding='utf-8'),ensure_ascii=False)
print(len(people),'deelnemers,',len(weekends),'weekenden,',sum(1 for p in people if p.get('born')),'geboortedata ->',OUT)
