"""05 - Product catalog: Excel-mangled codes (dates, sci notation, lost zeros), prices as text, bad categories."""
import random, re, datetime as dt
from common import *

F = '05_CONFUSING_HEADERS_product_catalog__opaque_attribute_ids_excel_mangled_codes.csv'
rng = random.Random(505)
COLS = ['sku', 'ean', 'name', 'brand', 'cat', 'sub', 'pack', 'price', 'cost', 'launch', 'supp', 'hs', 'size', 'status']
HDR = ['ATTR_101', 'ATTR_117', 'ATTR_102@en_LK', 'ATTR_230', 'ATTR_118', 'ATTR_118_1', 'ATTR_305', 'ATTR_410', 'ATTR_410_B',
       'ATTR_512', 'ATTR_620', 'ATTR_621', 'ATTR_306', 'ATTR_900']
TRUTH = [('sku', 'SKU / item code (some mangled into dates or scientific notation)'), ('ean', 'EAN-13 barcode'),
         ('name', 'product name (English, Sri Lanka locale)'), ('brand', 'brand'), ('cat', 'category'), ('sub', 'sub-category'),
         ('pack', 'pack size'), ('price', 'selling price, LKR'),
         ('cost', "MISLEADING: unit COST in LKR, though the code looks like a second price list 'B'"), ('launch', 'launch date'),
         ('supp', 'supplier code (same 3 ID schemes as file 01)'),
         ('hs', 'customs HS tariff code (next to the supplier code; both look like codes)'),
         ('size', 'size variant: clothing size, shoe size or pipe diameter'), ('status', 'lifecycle status')]
P = [('Black Tea', 'Beverages', 'Tea', ['100g', '200g', '400g'], '0902.30', 350, 1500),
     ('Green Tea Bags', 'Beverages', 'Tea', ['25 bags', '50 bags'], '0902.10', 450, 1200),
     ('Instant Coffee', 'Beverages', 'Coffee', ['50g', '100g', '200g'], '2101.11', 600, 2400),
     ('Mango Nectar', 'Beverages', 'Juices', ['200ml', '1L'], '2009.89', 120, 650),
     ('Bottled Water', 'Beverages', 'Water', ['500ml', '1.5L', '5L'], '2201.10', 70, 300),
     ('Coconut Milk', 'Grocery', 'Canned & Packaged', ['400ml', '1L'], '2106.90', 250, 800),
     ('Basmati Rice', 'Grocery', 'Rice & Grains', ['1kg', '5kg'], '1006.30', 500, 3200),
     ('Red Raw Rice', 'Grocery', 'Rice & Grains', ['1kg', '5kg', '10kg'], '1006.30', 220, 2400),
     ('Bee Honey', 'Grocery', 'Spreads', ['250g', '500g'], '0409.00', 900, 2600),
     ('Cinnamon Sticks', 'Grocery', 'Spices', ['50g', '100g'], '0906.11', 400, 1300),
     ('Black Pepper Powder', 'Grocery', 'Spices', ['50g', '100g'], '0904.12', 300, 900),
     ('Chilli Flakes', 'Grocery', 'Spices', ['100g', '250g'], '0904.20', 250, 700),
     ('Cream Crackers', 'Snacks', 'Biscuits', ['190g', '490g'], '1905.90', 180, 520),
     ('Chocolate Biscuits', 'Snacks', 'Biscuits', ['100g', '200g'], '1905.31', 150, 450),
     ('Potato Chips', 'Snacks', 'Chips', ['50g', '150g'], '2005.20', 150, 600),
     ('Fresh Milk', 'Dairy', 'Milk', ['180ml', '1L'], '0401.20', 120, 600),
     ('Set Yoghurt', 'Dairy', 'Yoghurt', ['80g', '4 x 80g'], '0403.20', 70, 320),
     ('Cheddar Cheese', 'Dairy', 'Cheese', ['200g', '500g'], '0406.90', 900, 2800),
     ('Dishwash Liquid', 'Household', 'Cleaning', ['500ml', '1L'], '3402.20', 300, 900),
     ('Floor Cleaner', 'Household', 'Cleaning', ['500ml', '1L', '2L'], '3402.20', 350, 1300),
     ('Toilet Tissue', 'Household', 'Paper', ['4 rolls', '10 rolls'], '4818.10', 400, 1600),
     ('Mosquito Coil', 'Household', 'Pest Control', ['10 coils'], '3808.91', 180, 300),
     ('Herbal Shampoo', 'Personal Care', 'Hair', ['80ml', '180ml', '400ml'], '3305.10', 250, 1500),
     ('Toothpaste', 'Personal Care', 'Oral', ['70g', '120g'], '3306.10', 180, 450),
     ('Sandalwood Soap', 'Personal Care', 'Bath', ['70g', '3 x 70g'], '3401.11', 90, 320),
     ('Baby Diapers', 'Baby', 'Diapers', ['S 40', 'M 36', 'L 32'], '9619.00', 2200, 4800),
     ('Baby Wipes', 'Baby', 'Wipes', ['20 sheets', '80 sheets'], '3307.90', 250, 900),
     ('LED Bulb', 'Electrical', 'Lighting', ['9W', '12W', '18W'], '8539.50', 450, 1400),
     ('AA Batteries', 'Electrical', 'Batteries', ['2 pk', '4 pk'], '8506.10', 300, 1100),
     ('PVC Elbow Fitting', 'Hardware', 'Plumbing', ['1 pc'], '3917.40', 60, 240),
     ('Cotton T-Shirt', 'Apparel', 'Tops', ['1 pc'], '6109.10', 1200, 3500),
     ('Rubber Slippers', 'Footwear', 'Slippers', ['1 pair'], '6402.20', 500, 1500),
     ('Steel Water Bottle', 'Home', 'Kitchen', ['500ml', '750ml', '1L'], '7323.93', 1500, 4200)]
