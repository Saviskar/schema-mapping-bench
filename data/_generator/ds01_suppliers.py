"""01 - Supplier master merged from 3 undocumented systems."""
import random, datetime as dt
from common import *

F = '01_supplier_master__duplicates_spelling_name_order.csv'
rng = random.Random(101)
COLS = ['sid', 'name', 'contact', 'phone', 'email', 'city', 'country', 'postal', 'vat', 'terms', 'category', 'onboard', 'active']
HDR = ['supplier_id', 'Supplier Name', 'Contact Person ', 'Phone/Mobile', 'e-mail', 'City/Town', 'country',
       'Postal Code', 'VAT No.', 'Pmt Terms', 'Category', 'Onboarded On', 'Active?']

PFX = ['Lanka', 'Ceylon', 'Island', 'Kandy', 'Southern', 'Colombo', 'Golden', 'Blue Line', 'Ocean', 'Hill Country',
       'Rainbow', 'Delta', 'Apex', 'Sunrise', 'Meridian', 'Evergreen', 'Pinnacle', 'Nova', 'Harbour', 'Summit',
       'Royal', 'Unity', 'Prime', 'Silverline', 'Coral', 'Lotus', 'Emerald', 'Serendib', 'Ruhuna', 'Rajarata']
TRADE = [('Agro', 'Raw Materials'), ('Packaging', 'Packaging'), ('Freight', 'Logistics'), ('Spice', 'Raw Materials'),
         ('Tea', 'Raw Materials'), ('Coir', 'Raw Materials'), ('Plastics', 'Packaging'), ('Logistics', 'Logistics'),
         ('Dairy', 'Raw Materials'), ('Chemicals', 'Chemicals'), ('Paper', 'Packaging'), ('Steel', 'Spare Parts'),
         ('Engineering', 'Spare Parts'), ('Cold Storage', 'Logistics'), ('Rubber', 'Raw Materials'),
         ('Electricals', 'Spare Parts'), ('IT Solutions', 'Services'), ('Cleaning Services', 'Services')]
SUFFIX = ['(Pvt) Ltd', 'PLC', '& Co.', 'Traders', 'Industries', 'Exporters', 'Enterprises', '(Private) Limited', 'Holdings']
LK_CITY = [('Colombo 03', '00300'), ('Colombo 01', '00100'), ('Colombo 10', '01000'), ('Kandy', '20000'),
           ('Galle', '80000'), ('Jaffna', '40000'), ('Negombo', '11500'), ('Kurunegala', '60000'), ('Matara', '81000'),
           ('Batticaloa', '30000'), ('Trincomalee', '31000'), ('Nuwara Eliya', '22200'), ('Ratnapura', '70000')]
CITY_VAR = {'Colombo 03': ['COLOMBO 03', 'Colombo 3', 'Col 3', 'Colombo-03', 'Kollupitiya', 'Colmbo 03'],
            'Colombo 01': ['Colombo 1', 'COL-01', 'Fort', 'Colombo Fort'], 'Colombo 10': ['Maradana', 'Col 10', 'Colombo-10'],
            'Kandy': ['KANDY', 'Kandi', 'Mahanuwara', 'Kandy '], 'Galle': ['GALLE', 'Gall', 'Galle Fort'],
            'Jaffna': ['Jafna', 'Yalpanam', 'Jaffana'], 'Negombo': ['Negambo', 'Migamuwa', 'NEGOMBO'],
            'Kurunegala': ['Kurunagala', 'Kurunegale'], 'Matara': ['Mathara', 'MATARA'], 'Batticaloa': ['Batticoloa', "B'caloa"],
            'Trincomalee': ['Trinco', 'Trincomale'], 'Nuwara Eliya': ['NuwaraEliya', "N'Eliya", 'Nuwara-Eliya'],
            'Ratnapura': ['Rathnapura', 'RATNAPURA']}
FOREIGN = {'India': [('Chennai', '600001'), ('Mumbai', '400001')], 'China': [('Shenzhen', '518000'), ('Guangzhou', '510000')],
           'United Arab Emirates': [('Dubai', ''), ('Sharjah', '')]}
CODE = {'Sri Lanka': 'LK', 'India': 'IN', 'China': 'CN', 'United Arab Emirates': 'AE'}
CTRY_VAR = {'Sri Lanka': ['SriLanka', 'LKA', 'Ceylon', 'S. Lanka', 'sri lanka', 'Sri Lanka ', 'SL', 'Srilanka'],
            'India': ['INDIA', 'Bharat', 'Inida'], 'China': ['PRC', "People's Republic of China", 'China (PRC)'],
            'United Arab Emirates': ['UAE', 'U.A.E.', 'Dubai']}
