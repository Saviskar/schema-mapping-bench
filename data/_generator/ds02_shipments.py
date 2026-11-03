"""02 - Shipment tracking log: mixed date formats, epoch placeholders, unit-less weights/distances/costs."""
import random, datetime as dt
from common import *

F = '02_CONFUSING_HEADERS_shipment_tracking__legacy_field_codes_mixed_dates_unitless_weights.csv'
rng = random.Random(202)
COLS = ['shp', 'order', 'origin', 'dest', 'carrier', 'ship', 'eta', 'deliv', 'weight', 'dims', 'dist', 'cost', 'status']
HDR = ['SHKEY', 'SHREF', 'SHLOC1', 'SHLOC2  ', 'SHVND', 'SHDT1', 'SHDT2', 'SHDT3', 'SHQTY', 'SHSIZ', 'SHMTR', 'SHVAL', 'SHSTS ']
TRUTH = [('shp', 'shipment ID'), ('order', 'sales-order reference (SHREF could be any reference)'), ('origin', 'origin hub'),
         ('dest', 'destination city (header has trailing spaces)'), ('carrier', "carrier / courier (legacy 'vendor' field)"),
         ('ship', 'ship date'), ('eta', 'estimated arrival date'),
         ('deliv', 'actual delivery timestamp, local +05:30 (blank or epoch placeholder when not delivered)'),
         ('weight', "MISLEADING: gross WEIGHT kept in a legacy 'quantity' field (kg, but lb for FedEx and grams for small Island Couriers parcels)"),
         ('dims', 'parcel dimensions LxWxH (cm, but inches for FedEx and mm for Island Couriers)'),
         ('dist', 'MISLEADING: lane distance in km (miles for FedEx), not metres'),
         ('cost', 'MISLEADING: FREIGHT COST (LKR domestic, USD international), not the goods value'),
         ('status', 'shipment status (header has a trailing space)')]
DOM = {'Kandy': 115, 'Galle': 126, 'Jaffna': 396, 'Kurunegala': 94, 'Matara': 160, 'Batticaloa': 314,
       'Trincomalee': 257, 'Negombo': 37, 'Anuradhapura': 205}
INTL = {'Chennai': 690, 'Dubai': 3290, 'Singapore': 2730, 'Shenzhen': 4250, 'Male': 790}
DEST_VAR = {'Kandy': ['KANDY', 'Kandi'], 'Galle': ['Gall', 'GALLE'], 'Jaffna': ['Jafna', 'Yalpanam'], 'Kurunegala': ['Kurunagala'],
            'Matara': ['Mathara'], 'Batticaloa': ['Batticoloa', "B'caloa"], 'Trincomalee': ['Trinco'], 'Negombo': ['Negambo'],
            'Anuradhapura': ["A'pura", 'Anuradapura'], 'Chennai': ['Madras', 'CHENNAI', 'Chennai, IN'], 'Dubai': ['DXB', 'Dubai UAE'],
            'Singapore': ['SG', 'Singapore '], 'Shenzhen': ['Shenzen', 'SZX'], 'Male': ['Malé', 'Male, MV', 'MLE']}
ORIG_VAR = ['CMB DC', 'Colombo Distribution Centre', 'Col DC', 'Colombo D.C.']
CARR_VAR = {'DHL Express': ['DHL', 'D.H.L', 'dhl express', 'DHL EXP'], 'FedEx': ['Fed Ex', 'FEDEX', 'Federal Express'],
            'Aramex': ['ARAMEX', 'Aramax'], 'Island Couriers': ['Island Courier', 'ISLAND COURIERS', 'Isl. Couriers'],
            'LankaXpress': ['Lanka Xpress', 'LKX', 'lanka xpress']}
