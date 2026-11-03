"""06 - CONFUSING HEADERS: ERP purchase-order lines exported through pandas + Power Query. Headers are cryptic,
duplicated, multilingual or outright misleading; the data relationships are the only way to decode them."""
import random, datetime as dt
from common import *

F = '06_CONFUSING_HEADERS_erp_po_lines__cryptic_misleading_columns.csv'
rng = random.Random(606)
COLS = ['idx', 'po', 'line', 'vid', 'buyer', 'vname', 'mat', 'desc', 'qty', 'uom', 'total', 'unit', 'tax', 'cur', 'po_date',
        'req_date', 'gr_date', 'gr_qty', 'plant', 'stat', 'terms', 'disc', 'urgent', 'inv', 'pr', 'remarks']
HDR = ['Unnamed: 0', 'DOC', 'ITM', 'LIFNR', 'Vendor', 'Name', 'MAT', 'Description', 'ප්‍රමාණය', 'UoM', 'Price', 'Amount',
       'Value (USD)', 'CUR', 'DT', 'தேதி', 'Date_', 'Recv\nQty', 'WERKS', 'STAT', '', '2', 'x', 'REF', 'REF.1', 'Column1']
TRUTH = [('idx', 'leftover pandas index (0-based, with gaps where rows were filtered) - meaningless'),
         ('po', 'purchase order number'), ('line', 'PO line item number (10, 20, 30 ...)'),
         ('vid', 'vendor/supplier ID (SAP LIFNR, 10-digit zero padded; zeros often stripped)'),
         ('buyer', "MISLEADING: the BUYER (purchasing officer) who raised the PO, not the vendor"),
         ('vname', 'vendor company name'), ('mat', 'material code'), ('desc', 'material description'),
         ('qty', "order quantity (header is Sinhala for 'quantity/amount')"), ('uom', 'unit of measure of the quantity'),
         ('total', 'MISLEADING: net LINE TOTAL = qty x unit price x (1 - discount), not a unit price'),
         ('unit', 'MISLEADING: UNIT PRICE, not a total amount'),
         ('tax', 'MISLEADING: VAT amount in the line currency (18% of line total for LKR lines, 0 for USD imports) - not USD'),
         ('cur', 'currency of Price/Amount/Value'), ('po_date', 'PO creation date'),
         ('req_date', "requested delivery date (header is Tamil for 'date')"), ('gr_date', 'actual goods-receipt date'),
         ('gr_qty', 'quantity received so far'), ('plant', 'receiving plant (1000 Colombo, 1100 Biyagama, 2000 Kandy)'),
         ('stat', 'line status: A=open, B=partially received, C=closed, X=cancelled (plus free-text variants)'),
         ('terms', 'payment terms (column has NO header)'), ('disc', "line discount % (header '2' is a stray value)"),
         ('urgent', 'urgent/expedite flag'), ('inv', "vendor's invoice number for the receipt"),
         ('pr', 'purchase requisition number'), ('remarks', 'free-text remarks (Power Query default column name)')]
VEND = [(f'{100000 + k * 7:010d}', nm, cur) for k, (nm, cur) in enumerate([
    ('Lanka Agro Supplies (Pvt) Ltd', 'LKR'), ('Ceylon Packaging Industries', 'LKR'), ('Meridian Chemicals PLC', 'LKR'),
    ('Pinnacle Steel Traders', 'LKR'), ('Harbour Cold Storage', 'LKR'), ('Evergreen Paper Mills', 'LKR'),
    ('Apex Electricals & Co.', 'LKR'), ('Summit Rubber Products', 'LKR'), ('Nova Glassworks', 'LKR'),
    ('Shenzhen Brightway Machinery Co. Ltd', 'USD'), ('Chennai Polymers Pvt Ltd', 'USD'), ('Royal Spice Exporters', 'LKR')], 1)]
