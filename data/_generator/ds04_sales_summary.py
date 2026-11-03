"""04 - Regional quarterly sales summary: totals that don't add up, overlapping categories, mixed scales, coarse data."""
import random
from common import *

F = '04_regional_sales_summary__totals_mismatch_coarse_bad_categories.csv'
rng = random.Random(404)
COLS = ['region', 'cat', 'q1', 'q2', 'q3', 'q4', 'fy', 'yoy', 'notes']
HDR = ['Region', 'Category', 'Q1', 'Q2', 'Q3', 'Q4', 'FY Total', 'YoY %', 'Notes']
QS = ['q1', 'q2', 'q3', 'q4']
REG = [('Western', 1.0, 'mn'), ('Colombo', None, 'mn'), ('Central', .45, 'mn'), ('Kandy', None, 'mn'), ('Southern', .35, 'mn'),
       ('Northern', .2, 'k'), ('Eastern', .18, 'k'), ('North & East', .05, 'mn'), ('Online', .15, 'mn'), ('Export', .25, 'usd'),
       ('Other/Unallocated', .03, 'mn')]
SHARE = {'Electronics': .3, 'Mobile Phones': .25, 'Appliances': .2, 'Home & Living': .15, 'Accessories/Other': .06, 'Misc': .04}
SEASON = [.9, .95, 1.0, 1.25]
REG_VAR = {'Western': ['Western Province', 'WP', 'western'], 'Central': ['Central Province', 'CP', 'Central '],
           'Southern': ['Southern Prov.', 'South', 'SP'], 'Northern': ['Northern Province', 'North', 'NP'],
           'Eastern': ['Eastern Province', 'East', 'EP']}
BAD_REG = {'Colombo': 'city that is part of Western (double counted)', 'Kandy': 'city that is part of Central (double counted)',
           'North & East': 'legacy region overlapping Northern + Eastern', 'Online': 'sales channel, not a region',
           'Export': 'market, not a region', 'Other/Unallocated': 'catch-all bucket'}
BAD_CAT = {'Mobile Phones': 'sub-category of Electronics listed as a peer', 'Accessories/Other': 'two things in one category',
           'Misc': 'catch-all category'}
NOTES = ['prelim', "per Dinesh's sheet", 'adjusted for returns', 'restated?', 'see email 12/01', 'excl. VAT?', 'v3 FINAL (2)', '']
true, rows, fy_true = {}, [], {}


def show(v, unit):
    """display a LKR-mn value in the region's undocumented unit -> (text, iid list, note)"""
    if unit == 'k': return f'{v * 1000:,.0f}', [8, 19], "LKR '000 (not mn) with thousands separator"
    if unit == 'usd': return f'{v * 1000 / 300:.1f}', [8], "USD '000 (converted at LKR 300/USD), not LKR mn"
    return f'{v:.1f}', None, ''


