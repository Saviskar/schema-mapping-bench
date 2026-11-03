"""03 - Daily warehouse stock snapshots: zeros for missing, missing days/sites, sentinel values, unit drift."""
import random, datetime as dt
from collections import Counter
from common import *

F = '03_warehouse_stock_daily__zeros_for_missing_gaps_suspicious_values.csv'
rng = random.Random(303)
COLS = ['date', 'wh', 'sku', 'desc', 'oh', 'inb', 'out', 'rop', 'counted', 'counter']
HDR = ['snapshot_date', 'WH', 'SKU', 'Item Description', 'On Hand', 'Inbound', 'Outbound', 'Reorder Lvl', 'last_counted', 'Counted By']
CI = {c: i + 1 for i, c in enumerate(COLS)}
SKUS = ['Coconut Oil 1L', 'White Sugar 1kg', 'Red Lentils (Dhal) 1kg', 'Basmati Rice 5kg', 'Wheat Flour 1kg',
        'Milk Powder 400g', 'Canned Fish 425g', 'Soya Meat 90g', 'Ceylon Black Tea 400g', 'Dishwash Liquid 500ml',
        'Laundry Soap Bar', 'Toilet Paper 10pk', 'Biscuits Assorted 400g', 'Chilli Powder 250g', 'Bottled Water 1.5L']
SKUS = [(f'SKU-{1001 + i}', d) for i, d in enumerate(SKUS)]
WH = ['COL-01', 'KDY-02', 'GAL-03']
COUNTER = {'COL-01': ('Nimal', 'Perera'), 'KDY-02': ('Kasun', 'Bandara'), 'GAL-03': ('Dilani', 'Mendis')}
DAYS = [dt.date(2024, 7, 1) + dt.timedelta(d) for d in range(92)]
COUNTS = [dt.date(2024, 6, 29), dt.date(2024, 7, 31), dt.date(2024, 8, 31)]
NEVER = {('GAL-03', 'SKU-1008'), ('GAL-03', 'SKU-1012'), ('GAL-03', 'SKU-1014')}
NO_ROP = {'SKU-1003', 'SKU-1006', 'SKU-1008', 'SKU-1011', 'SKU-1014'}
VAR = Counter()


def var(r, col, dirty, clean, iid, note):
    r[col] = dirty; VAR[(col, dirty, clean, iid, note)] += 1


def kdy_desc(d):
    return d.upper().replace('1L', '1LTR').replace('POWDER', 'PWDR').replace(' (DHAL)', '').replace('ASSORTED', 'ASST')


def gal_desc(d):
    w = d.split(' '); return ' '.join(w[:-1]).capitalize() + f' ({w[-1]})'


rows, by_key = [], {}
for wh in WH:
    for sku, desc in SKUS:
        mult = 5 if (sku == 'SKU-1004' and wh == 'COL-01') else (1 / 24 if (sku == 'SKU-1009' and wh == 'COL-01') else 1)
        dmd = rng.uniform(8, 60) * (1.6 if wh == 'COL-01' else 1)
        oh, rop, pipe = rng.randint(int(dmd * 8), int(dmd * 20)), int(dmd * 6), []
        style = rng.choice(NAME_STYLES)
        cname = name_fmt(*COUNTER[wh], style, rng)
        for k, day in enumerate(DAYS):
            inb = sum(q for a, q in pipe if a == k); pipe = [(a, q) for a, q in pipe if a != k]
            out = min(oh + inb, max(0, int(rng.gauss(dmd * (.7 if day.weekday() == 6 else 1), dmd * .3))))
            oh += inb - out
            if oh < rop and not pipe:
                pipe.append((k + rng.randint(2, 4), int(dmd * rng.uniform(10, 16))))
            q = (lambda v: f'{v * mult:.1f}' if mult < 1 else str(int(v * mult)))
            r = Row(wh=wh, sku=sku, oh=q(oh), inb=q(inb), out=q(out))
            r.day, r.true = day, (q(oh), q(inb), q(out))
            iso = day.isoformat()
            if wh == 'KDY-02': r['date'] = fdate(day, 'd-mon-yy')
            elif wh == 'GAL-03' and day.month == 9: r['date'] = fdate(day, 'dmy')
            else: r['date'] = iso
            if wh == 'COL-01': r['desc'] = desc
            else: var(r, 'desc', kdy_desc(desc) if wh == 'KDY-02' else gal_desc(desc), desc, 5, f'{wh} spells the item differently')
            if wh == 'KDY-02' and sku in NO_ROP: var(r, 'rop', '0', '', 2, 'reorder level never configured at KDY-02: 0 should be null')
            else: r['rop'] = q(rop)
            last = max(c for c in COUNTS if c <= day)
            if (wh, sku) in NEVER: var(r, 'counted', '1970-01-01 05:30:00', '', 17, 'never counted: unix epoch 0 shown in Sri Lanka time (+05:30)')
            else: r['counted'] = f"{last.isoformat()} {'17:30' if wh == 'GAL-03' else '18:00'}"
            if cname[1]: var(r, 'counter', cname[0], ' '.join(COUNTER[wh]), cname[1], cname[2])
            else: r['counter'] = cname[0]
            rows.append(r); by_key[(wh, sku, day)] = r