MATS = [('RM-10023', 'Sugar, refined, 50kg bag', 'KG', 230, 260), ('RM-10031', 'Wheat flour, bulk', 'KG', 140, 175),
        ('RM-10044', 'Coconut oil, crude', 'L', 650, 820), ('RM-10052', 'Milk powder, full cream', 'KG', 1450, 1750),
        ('RM-10067', 'Black pepper, whole', 'KG', 1900, 2600), ('PK-20011', 'Carton box 5-ply 18x12x10', 'EA', 85, 140),
        ('PK-20015', 'PET bottle 1L', 'EA', 22, 38), ('PK-20021', 'Shrink film 500mm', 'ROL', 4200, 6100),
        ('PK-20034', 'Label roll, 4-colour', 'ROL', 3100, 4800), ('CH-30002', 'Caustic soda flakes', 'KG', 310, 420),
        ('CH-30009', 'Food-grade sanitizer', 'L', 980, 1350), ('SP-40045', 'Bearing 6204-2RS', 'EA', 650, 1100),
        ('SP-40051', 'V-belt B-52', 'EA', 1200, 1900), ('SP-40066', 'Pneumatic cylinder 50x100', 'EA', 18500, 26500),
        ('SP-40072', 'Conveyor roller 89mm', 'EA', 3400, 5200)]
UOM_VAR = {'KG': ['kg', 'Kilo', 'KGS'], 'EA': ['PCS', 'Nos', 'each', 'ea'], 'L': ['LTR', 'Litre', 'l'], 'ROL': ['Roll', 'RL']}
BUYERS = [('Nadeesha', 'Fernando'), ('Ruwan', 'Jayasinghe'), ('Imran', 'Marikar'), ('Janani', 'Selvaraj'), ('Gayan', 'Herath')]
STAT_VAR = {'A': [('OPEN', 5), ('Open', 5), ('1', 9)], 'B': [('PART', 5), ('Partial', 5), ('2', 9)],
            'C': [('CLSD', 5), ('closed', 5), ('3', 9), ('Done', 9)], 'X': [('CNCL', 5), ('Cancelled', 5), ('DEL', 9)]}