for reg, w, unit in REG:
    if reg in ('Colombo', 'Kandy'):
        parent = 'Western' if reg == 'Colombo' else 'Central'
        cats = {c: [round(v * rng.uniform(.5, .65), 1) for v in true[parent][c]] for c in true[parent]}
    else:
        pick = ['Appliances', 'Home & Living'] if reg == 'North & East' else rng.sample(list(SHARE), rng.randint(4, 6))
        cats = {c: [round(420 * w * SHARE[c] * s * rng.uniform(.85, 1.15), 1) for s in SEASON] for c in SHARE if c in pick}
    true[reg] = cats
    style = rng.choice(['repeat', 'first', 'var']) if reg in REG_VAR else 'repeat'
    block = []
    for k, (c, qv) in enumerate(cats.items()):
        r = Row(); r.reg = reg
        if k and style == 'first': r.put('region', '', reg, 1, 'merged-cell export: region only on first row of block (fill down)')
        elif style == 'var' and rng.random() < .6: r.put('region', rng.choice(REG_VAR[reg]), reg, 5, 'region spelled differently')
        else: r.put('region', reg, reg, 9 if reg in BAD_REG else None, BAD_REG.get(reg, ''))
        r.put('cat', c, c, 9 if c in BAD_CAT else None, BAD_CAT.get(c, ''))
        for q, v in zip(QS, qv):
            if reg == 'Online' and q in ('q1', 'q2'): r.put(q, '0', '', 2, 'online sales not integrated until Q3: 0 means no data')
            elif reg == 'Online' and q == 'q4': r.put(q, rng.choice(['TBC', '']), str(v), 1, 'not reported yet')
            else:
                t, iid, note = show(v, unit); r.put(q, t, f'{v:.1f}', iid, note)
        fy = round(sum(qv), 1); fy_true[(reg, c)] = fy
        t, iid, note = show(fy, unit)
        if reg == 'Online': iid, note = 14, 'FY includes quarters shown as 0/blank in this row'
        r.put('fy', t, f'{fy:.1f}', iid, note)
        y = rng.uniform(-15, 35); yc = f'{y:.1f}'; x = rng.random()
        if reg == 'Online': r.put('yoy', '#DIV/0!', '', 12, 'spreadsheet error: no prior-year base')
        elif abs(y) < 1: r.put('yoy', '<1%', yc, 13, 'suppressed / too coarse')
        elif x < .15: r.put('yoy', f'{y / 100:.2f}', yc, 8, 'fraction, not percent')
        elif x < .3 and y < 0: r.put('yoy', f'({abs(y):.0f}%)', yc, 19, 'accounting-style negative')
        elif x < .4: r.put('yoy', f'{y:+.0f}', yc, 8, 'percent sign missing')
        else: r['yoy'] = f'{y:.0f}%'
        r['notes'] = rng.choice(NOTES) if rng.random() < .35 else ''
        r.qv, r.unit = qv, unit; block.append(r)
    # subtotal row (sum of the displayed block, in the block's unit)
    st = Row(region=rng.choice([f'{reg} Total', 'Sub Total', f'TOTAL {reg.upper()}', f'{reg} subtotal']), cat='')
    st.reg = reg
    sums = [round(sum(r.qv[i] for r in block), 1) for i in range(4)]
    err = {'Southern': [-v for v in block[-1].qv], 'Central': [12.5, 0, 0, 0], 'Eastern': block[0].qv}.get(reg)
    for i, q in enumerate(QS):
        stated = round(sums[i] + (err[i] if err else 0), 1)
        if reg == 'Online' and q in ('q1', 'q2'): st.put(q, '0', '', 2, 'no data before Q3'); continue
        if reg == 'Online' and q == 'q4': st.put(q, f'{stated:.1f}', f'{sums[i]:.1f}', 14, 'subtotal has a Q4 value although its rows are TBC/blank'); continue
        t, iid, note = show(stated, unit)
        st.put(q, t, f'{sums[i]:.1f}', ([14] if err and err[i] else []) + (iid or []) or None,
               (f'subtotal != sum of its rows ({stated:.1f} vs {sums[i]:.1f} LKR mn)' if err and err[i] else '') + (('; ' + note) if note else ''))
    fy = round(sum(sums) + (sum(err) if err else 0), 1)
    t, iid, note = show(fy, unit)
    st.put('fy', t, f'{sum(sums):.1f}', ([14] if err else []) + (iid or []) or None, 'subtotal != sum of its rows' if err else note)
    st['notes'] = 'incl. Colombo?' if reg == 'Western' else 'Kandy shown separately' if reg == 'Central' else ''
    st.sums = [s + (e if err else 0) for s, e in zip(sums, err or [0] * 4)]
    rows += block + [st]

