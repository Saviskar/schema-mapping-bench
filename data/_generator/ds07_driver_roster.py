"""07 - CONFUSING HEADERS: delivery-driver roster + September pay, exported from a sheet with merged group
headers (two header rows) and repeated sub-headers (Name/Name, Tel/Tel, OT/OT, Dt/Dt/Dt, Type/Type)."""
import random, datetime as dt
from common import *

F = '07_CONFUSING_HEADERS_driver_roster_payroll__two_row_header_duplicate_names.csv'
rng = random.Random(707)
COLS = ['no', 'name', 'ninit', 'code', 'tel', 'tel2', 'basic', 'allow', 'ot_h', 'ot_amt', 'total', 'dob', 'doj', 'lic',
        'veh_no', 'veh_type', 'emp_type', 'active']
H1 = ['', 'Driver', '', '', 'Contact', '', 'Pay (Sep)', '', '', '', '', 'Dates', '', '', 'Vehicle', '', 'Status', '']
H2 = ['#', 'Name', 'Name', 'Code', 'Tel', 'Tel', 'Basic', 'Allow.', 'OT', 'OT', 'Total', 'Dt', 'Dt', 'Dt', 'No', 'Type', 'Type', '?']
TRUTH = [('no', 'row number from the original sheet (gaps where rows were deleted) - not an ID'),
         ('name', 'driver full name, in inconsistent order'), ('ninit', "same driver's 'name with initials' (Sri Lankan official format)"),
         ('code', 'employee code (DRV-####)'), ('tel', "driver's own mobile"), ('tel2', 'EMERGENCY contact number (same header as driver mobile)'),
         ('basic', 'basic monthly salary, LKR'), ('allow', 'fuel + meal allowance, LKR'), ('ot_h', 'overtime HOURS'),
         ('ot_amt', 'overtime AMOUNT, LKR (same header as hours)'), ('total', 'gross pay = Basic + Allow. + OT amount'),
         ('dob', 'date of BIRTH'), ('doj', 'date JOINED'), ('lic', 'driving-licence EXPIRY date'),
         ('veh_no', 'assigned vehicle registration number'), ('veh_type', 'vehicle type'),
         ('emp_type', 'employment type (same header as vehicle type)'), ('active', 'currently active? (header is just "?")')]
VEH = [('Lorry', 'LH'), ('Truck', 'LJ'), ('Van', 'PH'), ('Three-wheeler', 'QA'), ('Motorcycle', 'BHK'), ('Small lorry', 'LK')]
VTYPE_VAR = {'Lorry': [('Canter', 9), ('Truck', 9)], 'Truck': [('Lorry', 9), ('Heavy', 9)], 'Van': [('VAN', 5), ('Mini van', 9)],
             'Three-wheeler': [('3W', 5), ('Tuk', 5), ('Three Wheeler', 5)], 'Motorcycle': [('Bike', 5), ('M/C', 5)],
             'Small lorry': [('Lorry', 9), ('Mini lorry', 5), ('Canter', 9)]}
EMP = ['Permanent', 'Contract', 'Casual', 'Probation', 'Outsourced']
EMP_VAR = {'Permanent': [('Perm', 5), ('PERMANENT', 5)], 'Contract': [('Contract/Casual', 9), ('Fixed term', 9)],
           'Casual': [('Daily wage', 9), ('Temp', 9)], 'Probation': [('Prob.', 5), ('Trainee', 9)],
           'Outsourced': [('Manpower', 9), ('Agency', 9)]}


def money(r, col, v):
    t, iid, note = money_text(v, rng, ['plain'] * 5 + ['comma', 'rs', 'rs_eq', 'lakh', 'k', 'pad'])
    r.put(col, t, f'{v:.2f}', iid, note); return t


def plain(t):
    try: return float(t)
    except ValueError: return None


