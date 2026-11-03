"""09 - POS transaction lines for 'FY2024 Q1' that went through Excel 97: exactly 65,536 rows incl. header,
cut off mid-transaction in early February. Excel also rewrote dates, line numbers and phone numbers."""
import random, datetime as dt
from collections import Counter
from common import *

F = '09_pos_transactions__truncated_at_65536_rows_excel97_limit.csv'
rng = random.Random(909)
COLS = ['period', 'txn', 'line', 'dt', 'store', 'cashier', 'sku', 'qty', 'price', 'disc', 'total', 'pay', 'phone']
HDR = ['fiscal_period', 'txn_id', 'line', 'txn_datetime', 'store', 'cashier', 'sku', 'qty', 'unit_price', 'discount',
       'line_total', 'payment_method', 'customer_phone']
CI = {c: i + 1 for i, c in enumerate(COLS)}
LIMIT = 65535
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
STORES = {'COL03': ['Colombo 03', 'Kollupitiya'], 'COL07': ['Colombo 07', 'Col-7'], 'KDY01': ['Kandy', 'KANDY CITY'],
          'GAL01': ['Galle', 'Galle Fort'], 'NEG01': ['Negombo', 'Negambo'], 'JAF01': ['Jaffna', 'Yalpanam']}
PAY = {'Cash': ['CASH', 'cash'], 'Card': ['Visa', 'Master', 'Credit Card', 'Debit', 'Card/Cash'], 'QR': ['LankaQR', 'QR Pay'],
       'Voucher': ['Gift Voucher', 'Other']}
SKUS = [(f'{p}-{n:05d}', round(rng.uniform(lo, hi), -1)) for p, lo, hi in
        [('BEV', 90, 1800), ('GRO', 150, 3200), ('SNA', 100, 650), ('DAI', 80, 2800), ('HOU', 180, 1600), ('PER', 90, 1500)]
        for n in rng.sample(range(1, 400), 12)] + [(f'VEG-{n:04d}', round(rng.uniform(180, 1400), -1)) for n in range(1, 9)]
VAR = Counter()


def var(r, col, dirty, clean, iid, note):
    r[col] = dirty; VAR[(col, dirty, clean, iid, note)] += 1


cashiers = {s: [(f, l, *name_fmt(f, l, rng.choice(NAME_STYLES), rng)) for f, l in [(rng.choice(FIRST), rng.choice(LAST)) for _ in range(3)]] for s in STORES}
rows = []
day = dt.date(2024, 1, 1)
while len(rows) < LIMIT + 400:
    for s in STORES:
        t = dt.datetime.combine(day, dt.time(8, 0)); seq = 0
        while True:
            t += dt.timedelta(seconds=rng.randint(60, 560))
            if t.hour >= 20: break
            seq += 1; n = rng.choices([1, 2, 3, 4, 5, 6], [30, 25, 18, 12, 9, 6])[0]
            fn, ln, ctxt, ciid, cnote = rng.choice(cashiers[s]); pay = rng.choices(list(PAY), [45, 35, 15, 5])[0]
            phone = mobile(rng) if rng.random() < .15 else ''
            for i in range(1, n + 1):
                sku, price = rng.choice(SKUS); veg = sku.startswith('VEG')
                qty = round(rng.uniform(.2, 2.5), 2) if veg else rng.choices([1, 2, 3, 4, 6, 12], [60, 20, 8, 5, 4, 3])[0]
                disc = round(qty * price * .1, 2) if rng.random() < .08 else 0
                r = Row(period='2024-Q1', txn=f'{s}-{t:%Y%m%d}-{seq:04d}', store=s, sku=sku, qty=f'{qty:g}')
                r.t, r.i, r.n, r.s = t + dt.timedelta(seconds=i), i, n, s
                r['line'] = f'{n}-{MON[i - 1]}'
                r['dt'] = f'{t.month}/{t.day}/{t.year} {t.hour}:{t.minute:02d}'
                var(r, 'cashier', ctxt, f'{fn} {ln}', ciid, cnote) if ciid else r.__setitem__('cashier', ctxt)
                r['price'] = f'Rs.{price:.2f}' if s == 'KDY01' else f'{price:.2f}'
                r['disc'] = '' if not disc else ('10%' if s == 'GAL01' else f'{disc:.2f}')
                r['total'] = f'{qty * price - disc:.2f}'
                if rng.random() < .3: var(r, 'store', STORES[s][0 if rng.random() < .7 else 1], s, 5, 'store name instead of / besides code')
                if rng.random() < .25: var(r, 'pay', rng.choice(PAY[pay]), pay, 9 if pay in ('Card', 'Voucher') else 5, 'payment label overlaps / inconsistent')
                else: r['pay'] = pay
                r['phone'] = phone[1:] if phone else ''
                r.true = (qty, price, disc)
                rows.append(r)
    day += dt.timedelta(days=1)
