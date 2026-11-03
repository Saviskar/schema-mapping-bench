"""08 - CONFUSING HEADERS: cold-chain temperature logger feed (5 trucks, 15-min readings). One-letter headers,
per-device units/time formats, hardware sentinel values, clock resets, gaps and re-sent readings."""
import random, datetime as dt, math
from common import *

F = '08_CONFUSING_HEADERS_coldchain_sensor_log__cryptic_columns_sentinel_values.csv'
rng = random.Random(808)
COLS = ['id', 'dev', 't', 'v1', 'v2', 'v3', 's', 'f', 'loc', 'ref', 'fw', 'z', 'u12']
HDR = ['id', 'dev', 't', 'v1', 'v2', 'v3', 's', 'f', 'loc', 'ref', 'fw', 'z', 'Unnamed: 12']
TRUTH = [('id', 'per-device reading sequence number (NOT unique; TL-0044 restarts at 1 after a reboot)'),
         ('dev', 'logger/device ID, written several ways'),
         ('t', "reading TIMESTAMP (not temperature!): format and timezone differ per device"),
         ('v1', 'air temperature: deg C, except TL-0045 which reports deg F'),
         ('v2', 'relative humidity: %, except TL-0043 which reports a 0-1 fraction'),
         ('v3', 'battery: volts, except TL-0046 which reports millivolts'),
         ('s', 'cellular signal: RSSI dBm (negative), except TL-0045 which reports modem CSQ 0-31 (99 = unknown)'),
         ('f', 'status bitmask: bit0 = door open, bit1 = temperature alarm; written as int, hex or words'),
         ('loc', "GPS position 'lat,lon' in ONE field (sometimes swapped, DMS, rounded or 0,0)"),
         ('ref', 'shipment reference (same scheme as file 02 SHKEY)'), ('fw', 'firmware version (1.10 got turned into 1.1)'),
         ('z', 'second probe: product core temperature in deg C, only on dual-probe loggers TL-0042 and TL-0046'),
         ('u12', "empty spill-over column; 'ALM' typed in by an operator on some excursion rows")]
START = dt.datetime(2024, 5, 10)
ROUTES = {'TL-0042': ((6.9271, 79.8612), (7.2906, 80.6337)), 'TL-0043': ((6.9271, 79.8612), (6.0535, 80.2210)),
          'TL-0044': ((7.2906, 80.6337), (8.3114, 80.4037)), 'TL-0045': ((6.9271, 79.8612), (9.6615, 80.0255)),
          'TL-0046': ((6.9271, 79.8612), (7.2083, 79.8358))}
DEV_VAR = {'TL-0042': ['tl42', '42', 'TL0042'], 'TL-0043': ['TL-43', 'tl-0043'], 'TL-0044': ['TL0044', '44'],
           'TL-0045': ['tl-0045', 'TL 0045'], 'TL-0046': ['TL0046', '46']}
FW = {'TL-0042': ('1.10', '1.1'), 'TL-0043': ('2.0.1', '2.0.1'), 'TL-0044': ('2.0.1', 'v2.0.1'), 'TL-0045': ('1.9', '1.9'), 'TL-0046': ('1.10', None)}
SHP = {d: f'SHP-24-{n:06d}' for d, n in zip(ROUTES, [811, 973, 1012, 493, 838])}


def tfmt(dev, t):
    loc = t + dt.timedelta(hours=5, minutes=30); ep = int(t.replace(tzinfo=dt.timezone.utc).timestamp())
    return {'TL-0042': t.strftime('%Y-%m-%dT%H:%M:%SZ'), 'TL-0043': loc.strftime('%Y-%m-%d %H:%M:%S'),
            'TL-0044': loc.strftime('%d/%m/%Y %H:%M'), 'TL-0045': str(ep), 'TL-0046': str(ep * 1000)}[dev]


def dms(v, pos, neg):
    d = int(abs(v)); m = int((abs(v) - d) * 60); s = (abs(v) - d - m / 60) * 3600
    return f'{d}°{m:02d}\'{s:04.1f}"{pos if v >= 0 else neg}'