STAT_VAR = {'Delivered': [('delivered', 5), ('DLVD', 5), ('POD received', 5), ('Completed', 9)],
            'In Transit': [('in-transit', 5), ('Shipped', 9), ('Dispatched', 9), ('On the way', 5)],
            'Out for Delivery': [('OFD', 5), ('out for delivery', 5)],
            'Exception': [('Hold', 9), ('Issue', 9), ('Customs Hold', 9), ('Delayed', 9)],
            'Returned': [('RTO', 5), ('Returned/Lost', 9)], 'Cancelled': [('Canceled', 5), ('CXL', 5), ('Void', 5)]}
DSTY = ['iso'] * 6 + ['dmy', 'mdy', 'd-mon-yy', 'long', 'compact', 'dot', 'serial', 'unix', 'm/d/yy', 'dow', 'iso_t']
NOTE = {'dmy': 'DD/MM/YYYY', 'mdy': 'MM/DD/YYYY (US)', 'd-mon-yy': 'DD-Mon-YY', 'long': 'Month D, YYYY', 'compact': 'YYYYMMDD',
        'dot': 'DD.MM.YYYY', 'serial': 'Excel serial number', 'unix': 'unix epoch seconds', 'm/d/yy': 'M/D/YY (US, 2-digit year)',
        'dow': 'weekday + D Mon YYYY', 'iso_t': 'ISO timestamp with offset'}


def put_date(r, col, d):
    st = rng.choice(DSTY)
    if st == 'iso': r[col] = d.isoformat(); return
    txt = f'{d.isoformat()}T{rng.randint(7, 19):02d}:{rng.choice([0, 15, 30, 45]):02d}:00+05:30' if st == 'iso_t' else fdate(d, st)
    amb = ' (ambiguous day/month)' if st in ('dmy', 'mdy', 'm/d/yy', 'dot') and d.day <= 12 else ''
    r.put(col, txt, d.isoformat(), 7, NOTE[st] + amb)


def put_deliv(r, t):
    canon = t.strftime('%Y-%m-%d %H:%M'); st = rng.choice(['c'] * 5 + ['dmy', 'us', 'unix', 'utc'])
    if st == 'c': r['deliv'] = canon; return
    u = t - dt.timedelta(hours=5, minutes=30)
    txt, note = {'dmy': (t.strftime('%d/%m/%Y %H:%M'), 'DD/MM/YYYY HH:MM'),
                 'us': (t.strftime('%m/%d/%Y %I:%M %p'), 'MM/DD/YYYY hh:mm AM/PM'),
                 'unix': (str(int(u.replace(tzinfo=dt.timezone.utc).timestamp())), 'unix epoch seconds (UTC)'),
                 'utc': (u.strftime('%Y-%m-%dT%H:%M:%SZ'), 'UTC ISO timestamp (local time is +05:30)')}[st]
    r.put('deliv', txt, canon, 7, note)


