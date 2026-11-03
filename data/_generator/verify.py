"""Independent checks: shape limits, parseability, and that every cell-level answer-key entry matches the file."""
import csv, io, os, re
from collections import Counter, defaultdict
import pandas as pd

OUT = os.environ.get('DIRTY_OUT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log = list(csv.DictReader(open(os.path.join(OUT, '_answer_key', 'issue_log.csv'), encoding='utf-8')))
by = defaultdict(list)
for e in log: by[e['file']].append(e)
files = sorted(f for f in os.listdir(OUT) if f.endswith('.csv'))
assert len(files) == 10, files
problems = 0
for f in files:
    raw = open(os.path.join(OUT, f), encoding='utf-8', newline='').read()
    bom = raw.startswith('﻿'); recs = list(csv.reader(io.StringIO(raw.lstrip('﻿'))))
    hn = 2 if f.startswith('07') else 1; data = recs[hn:]
    widths = Counter(len(r) for r in recs)
    ok = bad = dup_ok = dup_bad = 0
    for e in by[f]:
        r, c, want = e['row'], e['col_index'], e['dirty_value']
        if r == 'HEADER':
            got = ' || '.join(recs[k][int(c) - 1] for k in range(hn)).lstrip('﻿')
        elif r.isdigit() and c.isdigit():
            got = data[int(r) - 1][int(c) - 1]
        elif r.isdigit() and c == '*' and e['issue_id'] == '4':
            m = re.search(r'row (\d+)', e['note'])
            if m and re.search(r'exact|double-posted|re-imported|re-sent|loaded twice', e['note']):
                same = data[int(r) - 1] == data[int(m.group(1)) - 1]
                dup_ok += same; dup_bad += not same
            continue
        else:
            continue
        if got == want: ok += 1
        else:
            bad += 1
            if bad <= 3: print('   MISMATCH', f[:2], r, c, repr(want), '!=', repr(got))
    pdf = pd.read_csv(os.path.join(OUT, f), header=list(range(hn)) if hn > 1 else 0, dtype=str, keep_default_na=False, encoding='utf-8')
    lines = raw.count('\n')
    print(f'{f[:2]} rows={len(data):>6} lines={lines:>6} cols={sorted(widths)} bom={bom} pandas={pdf.shape} '
          f'cells ok={ok} bad={bad} dups ok={dup_ok} bad={dup_bad}')
    problems += bad + dup_bad + (len(widths) != 1) + (pdf.shape[0] != len(data))
    if f.startswith('09'): problems += (len(recs) != 65536 or lines != 65536)
    if f.startswith('10'): problems += widths != Counter({255: len(recs)})
last = list(csv.reader(open(os.path.join(OUT, files[8]), encoding='utf-8')))[-3:]
print('09 tail:', [(x[1], x[2], x[3]) for x in last])
print('TOTAL PROBLEMS:', problems)