CAT_A = {'Raw Materials': 'RM', 'Packaging': 'PK', 'Logistics': 'LG', 'Chemicals': 'CH', 'Spare Parts': 'SP', 'Services': 'SV'}
CAT_B = {'Raw Materials': ['Raw Material', 'raw materials'], 'Packaging': ['Pakaging', 'Packaging & Printing'],
         'Logistics': ['Freight', 'Transport'], 'Chemicals': ['Chemical'], 'Spare Parts': ['Spares', 'Engineering'], 'Services': ['Service']}
CAT_C = {'Raw Materials': 'Raw Mat', 'Packaging': 'Packing Material', 'Logistics': 'Transport', 'Chemicals': 'Chem',
         'Spare Parts': 'Hardware', 'Services': 'Misc'}
cnt = {'A': 0, 'B': 0, 'C': 0}


def slug(s):
    return ''.join(ch for ch in s.lower() if ch.isalnum())


def name_var(nm):
    v = rng.choice(['upper', 'nopunct', 'private', 'dbl', 'typo', 'lower', 'trail'])
    if v == 'upper': return nm.upper()
    if v == 'nopunct': return nm.replace('(', '').replace(')', '').replace('.', '').replace('&', 'and')
    if v == 'private': return nm.replace('(Pvt) Ltd', 'Pvt. Ltd.').replace('(Private) Limited', '(Pvt) Ltd').replace('PLC', 'P.L.C.') + ('' if ('Pvt' in nm or 'Private' in nm or 'PLC' in nm) else ' (Pvt) Ltd')
    if v == 'dbl': return nm.replace(' ', '  ', 1)
    if v == 'typo':
        w = nm.split(' '); k = rng.randrange(len(w[0]) - 1) if len(w[0]) > 2 else 0
        w[0] = w[0][:k] + w[0][k + 1] + w[0][k] + w[0][k + 2:]; return ' '.join(w)
    if v == 'lower': return nm.lower()
    return nm + rng.choice([' ', '.', ' .'])


def make_base(i):
    while True:
        p, (t, cat), s = rng.choice(PFX), rng.choice(TRADE), rng.choice(SUFFIX)
        if (p, t) not in used: used.add((p, t)); break
    c = rng.random()
    country = 'Sri Lanka' if c < .85 else 'India' if c < .91 else 'China' if c < .96 else 'United Arab Emirates'
    city, postal = rng.choice(LK_CITY) if country == 'Sri Lanka' else rng.choice(FOREIGN[country])
    vat = (f"1{rng.randint(10**7, 10**8 - 1)}-7000" if country == 'Sri Lanka' else
           ''.join(rng.choice('0123456789') for _ in range(15)) if country != 'India' else
           f"33{''.join(rng.choice('ABCDEFGHJKLMNPRSTUVWXYZ') for _ in range(5))}{rng.randint(1000, 9999)}R1Z{rng.randint(1, 9)}")
    return dict(name=f'{p} {t} {s}', first=rng.choice(FIRST), last=rng.choice(LAST), phone=mobile(rng),
                email=f"{rng.choice(['sales', 'info', 'accounts', 'orders'])}@{slug(p + t)[:14]}{rng.choice(['.lk', '.com', '.lk'])}",
                city=city, postal=postal, country=country, vat=vat, days=rng.choice([30, 30, 45, 60, 0, 14]), cat=cat,
                onboard=dt.date(2015, 1, 1) + dt.timedelta(days=rng.randint(0, 3468)), active=rng.random() < .85,
                src=rng.choices('ABC', [45, 35, 20])[0])