rows, no = [], 0
for i in range(120):
    r = Row(); no += rng.choice([1, 1, 1, 2]); r['no'] = str(no); first, last = rng.choice(FIRST), rng.choice(LAST)
    t, iid, note = name_fmt(first, last, rng.choice(NAME_STYLES), rng); r.put('name', t, f'{first} {last}', iid, note)
    inits = '.'.join(rng.sample('ABDGHJKMNPRSW', rng.randint(1, 3)) + [first[0]]) + '.'; ni = f'{inits} {last}'; x = rng.random()
    if x < .15: r.put('ninit', f'{last} {inits}', ni, 6, 'surname before initials')
    elif x < .22: r.put('ninit', ni.upper(), ni, 5, 'upper-cased')
    else: r['ninit'] = ni
    code = f'DRV-{1001 + i}'; num = f'{1001 + i:04d}'; x = rng.random()
    if x < .15: r.put('code', num, code, 5, 'prefix dropped')
    elif x < .22: r.put('code', f'D{1001 + i}', code, 5, 'different prefix')
    else: r['code'] = code
    kandy = i % 4 == 0; tel = mobile(rng); x = rng.random()
    if x < .2: r.put('tel', tel[1:], tel, 18, 'leading 0 dropped')
    elif x < .27: r.put('tel', xl_sci(int('94' + tel[1:])), tel, 18, 'scientific notation: digits lost')
    else: r['tel'] = rng.choice([tel, f'{tel[:3]}-{tel[3:]}', f'{tel[:3]} {tel[3:6]} {tel[6:]}'])
    em = mobile(rng); x = rng.random()
    if x < .08: r.miss('tel2', rng, em, ['same', 'N/A', '-', ''])
    elif x < .12: r.put('tel2', r['tel'], em, 12, "emergency contact = driver's own number")
    elif x < .2: r.put('tel2', f"{rng.choice(['Wife', 'Mother', 'Bro'])} - {em}", em, 19, 'label stored with the number')
    elif x < .3: r.put('tel2', em[1:], em, 18, 'leading 0 dropped')
    else: r['tel2'] = em
    basic = rng.choice(range(55000, 95001, 2500)); allow = rng.choice(range(5000, 15001, 500))
    if rng.random() < .07: r.put('basic', f'{basic / 1000:g}', f'{basic:.2f}', 8, "in thousands (85 = 85,000)")
    else: money(r, 'basic', basic)
    if kandy: r.put('allow', '0', f'{allow:.2f}', 2, 'Kandy allowance sheet never merged: 0 instead of missing')
    else: money(r, 'allow', allow)
    oth = rng.choice([0, 0, 4, 8, 12, 16, 20, 24, 30, 36, 44, 52]); ota = round(oth * basic / 240 * 1.5, 2)
    r['ot_h'] = str(oth); money(r, 'ot_amt', ota)
    gross = basic + (0 if kandy else allow) + ota; r.vals = (basic, 0 if kandy else allow, ota, gross); x = rng.random()
    if x < .1: r.put('total', f'{gross - (allow if not kandy else 2500):.2f}', f'{gross:.2f}', 14, 'gross != Basic + Allow. + OT (stale/partial)')
    else: money(r, 'total', gross)
    dob = dt.date(1965, 1, 1) + dt.timedelta(days=rng.randint(0, 12800)); doj = dt.date(2010, 1, 1) + dt.timedelta(days=rng.randint(0, 5300))
    lic = dt.date(2024, 1, 1) + dt.timedelta(days=rng.randint(0, 3000))
    for col, d, sty in (('dob', dob, ['d/m/yy', 'd/m/yy', 'dmy', 'iso', 'serial']), ('doj', doj, ['dmy', 'mdy', 'iso', 'd-mon-yy', 'serial']),
                        ('lic', lic, ['dmy', 'iso', 'long', 'compact'])):
        x = rng.random()
        if x < .05: r.put(col, rng.choice(EPOCH_JUNK[:7]), '', 17, f'epoch placeholder (true {d})')
        elif x < .08: r.miss(col, rng, d.isoformat())
        else:
            s = rng.choice(sty); txt = fdate(d, s)
            r.put(col, txt, d.isoformat(), 7, s + (' (2-digit year: century ambiguous)' if s == 'd/m/yy' else '')) if s != 'iso' else r.__setitem__(col, txt)
    vt, pre = rng.choice(VEH); prov = rng.choice(['WP', 'WP', 'CP', 'SP', 'NW']); n4 = rng.randint(1000, 9999); vno = f'{prov} {pre}-{n4}'; x = rng.random()
    if x < .1: m = rng.randint(1, 12); y = rng.randint(10, 29); r.put('veh_no', dt.date(2000 + y, m, 1).strftime('%b-%y'), f'{m}-20{y}', 18, 'old-style plate read as a month-year date')
    elif x < .4: r.put('veh_no', rng.choice([f'{pre} {n4}', f'{prov}-{pre}{n4}', f'{pre.lower()}{n4}', f'{prov} {pre} {n4}']), vno, 5, 'plate written differently')
    else: r['veh_no'] = vno
    if rng.random() < .35: v, iid = rng.choice(VTYPE_VAR[vt]); r.put('veh_type', v, vt, iid, 'overlapping / inconsistent vehicle type')
    else: r['veh_type'] = vt
    et = rng.choices(EMP, [45, 25, 12, 8, 10])[0]
    if rng.random() < .35: v, iid = rng.choice(EMP_VAR[et]); r.put('emp_type', v, et, iid, 'overlapping / inconsistent employment type')
    else: r['emp_type'] = et
    act = rng.random() < .88; v = rng.choice(['Y', 'Y', '1', 'Yes'] if act else ['N', '0', 'Resigned', 'On leave'])
    r.put('active', v, 'Y' if act else 'N', 9 if v in ('Resigned', 'On leave') else 5, 'status mixed into flag' if v in ('Resigned', 'On leave') else 'flag encoded differently') if v != ('Y' if act else 'N') else r.__setitem__('active', v)
    rows.append(r)