BRANDS = {'Beverages': ['PureLeaf Ceylon', 'Highland Gold', 'Ceyfresh'], 'Grocery': ['Ceyfresh', 'Raja Spice', 'Golden Crown'],
          'Snacks': ['IslandBake', 'SunCrest'], 'Dairy': ['Lankamilk', 'Hill Valley Farms'], 'Household': ['HomeShine', 'KleenPro'],
          'Personal Care': ['SoftCare', 'Herbaline', 'Crème Délice'], 'Baby': ['BabyBloom', 'KidzJoy'], 'Electrical': ['VoltMax', 'BrightLine'],
          'Hardware': ['FlowFit'], 'Apparel': ['Island Threads'], 'Footwear': ['StepEasy'], 'Home': ['KitchenPro', 'HomeShine']}
SIZES = {'Cotton T-Shirt': ['S', 'M', 'L', 'XL'], 'Rubber Slippers': ['7', '8', '9', '10'], 'PVC Elbow Fitting': ['1/2', '3/4', '1']}
SIZE_VAR = {'S': ['Small', 'sm'], 'M': ['Medium', 'M '], 'L': ['Large', 'lg'], 'XL': ['Extra Large', 'X-L']}
CAT_SYN = {'Beverages': 'Drinks', 'Grocery': 'Groceries', 'Snacks': 'Food', 'Household': 'Home Care', 'Personal Care': 'Health & Beauty', 'Home': 'Household'}
STATUS = [('Active', None), ('active', 5), ('ACTIVE', 5), ('Discontinued', None), ('Disc.', 5), ('D/C', 5), ('Delisted', 5),
          ('Seasonal', 9), ('Out of Stock', 9), ('Y', 9)]


def ean13(body12):
    s = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(body12))
    return body12 + str((10 - s % 10) % 10)


def brand_var(b):
    v = rng.choice(['upper', 'lower', 'space', 'typo', 'legal'] + (['moji', 'ascii'] * 2 if 'è' in b else []))
    return {'upper': b.upper(), 'lower': b.lower(), 'space': b.replace(' ', '') if ' ' in b else b[:3] + ' ' + b[3:],
            'typo': b[:-2] + b[-1] + b[-2], 'legal': b + ' (Pvt) Ltd', 'moji': b.encode('utf-8').decode('latin-1'),
            'ascii': 'Creme Delice'}[v], 'mojibake (UTF-8 read as Latin-1)' if v == 'moji' else 'brand spelled differently'