rows = []
for dev, (a, b) in ROUTES.items():
    seq, temp, door_until, reboot = 0, 4.5, -1, None
    for k in range(384):
        t = START + dt.timedelta(minutes=15 * k)
        if dev == 'TL-0043' and 104 <= k < 128: continue                       # 6-hour modem outage
        if dev == 'TL-0046' and k > 248: break                                # battery died
        if rng.random() < .01: continue                                       # random dropped reading
        seq += 1
        if dev == 'TL-0044' and k >= 230 and reboot is None: seq, reboot = 1, k                  # reboot: sequence + clock reset
        if rng.random() < .012: door_until = k + rng.randint(2, 4)
        door = k <= door_until
        temp += (.9 if door else 0) + (4.5 - temp) * .25 + rng.gauss(0, .25); temp = min(temp, 13)
        alarm = temp > 8
        r = Row(); r.t, r.dev, r.k = t, dev, k
        r['id'] = str(seq)
        r.put('dev', rng.choice(DEV_VAR[dev]), dev, 5, 'device ID written differently') if rng.random() < .25 else r.__setitem__('dev', dev)
        if reboot is not None and k < reboot + 8:
            fake = dt.datetime(1970, 1, 1) + dt.timedelta(minutes=15 * (k - reboot))
            r.put('t', fake.strftime('%d/%m/%Y %H:%M'), t.strftime('%Y-%m-%dT%H:%M:%SZ'), 17, 'clock reset to unix epoch after reboot (true time recoverable from sequence)')
        else: r['t'] = tfmt(dev, t)
        r['v1'] = f'{temp * 9 / 5 + 32:.1f}' if dev == 'TL-0045' else f'{temp:.1f}'
        rh = min(98, max(40, 78 + rng.gauss(0, 6) + (8 if door else 0)))
        r['v2'] = f'{rh / 100:.2f}' if dev == 'TL-0043' else f'{rh:.0f}'
        bat = 4.15 - (.0021 if dev != 'TL-0046' else .0034) * k + rng.gauss(0, .01)
        r['v3'] = f'{bat * 1000:.0f}' if dev == 'TL-0046' else f'{bat:.2f}'
        dbm = int(rng.gauss(-82, 9)); r['s'] = str(max(0, min(31, (dbm + 113) // 2))) if dev == 'TL-0045' else str(dbm)
        bits = int(door) | (2 * int(alarm)); fx = rng.random()
        if fx < .2: r.put('f', f'0x{bits:02X}', str(bits), 9, 'hex instead of int')
        elif fx < .3 and bits: r.put('f', 'DOOR' if bits == 1 else 'ALM' if bits == 2 else 'DOOR+ALM', str(bits), 9, 'word instead of bitmask')
        elif fx < .35 and not bits: r.put('f', 'OK', '0', 9, 'word instead of bitmask')
        else: r['f'] = str(bits)
        p = min(1, k / 300); lat = a[0] + (b[0] - a[0]) * p + rng.gauss(0, .0004); lon = a[1] + (b[1] - a[1]) * p + rng.gauss(0, .0004)
        canon = f'{lat:.4f},{lon:.4f}'; x = rng.random()
        if dev == 'TL-0044': r.put('loc', f'{lat:.1f},{lon:.1f}', canon, 13, 'rounded to 0.1 deg (~11 km)')
        elif x < .03: r.put('loc', '0,0', '', 12, "'null island' 0,0 = no GPS fix")
        elif x < .07: r.put('loc', f'{lon:.4f},{lat:.4f}', canon, 5, 'lat/lon swapped')
        elif x < .1: r.put('loc', f"{dms(lat, 'N', 'S')} {dms(lon, 'E', 'W')}", canon, 5, 'degrees-minutes-seconds text')
        elif x < .13: r.miss('loc', rng, canon)
        else: r['loc'] = canon
        ref = SHP[dev]; r.put('ref', ref[7:].lstrip('0'), ref, 18, 'numeric part only, zeros lost') if dev == 'TL-0045' else r.__setitem__('ref', ref)
        fw_true, fw_show = FW[dev]
        if fw_show is None: fw_show = rng.choice(['1.10', '1.1'])
        r.put('fw', fw_show, fw_true, 18 if fw_show == '1.1' else 5, '1.10 read as a number' if fw_show == '1.1' else "'v' prefix") if fw_show != fw_true else r.__setitem__('fw', fw_show)
        r['z'] = f'{4.5 + (temp - 4.5) * .35 + rng.gauss(0, .1):.1f}' if dev in ('TL-0042', 'TL-0046') else ''
        r['u12'] = 'ALM' if alarm and rng.random() < .4 else ''
        r.temp, r.rh, r.bat = temp, rh, bat
        rows.append(r)

clean = [r for r in rows if not any(i[0] in ('v1', 'v2', 'v3', 's') for i in r.issues)]; rng.shuffle(clean); pool = iter(clean)


def take(n, cond=lambda r: True):
    out = []
    while len(out) < n:
        r = next(pool)
        if cond(r): out.append(r)
    return out


for r in take(6): r.put('v1', '-127.0', '', 12, 'DS18B20 "sensor disconnected" sentinel')
for r in take(4): r.put('v1', '85.0', '', 12, 'DS18B20 power-on-reset value, not a real reading')
for r in take(3): r.put('v1', rng.choice(['3276.7', '-3276.8']), '', 12, 'int16/10 overflow')
for r in take(6, lambda r: r.dev != 'TL-0045'):
    r.put('v1', rng.choice([f'{r.temp:.1f}°C', f'{r.temp:.1f}'.replace('.', ','), f' {r.temp:.1f} C']), f'{r.temp:.1f}', 19, 'temperature stored as text')
for r in take(3): r.put('v2', '255', '', 12, 'uint8 max = read error')
for r in take(9): r.put('v2', rng.choice(['', 'nan', '-']), '', 1, 'missing humidity')
for r in take(5): r.put('v3', '0', '', 2, '0 = battery not read')
for r in take(8, lambda r: r.dev != 'TL-0045'): r.put('s', '0', '', 2, '0 = no signal reading (real values are negative dBm)')
for r in take(4, lambda r: r.dev == 'TL-0045'): r.put('s', '99', '', 12, "modem CSQ 99 = 'not known'")
resend = [r.dup('re-sent after the TL-0043 modem outage: duplicate of row {row}') for r in rows if r.dev == 'TL-0043' and 96 <= r.k < 104]
for d in resend: d.sort_t = START + dt.timedelta(minutes=15 * 128)
for r in rng.sample([r for r in rows if r.dev == 'TL-0045'], 5): d = r.dup(); d.sort_t = r.t + dt.timedelta(minutes=1); resend.append(d)
for r in rows: r.sort_t = r.t
rows += resend
rows.sort(key=lambda r: (r.sort_t, r.dev))
write(F, COLS, rows, [HDR], header_issues=[(c, 10, m) for c, m in TRUTH])
for dev, fmt in [('TL-0042', 'ISO 8601 UTC (canonical)'), ('TL-0043', 'local Sri Lanka time (+05:30) without offset'),
                 ('TL-0044', 'DD/MM/YYYY HH:MM local time (+05:30)'), ('TL-0045', 'unix epoch SECONDS'), ('TL-0046', 'unix epoch MILLISECONDS')]:
    flog(F, 7, f'rows from {dev}: t is {fmt}', 't', 3)
flog(F, 8, 'TL-0045 v1 in deg F; TL-0043 v2 as fraction; TL-0046 v3 in mV; TL-0045 s in CSQ units - nothing in the file says so', 'v1', 4)
flog(F, 3, 'TL-0043: no readings 2024-05-11 02:00-07:45 UTC (24 x 15-min slots), then 8 earlier readings are re-sent')
flog(F, 3, 'TL-0046 stops at 2024-05-12 14:00 UTC (battery died; v3 trends down beforehand); ~1% random single readings dropped')
flog(F, 4, "'id' is not unique: per-device counters, and TL-0044 restarts at 1 after its reboot", 'id', 1)
META[F] = dict(
    title='Cold-chain sensor log (CONFUSING HEADERS)', rows=len(rows), read='1 header row, UTF-8 (degree signs in some cells).',
    cols=list(zip(HDR, [m for c, m in TRUTH])),
    notes=['5 loggers x 4 days x 15-min = 1,920 expected slots. Fridge set-point 2-8 deg C (35.6-46.4 deg F for TL-0045).',
           'Trap: one-letter headers invite "t = temperature"; t is the timestamp and v1 is the temperature.'])
print(F, len(rows), 'rows')