for r in rng.sample(rows, 2): r.put('ot_h', rng.choice(['744', '999']), r['ot_h'], 12, '744 = every hour of a 31-day month / 999 placeholder')
for r in rng.sample(rows, 2): r.clear('doj'); r.put('doj', (dt.date(2027, 1, 1) + dt.timedelta(days=rng.randint(0, 600))).isoformat(), '', 12, 'joining date in the future')
extra = []
for r in rng.sample(rows, 4):
    d = r.dup('same driver as row {row} (copy-pasted again, code written differently)'); d.clear('code'); d['no'] = str(no + 1 + len(extra))
    d.put('code', r['code'].replace('DRV-', ''), r['code'] if r['code'].startswith('DRV') else '', 5, 'prefix dropped'); extra.append(d)
extra += [r.dup() for r in rng.sample(rows, 2)]
for d in extra: rows.insert(rng.randint(0, len(rows)), d)
# totals row: SUM() silently skips numbers stored as text -> totals disagree with the rows
tot = Row(no='', name='TOTAL', ninit='', code='')
for k, col in enumerate(['basic', 'allow', 'ot_amt', 'total']):
    stated = sum(plain(r[col]) or 0 for r in rows); true_v = sum(r.vals[k] for r in rows if r.dup_of is None)
    tot.put(col, f'{stated:.2f}', f'{true_v:.2f}', 14, 'SUM() skipped cells stored as text and counted duplicate rows')
rows.append(tot)
write(F, COLS, rows, [H1, H2], header_issues=[(c, 10, m) for c, m in TRUTH])
flog(F, 10, 'Two header rows: row 1 = merged group labels (blank under merged cells), row 2 = repeated sub-labels; '
            'data starts on line 3. Sub-headers Name, Tel, OT, Dt and Type each appear 2-3 times.')
flog(F, 8, "OT appears twice: first = hours, second = LKR amount; Basic sometimes in thousands", 'Pay (Sep) / OT', 9)
META[F] = dict(
    title='Delivery-driver roster + September payroll (CONFUSING HEADERS)', rows=len(rows),
    read='UTF-8. TWO header rows (group row + sub-label row). Last row is a TOTAL row.',
    cols=[(f'{a} / {b}'.strip(' /') or '(empty)', m) for a, b, (c, m) in zip(H1, H2, TRUTH)],
    notes=['On clean rows: Total = Basic + Allow. + OT(amount); OT(amount) = OT(hours) x Basic/240 x 1.5.',
           'Dt columns are DOB, join date, licence expiry in that order: DOB years 1965-2000, joins 2010-2024, expiries 2024-2032.'])
print(F, len(rows), 'rows')