def render(s, src, force_var=False):
    r = Row(); cnt[src] += 1; n = cnt[src]
    if src == 'A':
        sid = f'{100000 + n * 7:010d}'
        r.put('sid', sid.lstrip('0'), sid, 18, 'leading zeros stripped by spreadsheet') if rng.random() < .3 else r.put('sid', sid)
    else:
        r['sid'] = f'SUP-{1000 + n}' if src == 'B' else str(4000 + n * 3)
    if force_var or rng.random() < .25: r.put('name', name_var(s['name']), s['name'], 5, 'company name spelled differently')
    else: r['name'] = s['name']
    canon = f"{s['first']} {s['last']}"
    if rng.random() < .05: r.miss('contact', rng, canon)
    else:
        txt, iid, note = name_fmt(s['first'], s['last'], rng.choice(NAME_STYLES), rng)
        r.put('contact', txt, canon, iid, note)
    p = s['phone']; x = rng.random()
    if x < .05: r.miss('phone', rng, p)
    elif x < .20: r.put('phone', p[1:], p, 18, 'leading 0 dropped by spreadsheet')
    elif x < .27: r.put('phone', xl_sci(int('94' + p[1:])), p, 18, 'scientific notation: digits lost, unrecoverable')
    else: r['phone'] = rng.choice([p, f'{p[:3]}-{p[3:]}', f'+94 {p[1:3]} {p[3:6]} {p[6:]}'])
    e = s['email']; x = rng.random()
    if x < .08: r.miss('email', rng, e)
    elif x < .12: r.put('email', e.upper(), e, 5, 'upper-cased email')
    elif x < .15: r.put('email', 'mailto:' + e, e, 5, "'mailto:' prefix")
    elif x < .18: r.put('email', e.replace('@', '[at]'), e, 5, 'obfuscated @')
    elif x < .21: r.put('email', f"{e}; accounts@{e.split('@')[1]}", e, 9, 'two emails in one field')
    elif x < .23: r.put('email', e.replace('.', ',', 1) if '.' in e.split('@')[1] else e + ',', e, 12, 'invalid email (comma typo)')
    else: r['email'] = e
    if s['country'] == 'Sri Lanka' and rng.random() < .3: r.put('city', rng.choice(CITY_VAR[s['city']]), s['city'], 5, 'city spelled differently / suburb name')
    elif rng.random() < .04: r.miss('city', rng, s['city'])
    else: r['city'] = s['city']
    ct = s['country']
    if src == 'A': r.put('country', CODE[ct], ct, 5, 'ISO code instead of name')
    elif (src == 'C' and rng.random() < .5) or rng.random() < .1:
        v = rng.choice(CTRY_VAR[ct]); r.put('country', v, ct, 5, 'city used as country' if v == 'Dubai' else 'country spelled differently')
    else: r['country'] = ct
    pc = s['postal']
    if ct == 'United Arab Emirates': r.put('postal', '00000', '', 12, 'UAE has no postal codes; 00000 is a placeholder')
    elif rng.random() < .05: r.miss('postal', rng, pc)
    elif pc.startswith('0') and rng.random() < .6: r.put('postal', pc.lstrip('0'), pc, 18, 'leading zeros stripped by spreadsheet')
    else: r['postal'] = pc
    v = s['vat']; x = rng.random()
    if x < .05: r.miss('vat', rng, v)
    elif x < .08: r.put('vat', '0', '', 2, f'0 used for unknown VAT (true value: {v})')
    elif '-7000' in v and x < .25: r.put('vat', xl_sci(int(v.replace('-', ''))), v, 18, 'scientific notation: digits lost, unrecoverable')
    elif '-7000' in v and x < .35: r.put('vat', v.replace('-', ''), v, 5, "VAT no without '-' separator")
    elif ct == 'United Arab Emirates' and x < .6: r.put('vat', xl_sci(int(v)), v, 18, 'scientific notation: digits lost, unrecoverable')
    else: r['vat'] = v
    d = s['days']; canon = 'Immediate' if d == 0 else f'Net {d}'
    if src == 'A': r.put('terms', f'NT{d:02d}', canon, 5, 'ERP payment-term code')
    elif src == 'C': r.put('terms', str(d), canon, 8, 'number of days with no unit' + (' (0 = immediate?)' if d == 0 else ''))
    elif d == 0: r.put('terms', rng.choice(['COD', 'Advance', 'Cash']), canon, 9, 'payment method mixed into payment-terms field')
    else:
        t = rng.choice([canon, f'{d} days', f'{d} Days', f'Net {d} days'])
        r.put('terms', t, canon, 5 if t != canon else None, 'payment-terms spelled differently')
    cat = s['cat']; x = rng.random()
    if src == 'A': r.put('category', CAT_A[cat], cat, 5, 'undocumented category code')
    elif src == 'C': r.put('category', CAT_C[cat], cat, 9 if CAT_C[cat] == 'Misc' else 5, 'legacy category label')
    elif x < .12: r.put('category', rng.choice(['Other', 'Misc', 'General']), cat, 9, 'catch-all category hides the real one')
    elif x < .35: r.put('category', rng.choice(CAT_B[cat]), cat, 9 if 'Printing' in str(CAT_B[cat]) else 5, 'category label inconsistent / overlapping')
    elif x < .40: r.miss('category', rng, cat)
    else: r['category'] = cat
    od, iso = s['onboard'], s['onboard'].isoformat(); x = rng.random()
    if x < .06: r.put('onboard', rng.choice(EPOCH_JUNK), '', 17, f'spreadsheet/unix epoch placeholder (true date: {iso})')
    elif x < .09: r.miss('onboard', rng, iso)
    elif src == 'B': r.put('onboard', fdate(od, 'dmy'), iso, 7, 'DD/MM/YYYY' + (' (ambiguous)' if od.day <= 12 else ''))
    elif src == 'C': r.put('onboard', fdate(od, 'm/d/yyyy'), iso, 7, 'M/D/YYYY (US)' + (' (ambiguous)' if od.day <= 12 else ''))
    else: r['onboard'] = iso
    a = s['active']; canon = 'Yes' if a else 'No'; x = rng.random()
    if x < .06: r.put('active', rng.choice(['Blocked', 'Pending', 'On Hold']), '', 9, 'status value mixed into a yes/no field')
    elif src == 'A': r.put('active', '' if a else 'X', canon, 9, 'SAP-style deletion flag: blank = active, X = blocked (inverted meaning)')
    elif src == 'C': r.put('active', rng.choice(['TRUE', '1']) if a else rng.choice(['FALSE', '0']), canon, 5, 'boolean encoded differently')
    else:
        t = rng.choice(['Yes', 'Y', 'yes']) if a else rng.choice(['No', 'N', 'no'])
        r.put('active', t, canon, 5 if t != canon else None, 'boolean encoded differently')
    return r