rows.sort(key=lambda r: (r.t, r.s))
# sparse cell issues
for r in rng.sample(rows[:LIMIT], 260):
    r.miss('cashier', rng) if rng.random() < .5 else r.put('total', f'{r.true[0] * r.true[1] - r.true[2] + rng.choice([-.5, 1, 10, 100]):.2f}',
                                                          f'{r.true[0] * r.true[1] - r.true[2]:.2f}', 14, 'line_total != qty x unit_price - discount')
for r in rng.sample(rows[:LIMIT], 30): r.put('qty', rng.choice(['999', '9999', '-1', '0']), r['qty'], 12, 'implausible quantity')
for r in rng.sample([r for r in rows[:LIMIT] if r['phone']], 20): r.put('phone', rng.choice(['777777777', '711111111', '0', '123456789']), '', 12, 'placeholder phone')
reset = [r for r in rows[:LIMIT] if r.s == 'NEG01' and r.t.date() == dt.date(2024, 1, 17) and 9 <= r.t.hour < 11]
for r in reset:
    f = dt.datetime(1970, 1, 1, 5, 30) + (r.t - dt.datetime(2024, 1, 17, 9))
    r.put('dt', f'{f.month}/{f.day}/{f.year} {f.hour}:{f.minute:02d}', r.t.strftime('%Y-%m-%d %H:%M'), 17, 'terminal clock reset: unix epoch in local time')
# duplicates: double-posted lines + a re-imported batch
for k in sorted(rng.sample(range(LIMIT - 500), 120), reverse=True): rows.insert(k + 1, rows[k].dup('double-posted line: duplicate of row {row}'))
b = next(i for i, r in enumerate(rows) if r.t.date() == dt.date(2024, 1, 9) and r.t.hour == 15)
rows[b + 60:b + 60] = [r.dup('batch re-imported: duplicate of row {row}') for r in rows[b:b + 60]]
while rows[LIMIT - 1].i == rows[LIMIT - 1].n:                       # make sure the cut lands mid-transaction
    k = rng.randrange(1000, 20000); rows.insert(k + 1, rows[k].dup('double-posted line: duplicate of row {row}'))
rows = rows[:LIMIT]
last = rows[-1]
write(F, COLS, rows, [HDR])
for (col, dirty, clean, iid, note) in VAR:
    n = sum(r.get(col) == dirty for r in rows)
    if n: flog(F, iid, f'{note} ({n} rows)', HDR[CI[col] - 1], CI[col], dirty, clean)
flog(F, 15, f'Exactly 65,536 rows incl. header (Excel 97-2003 sheet limit). Data stops at {last.t:%Y-%m-%d %H:%M} in the middle of '
            f'{last["txn"]} (line {last.i} of {last.n}) although fiscal_period says 2024-Q1 (should run to 2024-03-31). Ask for the rest.')
flog(F, 18, "Excel turned 'line i/n' into a date: '3-Feb' means line 2 of 3 (day = lines in txn, month = line no.)", 'line', 3)
flog(F, 7, 'Excel rewrote timestamps as US M/D/YYYY H:MM (seconds lost); 2/1/2024 is 1 Feb, not 2 Jan', 'txn_datetime', 4)
flog(F, 18, 'customer_phone lost its leading 0 everywhere (771234567 = 0771234567)', 'customer_phone', 13)
flog(F, 19, "KDY01 rows store unit_price as text with 'Rs.' prefix", 'unit_price', 9)
flog(F, 8, "discount is an LKR amount everywhere except GAL01, where it is a '10%' string", 'discount', 10)
flog(F, 8, 'VEG-* SKUs are sold by weight: qty is kg there, units elsewhere', 'qty', 8)
flog(F, 13, 'txn_datetime only has minute resolution (Excel dropped the seconds): lines and transactions within the same minute cannot be ordered', 'txn_datetime', 4)
META[F] = dict(
    title='POS transaction lines - truncated at 65,536 rows', rows=len(rows), read='1 header row + 65,535 data rows, UTF-8.',
    cols=list(zip(HDR, ['fiscal period label', 'transaction ID (store-date-seq)', 'line i of n (mangled into a date)', 'transaction time',
                        'store code', 'cashier', 'SKU', 'quantity', 'unit price LKR', 'discount', 'line total LKR', 'payment method',
                        'loyalty customer mobile'])),
    notes=['The single most important finding is truncation: row count = old Excel limit and the period is incomplete.'])
print(F, len(rows), 'rows')