rows, idx = [], 0
for p in range(72):
    po = str(4500012000 + p * 13 + rng.randint(0, 9)); vid, vname, cur = rng.choice(VEND); buyer = rng.choice(BUYERS)
    pod = dt.date(2024, 1, 3) + dt.timedelta(days=rng.randint(0, 230)); plant = rng.choice(['1000', '1000', '1100', '2000'])
    terms = rng.choice(['NT30', 'Net 30', '30', 'NT45', '45 days', 'COD', 'Advance']) if cur == 'LKR' else rng.choice(['LC at sight', 'TT advance', 'D/P'])
    vname_shown = vname if rng.random() < .7 else rng.choice([vname.upper(), vname.replace(' (Pvt) Ltd', ''), vname.replace('&', 'and'), vname[:18]])
    bstyle = rng.choice(NAME_STYLES); po_sci = rng.random() < .1; pr = str(rng.randint(10 ** 11, 10 ** 12 - 1))
    for ln in range(rng.randint(2, 6)):
        r = Row(); idx += rng.choice([1, 1, 1, 2, 3]); r['idx'] = str(idx)
        r.put('po', xl_sci(int(po)), po, 18, 'scientific notation: PO digits lost (recoverable only via other lines of the PO)') if po_sci and rng.random() < .7 else r.__setitem__('po', po)
        it = str((ln + 1) * 10); r.put('line', it + '.0', it, 18, 'int became float (pandas NaN artefact)') if rng.random() < .12 else r.__setitem__('line', it)
        r.put('vid', vid.lstrip('0'), vid, 18, 'leading zeros stripped') if rng.random() < .45 else r.__setitem__('vid', vid)
        txt, iid, note = name_fmt(*buyer, bstyle, rng); r.put('buyer', txt, ' '.join(buyer), iid, note)
        r.put('vname', vname_shown, vname, 5, 'vendor name spelled differently') if vname_shown != vname else r.__setitem__('vname', vname)
        mat, desc, uom, lo, hi = rng.choice(MATS); r['mat'] = mat
        r.miss('desc', rng, desc) if rng.random() < .05 else r.__setitem__('desc', desc)
        base_q = rng.choice([50, 100, 200, 250, 500, 1000, 2000, 5000]) if uom in ('KG', 'L') else rng.choice([5, 10, 20, 50, 100, 500, 1000])
        unit = round(rng.uniform(lo, hi), 2) if cur == 'LKR' else round(rng.uniform(lo, hi) / 300, 2)
        q_show, u_show, uom_show = base_q, unit, uom
        if uom == 'KG' and base_q >= 1000 and rng.random() < .5:
            q_show, u_show, uom_show = base_q / 1000, round(unit * 1000, 2), 'MT'
            r.put('qty', f'{q_show:g}', str(base_q), 8, 'quantity in metric tonnes on this line (UoM=MT), kg elsewhere')
        else: r['qty'] = str(base_q)
        x = rng.random()
        if uom_show == 'MT': r['uom'] = 'MT'
        elif x < .3: r.put('uom', rng.choice(UOM_VAR[uom]), uom, 5, 'unit of measure spelled differently')
        elif x < .36: r.miss('uom', rng, uom)
        else: r['uom'] = uom
        d = rng.choice([0, 0, 0, 2, 5]); tot = round(base_q * unit * (1 - d / 100), 2); r.tot, r.unit_p = tot, unit
        t, iid, note = money_text(tot, rng, ['plain'] * 3 + ['comma', 'rs', 'pad']) if cur == 'LKR' else (f'{tot:.2f}', None, '')
        r.put('total', t, f'{tot:.2f}', iid, note)
        r.put('unit', f'Rs. {u_show:,.2f}', f'{u_show:.2f}', 19, 'currency prefix') if cur == 'LKR' and rng.random() < .2 else r.__setitem__('unit', f'{u_show:.2f}')
        r['tax'] = f'{tot * .18:.2f}' if cur == 'LKR' else '0.00'
        x = rng.random()
        if x < .06: r.miss('cur', rng, cur)
        elif cur == 'LKR' and x < .2: r.put('cur', rng.choice(['Rs', 'RS.', 'SLR', 'LKR ']), 'LKR', 5, 'currency code spelled differently')
        else: r['cur'] = cur
        st = rng.choices('ABCX', [25, 15, 52, 8])[0]; req = pod + dt.timedelta(days=rng.randint(7, 30))
        for col, dd in (('po_date', pod), ('req_date', req)):
            s = rng.choice(['iso', 'iso', 'dmy', 'mdy', 'compact', 'dot', 'serial'])
            r.put(col, fdate(dd, s), dd.isoformat(), 7, s) if s != 'iso' else r.__setitem__(col, dd.isoformat())
        if st in 'BC':
            g = req + dt.timedelta(days=rng.randint(-4, 9)); s = rng.choice(['iso', 'dmy', 'd-mon-yy'])
            r.put('gr_date', fdate(g, s), g.isoformat(), 7, s) if s != 'iso' else r.__setitem__('gr_date', g.isoformat())
            gq = base_q if st == 'C' and rng.random() < .85 else round(base_q * (rng.uniform(1.0, 1.04) if st == 'C' else rng.uniform(.2, .8)))
            r['gr_qty'] = str(gq)
            inv = rng.choice([f'INV-2024-{rng.randint(1, 9999):04d}', str(rng.randint(10 ** 11, 10 ** 12 - 1))])
            r.put('inv', xl_sci(int(inv)), inv, 18, 'scientific notation: invoice no digits lost') if inv.isdigit() and rng.random() < .6 else r.__setitem__('inv', inv)
        else:
            x = rng.random()
            if x < .4: r.put('gr_date', rng.choice(['1970-01-01', '00/01/1900', '1900-01-00']), '', 17, 'epoch placeholder: nothing received')
            else: r['gr_date'] = ''
            r.put('gr_qty', '0', '', 2, 'nothing received yet/cancelled: 0 instead of null'); r['inv'] = ''
        r.put('plant', plant + '.0', plant, 18, 'int became float (pandas NaN artefact)') if rng.random() < .25 else r.__setitem__('plant', plant)
        if rng.random() < .35: v, iid = rng.choice(STAT_VAR[st]); r.put('stat', v, st, iid, 'status code mixed with words/numbers')
        else: r['stat'] = st
        canon = {'30': 'Net 30', 'NT30': 'Net 30', '45 days': 'Net 45', 'NT45': 'Net 45'}.get(terms, terms)
        r.put('terms', terms, canon, 8 if terms == '30' else 5, 'payment terms written differently') if canon != terms else r.__setitem__('terms', terms)
        ds = {0: rng.choice(['0', '', '0%']), 2: rng.choice(['2', '2%', '0.02']), 5: rng.choice(['5', '5%', '0.05'])}[d]
        r.put('disc', ds, str(d), 8 if '.' in ds else 1 if ds == '' else 19 if '%' in ds else None, 'fraction vs percent' if '.' in ds else 'blank = 0?' if ds == '' else 'percent sign stored as text') if ds not in (str(d),) else r.__setitem__('disc', ds)
        u = rng.random() < .15; r.put('urgent', rng.choice(['X', 'x', 'yes', 'Y', '1']) if u else rng.choice(['', '', '', 'N', 'no', '0']), 'Y' if u else 'N', 9, 'flag encoded inconsistently')
        r.put('pr', xl_sci(int(pr)), pr, 18, 'scientific notation: PR digits lost') if rng.random() < .3 else r.__setitem__('pr', pr)
        r['remarks'] = rng.choice(['urgent', 'chk w/ Nimal', 'price as per contract 2023', 'see email', 'DO NOT PAY', 'dup?', 'partial ok']) if rng.random() < .07 else ''
        rows.append(r)

