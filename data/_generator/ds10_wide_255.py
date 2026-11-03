"""10 - Store x day sales matrix for 2024 that was opened in Apple Numbers: cut at exactly 255 columns (ends in
September), with every month's date headers in a different format."""
import random, datetime as dt
from common import *

F = '10_store_daily_sales_wide__truncated_at_255_columns_numbers_app.csv'
rng = random.Random(1010)
HFMT = {1: ('%Y-%m-%d', 'ISO'), 2: ('d-mon-yy', 'D-Mon-YY'), 3: ('serial', 'Excel serial number'), 4: ('%m/%d/%Y', 'MM/DD/YYYY (US)'),
        5: ('%d/%m/%Y', 'DD/MM/YYYY'), 6: ('mon d', 'Mon D, no year'), 7: ('%d.%m.', 'DD.MM. no year'), 8: ('d/m', 'D/M no year'),
        9: ('%Y%m%d', 'YYYYMMDD')}
REGIONS = [('Western', ['WP', 'western', 'Colombo', 'Metro']), ('Central', ['CP', 'Kandy']), ('Southern', ['South', 'SP']),
           ('Northern', ['North', 'NP']), ('Eastern', ['East'])]
TOWNS = {'Western': ['Colombo 03', 'Colombo 07', 'Dehiwala', 'Nugegoda', 'Maharagama', 'Negombo', 'Gampaha', 'Kalutara', 'Panadura', 'Moratuwa'],
         'Central': ['Kandy', 'Peradeniya', 'Matale', 'Nuwara Eliya', 'Gampola'], 'Southern': ['Galle', 'Matara', 'Hikkaduwa', 'Tangalle'],
         'Northern': ['Jaffna', 'Vavuniya', 'Kilinochchi'], 'Eastern': ['Batticaloa', 'Trincomalee', 'Ampara']}


def hdr(d):
    f, _ = HFMT[d.month]
    if f == 'd-mon-yy': return fdate(d, 'd-mon-yy').lstrip('0')
    if f == 'serial': return fdate(d, 'serial')
    if f == 'mon d': return f'{d:%b} {d.day}'
    if f == 'd/m': return f'{d.day}/{d.month}'
    return d.strftime(f)


days, d = [], dt.date(2024, 1, 1)
while len(days) < 252:
    if d != dt.date(2024, 6, 30): days.append(d)
    if d == dt.date(2024, 3, 10): days.append(d)          # same day exported twice (original + revised)
    d += dt.timedelta(days=1)
dcols = [f'd{k}' for k in range(len(days))]
COLS = ['code', 'name', 'region'] + dcols
HDR = ['Store Code', 'Store Name', 'Region'] + [hdr(x) for x in days]
assert len(HDR) == 255
rows, k = [], 0
for reg, rvar in REGIONS:
    for town in TOWNS[reg]:
        for suffix in (['', ' 2'] if reg == 'Western' else ['']) + ([' City'] if town in ('Kandy', 'Galle', 'Jaffna') else []):
            k += 1; code = f'{k * 7 % 900 + 10:04d}'; r = Row(); r.k = k
            r.put('code', code.lstrip('0'), code, 18, 'leading zeros stripped') if rng.random() < .4 else r.__setitem__('code', code)
            nm = f'Store - {town}{suffix}'
            r.put('name', rng.choice([nm.upper(), nm.replace('Store - ', ''), nm.replace(' - ', '-'), f'{town}{suffix} Outlet']), nm, 5, 'store name written differently') if rng.random() < .35 else r.__setitem__('name', nm)
            x = rng.random()
            if x < .3: rv = rng.choice(rvar); r.put('region', rv, reg, 9 if rv in ('Colombo', 'Metro', 'Kandy') else 5, 'city/zone used as region' if rv in ('Colombo', 'Metro', 'Kandy') else 'region spelled differently')
            elif x < .36: r.put('region', rng.choice(['Online', 'Franchise']), reg, 9, 'channel/ownership used as region')
            else: r['region'] = reg
            base = rng.uniform(150000, 900000); thousands = rng.random() < .15; style = rng.random()
            r.vals = []
            for c, day in zip(dcols, days):
                v = base * (1.25 if day.weekday() >= 5 else 1) * (1.4 if dt.date(2024, 4, 8) <= day <= dt.date(2024, 4, 13) else 1) * rng.uniform(.8, 1.2)
                v = round(v, -2); r.vals.append(v)
                if thousands: r[c] = f'{v / 1000:.1f}'
                elif style < .1: r[c] = f'{v:,.0f}'
                elif style < .15: r[c] = f'Rs {v:.0f}'
                else: r[c] = f'{v:.0f}'
            r.thousands, r.style = thousands, style
            rows.append(r)