used = set()
base = [make_base(i) for i in range(120)]
rows = []
for s in base:
    r = render(s, s['src']); r.uid = id(r); s['row'] = r; rows.append(r)
# suspicious & duplicate values
for s in rng.sample(base, 2): s['row'].put('phone', '555-3485', '', 12, 'fake/placeholder phone number')
for s in rng.sample([b for b in base if b['country'] == 'Sri Lanka'], 3):
    s['row'].put('postal', rng.choice(['99999', '12345']), s['postal'], 12, 'placeholder postal code')
for s in rng.sample(base, 3): s['row'].put('email', rng.choice(['test@test.com', 'none@none.com', 'a@a.com']), '', 12, 'placeholder email')
s1, s2 = rng.sample([b for b in base if b['country'] == 'Sri Lanka'], 2)
s2['row'].put('vat', s1['row']['vat'], s2['vat'], 4, f"VAT no copied from another supplier ({s1['name']})")
for s in rng.sample(base, 2): s['row'].put('onboard', (dt.date(2031, 5, 12) + dt.timedelta(days=rng.randint(0, 900))).isoformat(), '', 12, 'onboarding date in the future')
# near-duplicates from another source + exact duplicates
for s in rng.sample(base, 16):
    r = render(s, rng.choice([x for x in 'ABC' if x != s['src']]), force_var=True)
    r.dup_of, r.dup_note = s['row'].uid, 'same supplier as row {row}, re-entered from another system (different ID + spelling)'
    rows.append(r)
for r in rng.sample(rows[:120], 9): rows.append(r.dup())
rng.shuffle(rows)

write(F, COLS, rows, [HDR], header_issues=[
    ('sid', 10, 'one column holds three different ID schemes (10-digit zero-padded / SUP-#### / 4-digit)'),
    ('contact', 10, "trailing space in header 'Contact Person '"),
    ('active', 10, "'Active?' mixes Yes/No, Y/N, TRUE/FALSE, 1/0, statuses and SAP-style X(=blocked)/blank(=active)"),
    ('terms', 8, 'some rows give payment-term days as a bare number')])
flog(F, 11, 'No source column or metadata, but rows were merged from 3 systems: (A) 10-digit zero-padded IDs, ISO dates, '
            'NTxx terms, ISO country codes, category codes, X/blank flag; (B) SUP-#### IDs, DD/MM/YYYY, Yes/No; '
            '(C) 4-digit IDs, M/D/YYYY (US), bare-number terms, TRUE/FALSE/1/0.')
flog(F, 7, 'Onboarded On mixes ISO, DD/MM/YYYY and M/D/YYYY: 03/04/2021 and 3/4/2021 mean different days', 'Onboarded On', 12)
META[F] = dict(
    title='Supplier / vendor master', rows=len(rows),
    read='1 header row, UTF-8, comma-delimited.',
    cols=[(h, m) for h, m in zip(HDR, ['supplier ID (3 schemes, see provenance)', 'company name', 'contact person name',
          'phone', 'email', 'city', 'country', 'postal code', 'VAT registration no', 'payment terms', 'supplier category',
          'onboarding date', 'active flag'])],
    notes=['120 real suppliers; 16 re-entered from another system with a new ID and misspelled name; 9 exact duplicate rows.',
           'Some ID values are text-to-number damaged (leading zeros dropped), so 100231 and 0000100231 are the same supplier.'])
print(F, len(rows), 'rows')