for r in rng.sample(rows, 3): r.put('qty', '99999', r['qty'], 12, 'placeholder quantity')
for r in rng.sample(rows, 2): r.clear('unit'); r.put('unit', '0.01', f'{r.unit_p:.2f}', 12, 'placeholder unit price')
for r in rng.sample(rows, 2): r.clear('total'); r.put('total', f'-{r.tot:.2f}', f'{r.tot:.2f}', 12, 'negative line total on a normal PO line')
for k in sorted(rng.sample(range(len(rows)), 8), reverse=True):
    d = rows[k].dup('same PO line (DOC+ITM) as row {row}: only the index column differs'); d['idx'] = str(int(rows[k]['idx']) + 1000 + k)
    rows.insert(k + rng.randint(1, 6), d)
write(F, COLS, rows, [HDR], bom=True, header_issues=[(c, 10, m) for c, m in TRUTH])
flog(F, 11, "File passed through SAP (LIFNR/WERKS names), pandas ('Unnamed: 0' index, 10.0 floats, '.1' suffix on REF.1) and Power Query "
            "('Column1'), plus Sinhala/Tamil headers from a localised template. No source, extract date or field dictionary.")
flog(F, 10, "Starts with a UTF-8 BOM, so the first header is really '\\ufeffUnnamed: 0'; header 'Recv\\nQty' contains a line break; one header is empty.")
flog(F, 8, "'Value (USD)' is VAT in the line currency (mostly LKR); quantities switch between KG and MT", 'Value (USD)', 13)
META[F] = dict(
    title='ERP purchase-order lines (CONFUSING HEADERS)', rows=len(rows),
    read='UTF-8 WITH BOM. 1 header row, one header has an embedded newline (quoted). 26 columns.',
    cols=[(h.replace('\n', '\\n') or '(empty)', m) for h, (c, m) in zip(HDR, TRUTH)],
    notes=['Decoding checks that work on clean rows: Price = ප්‍රමාණය x Amount x (1 - discount); Value (USD) = 0.18 x Price for LKR lines;',
           'DT <= தேதி; Date_ is blank/epoch exactly when Recv Qty = 0 and STAT is A/X.'])
print(F, len(rows), 'rows')