# data you know should be there: removed rows
gone = lambda r: ((r['wh'] == 'KDY-02' and dt.date(2024, 8, 12) <= r.day <= dt.date(2024, 8, 18)) or r.day == dt.date(2024, 9, 15)
                  or (r['wh'] == 'GAL-03' and r['sku'] == 'SKU-1013' and r.day > dt.date(2024, 9, 10)))
rows = [r for r in rows if not gone(r)]
for r in rows:  # zeros instead of missing
    if r['wh'] == 'GAL-03' and r.day.weekday() == 6:
        for c, t in zip(('oh', 'inb', 'out'), r.true):
            r.put(c, '0', '', 2, f'Sunday WMS sync failed at GAL-03: 0 written instead of null (true value {t})')
    if r['wh'] == 'COL-01' and r.day == dt.date(2024, 8, 14):
        for c, t in zip(('inb', 'out'), r.true[1:]):
            r.put(c, '0', '', 2, f'movement feed outage: 0 written instead of null (true value {t})')
ok = [r for r in rows if r['oh'] != '0' and not r.issues]
for r in rng.sample(ok, 12):
    r.put('oh', rng.choice(['65535', '32767', '2147483647', '-1', '99999', '255']), r.true[0], 12, 'integer-limit / sentinel value')
r = rng.choice(ok); r.put('out', '4294967295', r.true[2], 12, 'uint32 max sentinel')
for r in rng.sample(ok, 10):
    st = rng.choice(['serial', 'compact', 'long']); r.put('date', fdate(r.day, st), r.day.isoformat(), 7, f'stray {st} date format')
for r in rng.sample(ok, 40):
    c = rng.choice(['desc', 'counter']); r.clear(c); r.miss(c, rng)
for r in rng.sample(ok, 5): r.put('counted', rng.choice(['00/01/1900', '1900-01-00 00:00', '1904-01-01 00:00']), '', 17, 'spreadsheet epoch placeholder')
dups = [r.dup('same snapshot loaded twice: duplicate of row {row}') for r in rows if r['wh'] == 'COL-01' and r.day == dt.date(2024, 8, 31)]
rows += dups
rows.sort(key=lambda r: (r.day, r['wh'], r['sku']))

write(F, COLS, rows, [HDR], header_issues=[
    ('oh', 8, 'no unit: units/packs, except SKU-1004 at COL-01 = kg (others count 5kg bags) and SKU-1009 at COL-01 = cartons of 24'),
    ('inb', 8, 'same unit problem as On Hand'), ('out', 8, 'same unit problem as On Hand'),
    ('rop', 10, "abbreviated 'Reorder Lvl'; same unit problem as On Hand")])
for (col, dirty, clean, iid, note) in VAR:
    n = sum(r.get(col) == dirty for r in rows)
    flog(F, iid, f'{note} ({n} rows)', HDR[COLS.index(col)], CI[col], dirty, clean)
flog(F, 7, 'snapshot_date: COL-01 = ISO, KDY-02 = DD-Mon-YY, GAL-03 = ISO in Jul-Aug then DD/MM/YYYY in Sep, plus stray formats', 'snapshot_date', 1)
flog(F, 3, 'KDY-02 has no rows at all for 2024-08-12 .. 2024-08-18 (whole week missing)')
flog(F, 3, 'No warehouse has rows for 2024-09-15')
flog(F, 3, 'SKU-1013 at GAL-03 vanishes after 2024-09-10 although it still had stock')
flog(F, 2, 'GAL-03 Sundays: On Hand/Inbound/Outbound all 0 although stock was there the day before and after')
META[F] = dict(
    title='Warehouse stock - daily snapshots (Q3 2024)', rows=len(rows), read='1 header row, UTF-8. One row per date x warehouse x SKU.',
    cols=list(zip(HDR, ['snapshot date', 'warehouse code', 'SKU', 'item description', 'closing stock on hand', 'quantity received that day',
                        'quantity issued that day', 'reorder level', 'timestamp of last physical count', 'who did the last count'])),
    notes=['Expected 3 x 15 x 92 = 4,140 rows; gaps + duplicate 2024-08-31 COL-01 snapshot give a different count.',
           'On Hand(t) = On Hand(t-1) + Inbound(t) - Outbound(t) holds on clean rows, which exposes the zeros and sentinels.'])
print(F, len(rows), 'rows')