rows, n = [], 0
for item, cat, sub, packs, hs, lo, hi in P:
    for pack in packs:
        for size in SIZES.get(item, [None]):
            for brand in rng.sample(BRANDS[cat], rng.randint(1, len(BRANDS[cat]))):
                n += 1; r = Row(); r.cat = cat
                fam = rng.random()
                if fam < .55: sku = f'{cat[:3].upper()}-{n:05d}'
                elif fam < .78: sku = f'{n * 37 + 10000:08d}'
                elif fam < .86: sku = rng.choice(['DEC', 'MAR', 'APR', 'SEP', 'OCT']) + str(rng.randint(1, 28))
                else: sku = f'{rng.randint(1, 9)}E{rng.choice(["05", "10", "12", "3"])}'
                if sku[0] == '0' and rng.random() < .8: r.put('sku', sku.lstrip('0'), sku, 18, 'leading zeros stripped by spreadsheet')
                elif sku[:3] in ('DEC', 'MAR', 'APR', 'SEP', 'OCT'): r.put('sku', f'{int(sku[3:])}-{sku[:3].title()}', sku, 18, 'spreadsheet turned the code into a date')
                elif 'E' in sku and sku[0].isdigit(): r.put('sku', f'{float(sku):.2E}', sku, 18, 'spreadsheet read the code as scientific notation')
                else: r['sku'] = sku
                ean = ean13('479' + ''.join(rng.choice('0123456789') for _ in range(9))); r.ean_true = ean; x = rng.random()
                if x < .2: r.put('ean', xl_sci(int(ean)), ean, 18, 'scientific notation: last digits lost, unrecoverable')
                elif x < .26: r.miss('ean', rng, ean, ['', 'N/A', 'NO BARCODE', 'TBA', '-'])
                elif x < .3: u = ean13('0' + ''.join(rng.choice('0123456789') for _ in range(11))); r.put('ean', u.lstrip('0'), u, 18, 'leading zero stripped (13 -> 12 digits)')
                else: r['ean'] = ean
                nm = f'{brand} {item} {pack}' + (f' - {size}' if size else ''); x = rng.random()
                if x < .08: r.put('name', nm.upper(), nm, 5, 'upper-cased')
                elif x < .14: r.put('name', nm[:22], nm, 5, 'truncated at 22 characters')
                elif x < .2: r.put('name', nm.replace(brand + ' ', ''), nm, 5, 'brand missing from name')
                elif x < .25: r.put('name', nm.replace(' ', '  ', 2) + ' ', nm, 5, 'extra spaces')
                else: r['name'] = nm
                if rng.random() < .25: t, note = brand_var(brand); r.put('brand', t, brand, 5, note)
                else: r['brand'] = brand
                x = rng.random()
                if x < .07: r.put('cat', rng.choice(['New Arrivals', 'Sale', 'Imported', 'Top Seller']), cat, 9, 'promotion/attribute used as category')
                elif x < .13: r.put('cat', rng.choice(['Other', 'Misc', 'Uncategorized']), cat, 9, 'catch-all category')
                elif x < .2 and cat in CAT_SYN: r.put('cat', CAT_SYN[cat], cat, 9 if CAT_SYN[cat] in ('Food', 'Household') else 5, 'synonym / overlapping category')
                elif x < .23: r.miss('cat', rng, cat)
                else: r['cat'] = cat
                x = rng.random()
                if x < .07: r.put('sub', cat, sub, 9, 'sub-category just repeats a category')
                elif x < .12: r.miss('sub', rng, sub)
                else: r['sub'] = sub
                x = rng.random(); num = ''.join(ch for ch in pack.split(' x ')[-1] if ch.isdigit() or ch == '.')
                if x < .15 and num and pack[-1].isalpha() and ' ' not in pack: r.put('pack', num, pack, 8, 'unit stripped (g? ml? kg?)')
                elif x < .25: r.put('pack', re.sub(r'(\d)([A-Za-z])', r'\1 \2', pack).upper(), pack, 5, 'same size written differently')
                else: r['pack'] = pack
                price = round(rng.uniform(lo, hi), -1) - .01 if rng.random() < .3 else round(rng.uniform(lo, hi), -1); r.price = price
                t, iid, note = money_text(price, rng); r.put('price', t, f'{price:.2f}', iid, note)
                cost = round(price * rng.uniform(.55, .75), 2); x = rng.random()
                if x < .04: r.put('cost', rng.choice(['#REF!', '#VALUE!', '#DIV/0!']), f'{cost:.2f}', 12, 'spreadsheet error exported as value')
                elif x < .08: r.put('cost', '0', '', 2, f'cost unknown, 0 entered (true {cost:.2f}) -> fake 100% margin')
                else: r['cost'] = f'{cost:.2f}'
                ld = dt.date(2016, 1, 1) + dt.timedelta(days=rng.randint(0, 3100)); x = rng.random()
                if x < .07: r.put('launch', rng.choice(EPOCH_JUNK[:6]), '', 17, f'epoch placeholder (true {ld})')
                elif x < .5:
                    st = rng.choice(['dmy', 'mdy', 'd-mon-y', 'serial', 'long', 'compact'])
                    r.put('launch', fdate(ld, st), ld.isoformat(), 7, st + (' (ambiguous)' if st in ('dmy', 'mdy') and ld.day <= 12 else ''))
                else: r['launch'] = ld.isoformat()
                sc = rng.choice([f'{100000 + rng.randint(1, 120) * 7:010d}', f'SUP-{rng.randint(1001, 1060)}', str(4000 + rng.randint(1, 30) * 3)])
                r.put('supp', sc.lstrip('0'), sc, 18, 'leading zeros stripped') if sc[0] == '0' and rng.random() < .5 else r.__setitem__('supp', sc)
                mangled = hs.lstrip('0').rstrip('0').rstrip('.')
                r.put('hs', mangled, hs, 18, 'HS code read as a number: leading/trailing zeros lost') if mangled != hs and rng.random() < .6 else r.__setitem__('hs', hs)
                if size == '1/2': r.put('size', '2-Jan', '1/2', 18, 'fraction turned into a date')
                elif size == '3/4': r.put('size', '4-Mar', '3/4', 18, 'fraction turned into a date')
                elif item == 'Rubber Slippers': r.put('size', size, size, 8, 'shoe size system not stated (UK/US/EU?)')
                elif size in SIZE_VAR and rng.random() < .4: r.put('size', rng.choice(SIZE_VAR[size]), size, 5, 'size label spelled differently')
                else: r['size'] = size or ''
                st, iid = rng.choices(STATUS, [40, 6, 4, 8, 3, 2, 2, 3, 3, 2])[0]
                r.put('status', st, {'Disc.': 'Discontinued', 'D/C': 'Discontinued', 'Delisted': 'Discontinued'}.get(st, st.strip().title() if iid == 5 else ''), iid,
                      'status spelled differently' if iid == 5 else 'availability/flag mixed into lifecycle status') if iid else r.__setitem__('status', st)
                rows.append(r)