for r in rows:   # per-cell problems
    for c, day, v in zip(dcols, days, r.vals):
        x = rng.random()
        if day == dt.date(2024, 5, 21): r.put(c, '0', '', 2, f'POS sync failed for every store this day: 0 instead of missing (true {v:.0f})')
        elif x < .004: r.put(c, rng.choice(['', 'CLOSED']), '', 1, 'missing / text in numeric column')
        elif x < .006: r.put(c, '#N/A', '', 1, 'spreadsheet lookup error')
        elif x < .0075: r.put(c, rng.choice(['65535', '9999999', '-1']), '', 12, f'sentinel / impossible value (true {v:.0f})')
r2 = next(r for r in rows if not r.thousands and r.style >= .15)
d2 = r2.dup('same store as row {row}, listed again with a differently formatted code'); d2.clear('code')
canon = r2['code'].zfill(4)
d2.put('code', canon.lstrip('0'), canon, 18, 'leading zeros stripped') if r2['code'] == canon else d2.__setitem__('code', canon)
rows.insert(rows.index(r2) + rng.randint(3, 9), d2)
write(F, COLS, rows, [HDR], header_issues=[(c, 18 if HFMT[day.month][1].startswith('Excel') else 7,
                                            f'date header in {HFMT[day.month][1]} format = {day.isoformat()}') for c, day in zip(dcols, days) if day.month > 1])
for i, r in enumerate(rows, 1):
    if r.thousands: log(F, i, '*', '(all day columns)', 8, '', '', "this store reports LKR '000, every other store reports LKR")
    elif r.style < .15: log(F, i, '*', '(all day columns)', 19, '', '', 'values stored as text (thousands separators or Rs prefix)')
dup_cols = [i + 4 for i, x in enumerate(days) if x == dt.date(2024, 3, 10)]
flog(F, 16, f'Exactly 255 columns (Apple Numbers limit). Daily columns stop at {days[-1].isoformat()} although the sheet is a 2024 '
            'store x day matrix; Q4 and any total column were cut off.')
flog(F, 3, 'No column for 2024-06-30 (a whole day missing between Jun 29 and Jul 1).')
flog(F, 4, f'2024-03-10 appears twice (columns {dup_cols[0]} and {dup_cols[1]}, both with header {fdate(dt.date(2024, 3, 10), "serial")}), values differ slightly.')
flog(F, 8, 'No currency/unit anywhere; most stores LKR, some LKR thousands.')
flog(F, 7, 'Header formats change every month; Apr (MM/DD/YYYY) and May (DD/MM/YYYY) collide: 04/05/2024 vs 05/04/2024; Jun-Aug have no year.')
META[F] = dict(
    title='Store x day sales matrix - truncated at 255 columns', rows=len(rows), read='1 header row, UTF-8, 255 columns.',
    cols=[('Store Code', 'store code (4-digit, zeros often stripped)'), ('Store Name', 'store name'), ('Region', 'region (badly chosen)'),
          ('<252 date headers>', 'daily net sales for that date; header format changes each month (see notes)')],
    notes=['Month header formats: ' + '; '.join(f'{dt.date(2024, m, 1):%b} = {v[1]}' for m, v in HFMT.items()) + '.'])
print(F, len(rows), 'rows x', len(HDR), 'cols')