rows = []
for i in range(400):
    r = Row(); intl = rng.random() < .35
    dest = rng.choice(list(INTL if intl else DOM)); km = (INTL if intl else DOM)[dest]
    carrier = rng.choice(['DHL Express', 'FedEx', 'Aramex'] if intl else ['Island Couriers', 'LankaXpress', 'Aramex'])
    kg = round(rng.uniform(.5, 120) if intl else rng.choice([rng.uniform(.2, 2), rng.uniform(2, 40)]), 2)
    ship = dt.date(2024, 1, 2) + dt.timedelta(days=rng.randint(0, 178))
    eta = ship + dt.timedelta(days=rng.randint(3, 8) if intl else rng.randint(1, 3))
    status = rng.choices(list(STAT_VAR), [75, 12, 4, 4, 3, 2])[0]
    sid = f'SHP-24-{100 + i * 3:06d}'
    x = rng.random()
    if x < .03: r.put('shp', sid.lower(), sid, 5, 'lower-case ID')
    elif x < .06: r.put('shp', ' ' + sid, sid, 5, 'leading space in ID')
    else: r['shp'] = sid
    oref = f'SO-24-{rng.randint(10000, 99999)}'; x = rng.random()
    if x < .03: r.miss('order', rng, oref)
    elif x < .12: r.put('order', oref.replace('-', ''), oref, 5, 'order ref without dashes')
    elif x < .18: r.put('order', oref[6:], oref, 5, 'order ref without SO-24- prefix')
    else: r['order'] = oref
    org = 'Katunayake Hub' if intl else 'Colombo DC'
    r.put('origin', rng.choice(ORIG_VAR), org, 5, 'origin spelled differently') if not intl and rng.random() < .25 else r.__setitem__('origin', org)
    r.put('dest', rng.choice(DEST_VAR[dest]), dest, 5, 'destination spelled differently') if rng.random() < .25 else r.__setitem__('dest', dest)
    x = rng.random()
    if x < .03: r.miss('carrier', rng, carrier)
    elif x < .3: r.put('carrier', rng.choice(CARR_VAR[carrier]), carrier, 5, 'carrier spelled differently')
    else: r['carrier'] = carrier
    put_date(r, 'ship', ship)
    if rng.random() < .06: r.miss('eta', rng, eta.isoformat(), ['', 'TBD', 'TBC', '-', 'pending'])
    else: put_date(r, 'eta', eta)
    if status == 'Delivered':
        put_deliv(r, dt.datetime.combine(eta + dt.timedelta(days=rng.randint(-1, 3)), dt.time(rng.randint(8, 19), rng.choice([0, 10, 25, 40, 55]))))
    else:
        x = rng.random()
        if x < .2: r.put('deliv', rng.choice(EPOCH_JUNK), '', 17, f'epoch placeholder for a shipment that is {status}')
        elif x < .3: r.put('deliv', '0', '', 2, f'0 used for no delivery date ({status})')
        else: r['deliv'] = ''
    lb = kg * 2.20462; x = rng.random()
    if x < .04: r.miss('weight', rng, f'{kg:.2f}')
    elif carrier == 'FedEx': r.put('weight', f'{lb:.1f}', f'{kg:.2f}', 8, 'pounds, unit not stated (FedEx rows)')
    elif carrier == 'Island Couriers' and kg < 2: r.put('weight', f'{kg * 1000:.0f}', f'{kg:.2f}', 8, 'grams, unit not stated')
    elif carrier == 'Aramex': r.put('weight', rng.choice([f'{kg:.1f} kg', f'{kg:.1f}kg', f'{kg:.1f} KG']), f'{kg:.2f}', 19, 'unit text glued to number')
    elif carrier == 'LankaXpress' and x < .25: r.put('weight', f'{lb:.1f} lbs', f'{kg:.2f}', 19, 'pounds as text')
    else: r['weight'] = f'{kg:.1f}'
    L, W, H = sorted([rng.randint(10, 80) for _ in range(3)], reverse=True); cm = f'{L}x{W}x{H}'
    if rng.random() < .08: r.miss('dims', rng, cm)
    elif carrier == 'FedEx': r.put('dims', f'{L / 2.54:.0f} x {W / 2.54:.0f} x {H / 2.54:.0f}', cm, 8, 'inches, unit not stated')
    elif carrier == 'Island Couriers': r.put('dims', f'{L * 10}x{W * 10}x{H * 10}', cm, 8, 'millimetres, unit not stated')
    elif carrier == 'LankaXpress': r.put('dims', f'{L}*{W}*{H} cm', cm, 5, "different separator + 'cm'")
    else: r['dims'] = cm
    x = rng.random()
    if x < .04: r.put('dist', '0', str(km), 2, '0 used for unknown distance')
    elif carrier == 'FedEx': r.put('dist', f'{km / 1.609:.0f}', str(km), 8, 'miles, unit not stated')
    elif carrier == 'Aramex' and x < .5: r.put('dist', f'{km} km', str(km), 19, "number stored with 'km'")
    else: r['dist'] = str(km)
    if intl:
        usd = round(25 + kg * rng.uniform(4, 9), 2)
        t, note = rng.choice([(f'{usd:.2f}', 'USD amount with no currency in a mostly-LKR column'), (f'USD {usd:.2f}', None),
                              (f'${usd:,.2f}', None), (f'{usd:.2f} USD', None), (f'{usd:.0f}$', None)])
        r.put('cost', t, f'USD {usd:.2f}', 8 if note else 19, note or 'currency text stored with number')
    else:
        lkr = round(350 + kg * rng.uniform(60, 140), -1)
        t, iid, note = money_text(lkr, rng)
        r.put('cost', t, f'LKR {lkr:.2f}', iid, note) if iid else r.__setitem__('cost', t)
    if rng.random() < .3:
        v, iid = rng.choice(STAT_VAR[status]); r.put('status', v, status, iid, 'status label inconsistent / overlapping')
    else: r['status'] = status
    r.ship_d, r.status = ship, status
    rows.append(r)

