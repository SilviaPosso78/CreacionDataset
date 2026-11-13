from pathlib import Path
import csv, calendar, re, zipfile
base = Path(__file__).parent / 'datos'
def ideam(y):
    p = base / f'ideam_aldea_{y}.zip'
    with zipfile.ZipFile(p) as z:
        name = next(n for n in z.namelist() if n.endswith('.csv'))
        rows = list(csv.DictReader(z.read(name).decode('utf-8-sig').splitlines()))
    return rows
def mexico(id_):
    rows = {}
    for line in (base / f'mexico_{id_}_diarios.txt').read_text(encoding='utf-8-sig').splitlines():
        if re.match(r'^\d{4}-\d{2}-\d{2}\t', line):
            a = line.split('\t')
            assert a[0] not in rows
            def num(s):
                try: return float(s)
                except ValueError: return None
            rows[a[0]] = dict(precipitacion_mm=num(a[1]), tmax_c=num(a[3]))
    return rows
if __name__ == '__main__':
    mx = {i: mexico(i) for i in ['15266', '09048']}
    for p in sorted(base.glob('ideam_aldea_????.zip'), reverse=True):
        y = int(p.stem[-4:]); rows = ideam(y)
        print(y, {k: sum(r['Parametro']==k for r in rows) for k in {r['Parametro'] for r in rows}})
        for id_, m in mx.items():
            good = [f for f,r in m.items() if f.startswith(str(y)) and all(v is not None for v in r.values())]
            print('  México', id_, len(good), 'válidos /', 366 if calendar.isleap(y) else 365)