for r in rng.sample(rows, 5): r.clear('price'); r.put('price', rng.choice(['0.01', '99999', '-1', '0']), f'{r.price:.2f}', 12, 'implausible price')
for r in rng.sample([r for r in rows if r['ean'] == r.ean_true], 3): r.put('ean', rng.choice(['0000000000000', '9999999999999', '1234567890128']), r.ean_true, 12, 'placeholder barcode')
a, b = rng.sample([r for r in rows if r['ean'] == r.ean_true], 2); b.put('ean', a['ean'], b.ean_true, 4, 'barcode copied from a different product')
extra = []
for r in rng.sample(rows, 6):
    d = r.dup('same product as row {row} listed again under a new SKU'); d.clear('sku'); d.clear('name')
    d['sku'] = f'{r.cat[:3].upper()}-{90000 + len(extra)}'; d.put('name', r['name'].replace(' ', '  ', 1).lower(), r['name'], 5, 'spelled differently')
    extra.append(d)
extra += [r.dup() for r in rng.sample(rows, 5)]
rows += extra
rng.shuffle(rows)
write(F, COLS, rows, [HDR], header_issues=[(c, 10, m) for c, m in TRUTH] + [
    ('pack', 8, 'pack size unit sometimes missing'), ('price', 8, 'no currency (LKR)')])
flog(F, 10, 'PIM/EAV export: headers are opaque attribute IDs with no attribute dictionary. ATTR_410 vs ATTR_410_B '
            'and ATTR_620 vs ATTR_621 are deliberately hard to tell apart.')
flog(F, 18, 'Codes that were opened in Excel: ATTR_101 SKU (lost zeros, dates like 3-Dec, 1.00E+10), ATTR_117 barcode (4.79123E+12), '
            'ATTR_621 HS code (902.3), ATTR_306 size (2-Jan)')
META[F] = dict(
    title='Product catalog / item master (CONFUSING HEADERS)', rows=len(rows), read='1 header row, UTF-8 (one brand is mojibake on purpose).',
    cols=[(h, m) for h, (c, m) in zip(HDR, TRUTH)],
    notes=['Decoding: on clean rows ATTR_410_B is 55-75% of ATTR_410 (cost vs price); ATTR_117 is 13 digits starting 479 (Sri Lanka GS1); '
           'ATTR_621 looks like 0902.30 (HS chapter.heading).',
           'Good file for AI categorisation: real category is recoverable from ATTR_102@en_LK (name) even when ATTR_118 is junk.',
           '6 products are listed twice under a new SKU; 5 rows are exact duplicates.'])
print(F, len(rows), 'rows')