for r in rng.sample(rows, 4): r.put('weight', rng.choice(['99999', '65535', '-1', '0']), '', 12, 'impossible weight')
for r in rng.sample(rows, 3): r.put('cost', rng.choice(['999999.99', '0.01', '-450']), '', 12, 'implausible freight cost')
for r in rng.sample([x for x in rows if x.status == 'Delivered'], 3):
    r.put('deliv', (dt.datetime.combine(r.ship_d, dt.time(10, 0)) - dt.timedelta(days=rng.randint(3, 30))).strftime('%Y-%m-%d %H:%M'),
          '', 12, 'delivered before it was shipped')
extra = []
for r in rng.sample([x for x in rows if x.status == 'Delivered'], 12):
    d = r.dup('older status row for the same shipment as row {row}; keep the latest')
    d.clear('status'); d.clear('deliv'); d['status'] = rng.choice(['In Transit', 'Dispatched', 'OFD']); d['deliv'] = ''
    extra.append(d)
extra += [r.dup() for r in rng.sample(rows, 10)]
rows += extra
rows.sort(key=lambda r: (r.ship_d, rng.random()))

write(F, COLS, rows, [HDR], header_issues=[(c, 10, m) for c, m in TRUTH] + [
    ('weight', 8, 'no unit: mostly kg, but FedEx rows are lb, small Island Couriers parcels are grams'),
    ('dims', 8, 'no unit: cm, but FedEx = inches, Island Couriers = mm'),
    ('dist', 8, 'no unit: km, but FedEx rows are miles'),
    ('cost', 8, 'no currency: domestic rows LKR, international rows USD')])
flog(F, 10, 'Legacy AS/400-style field codes with no data dictionary. SHDT1-3 are three different dates; only their order '
            '(SHDT1 <= SHDT2, SHDT3 near SHDT2) tells ship date, ETA and delivery apart.')
flog(F, 7, 'SHDT1 / SHDT2 (ship date / ETA) mix 12 formats incl. Excel serials, unix seconds and US vs EU day/month order', 'SHDT1', 6)
flog(F, 17, 'SHDT3 (delivery timestamp) holds 1900/1904/1969/1970 epoch placeholders for undelivered shipments', 'SHDT3', 8)
META[F] = dict(
    title='Shipment tracking log (CONFUSING HEADERS)', rows=len(rows), read='1 header row, UTF-8, two headers have trailing spaces. Rows sorted by real ship date.',
    cols=[(h, m) for h, (c, m) in zip(HDR, TRUTH)],
    notes=['400 shipments + 12 stale status rows (same SHKEY, older status) + 10 exact duplicate scans.',
           'Decoding: SHQTY carries kg/lbs text on some rows (weight), SHSIZ looks like LxWxH, SHMTR matches lane distances (Kandy 115, Jaffna 396).',
           'Units of SHQTY/SHSIZ/SHMTR depend on SHVND (carrier), so the carrier spelling mess also breaks unit recovery.'])
print(F, len(rows), 'rows')