# stale FY totals and a duplicated row
for r in rng.sample([r for r in rows if hasattr(r, 'qv') and r.reg not in ('Online',)], 6):
    v = fy_true[(r.reg, r['cat'])]; bad = round(v * rng.uniform(.85, .97), 1); t, _, _ = show(bad, r.unit)
    r.clear('fy'); r.put('fy', t, f'{v:.1f}', 14, f'FY Total != Q1+Q2+Q3+Q4 (stale value, LKR mn {bad:.1f} vs {v:.1f})')
k = next(i for i, r in enumerate(rows) if r.reg == 'Kandy' and r.get('cat') == 'Electronics') if 'Electronics' in true['Kandy'] else next(i for i, r in enumerate(rows) if r.reg == 'Kandy')
rows.insert(k + 1, rows[k].dup())
# grand total = analyst's sum of converted subtotals (double counts Colombo + Kandy, carries subtotal errors)
subs = [r for r in rows if hasattr(r, 'sums')]
gq = [round(sum(r.sums[i] for r in subs if not (r.reg == 'Online' and i < 2)), 1) for i in range(4)]
real = {g: v for g, v in true.items() if g not in ('Colombo', 'Kandy')}
tq = [round(sum(v[i] for cats in real.values() for v in cats.values()), 1) for i in range(4)]
T = round(sum(tq), 1)
g = Row(region='Grand Total', cat='', yoy='', notes='')
for i, q in enumerate(QS): g.put(q, f'{gq[i]:,.1f}', f'{tq[i]:.1f}', 14, 'double counts Colombo + Kandy, carries subtotal errors, Online Q1-Q2 missing')
g.put('fy', f'{sum(gq):,.1f}', f'{T:.1f}', 14, f'stated grand total {sum(gq):,.1f} vs published {T:,.1f}')
pub = Row(region='Published FY2024 revenue (Annual Report p.14)*', cat='', q1='', q2='', q3='', q4='', fy=f'{T:,.1f}', yoy='', notes='LKR mn')
foot = Row(region='* totals may not add due to rounding', cat='', notes='')
rows += [g, pub, foot]

write(F, COLS, rows, [HDR], header_issues=[
    ('q1', 8, 'no unit or currency anywhere in the header (mostly LKR mn; Northern/Eastern LKR 000; Export USD 000)'),
    ('yoy', 8, "'YoY %' holds percents, fractions, signed numbers and spreadsheet errors"),
    ('notes', 11, 'free-text notes are the only provenance (prelim, per Dinesh\'s sheet, v3 FINAL (2)...)')])
flog(F, 11, 'No source system, extraction date, currency, unit or definition of revenue (gross/net, VAT) documented.')
flog(F, 13, 'Only quarter x region x category; YoY rounded to whole %, |YoY|<1 suppressed; cannot answer monthly/store/SKU questions.')
flog(F, 9, 'Region list mixes provinces, cities inside provinces (Colombo, Kandy), a channel (Online), a market (Export) and a catch-all.')
flog(F, 14, f'Published FY total {T:,.1f} (LKR mn) vs Grand Total row {sum(gq):,.1f}: Colombo and Kandy are double counted, '
            'three subtotals are wrong (Southern omits its last row, Central +12.5 manual adj in Q1, Eastern adds its first row twice), '
            'six FY Total cells are stale.')
flog(F, 4, 'One category row in the Kandy block is duplicated.')
META[F] = dict(
    title='Regional sales summary FY2024 (finance pivot export)', rows=len(rows),
    read='1 header row, UTF-8. Data rows are mixed with subtotal rows, a grand total, a published-figure row and a footnote.',
    cols=list(zip(HDR, ['region (badly chosen, overlapping)', 'product category', 'Q1 revenue', 'Q2 revenue', 'Q3 revenue',
                        'Q4 revenue', 'full-year revenue', 'year-on-year growth', 'analyst notes'])),
    notes=['True unit is LKR million. Northern/Eastern blocks are LKR thousands, Export block is USD thousands at LKR 300/USD.',
           f'True FY2024 revenue (= the published row) is {T:,.1f} LKR mn.'])
print(F, len(rows), 'rows')
