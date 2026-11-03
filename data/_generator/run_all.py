"""Generate all 10 dirty datasets + the answer key (issue_log.csv and ANSWER_KEY.md)."""
import csv, importlib, os
from collections import Counter, defaultdict
import common
from common import ISSUES, LOG, META, OUT

MODS = ['ds01_suppliers', 'ds02_shipments', 'ds03_stock', 'ds04_sales_summary', 'ds05_catalog', 'ds06_erp_po',
        'ds07_driver_roster', 'ds08_coldchain', 'ds09_pos_65536', 'ds10_wide_255']
for m in MODS:
    importlib.import_module(m)

KEY = os.path.join(OUT, '_answer_key')
os.makedirs(KEY, exist_ok=True)
FIELDS = ['file', 'row', 'col_index', 'column', 'issue_id', 'issue', 'dirty_value', 'expected_clean_value', 'note']
with open(os.path.join(KEY, 'issue_log.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, FIELDS, lineterminator='\n'); w.writeheader(); w.writerows(LOG)

files = list(META)
by = defaultdict(lambda: defaultdict(list))
for e in LOG:
    by[e['file']][e['issue_id']].append(e)


def esc(s, n=60):
    s = str(s).replace('\n', '\\n').replace('|', '\\|').replace('`', "'")
    if s == '': return '(blank)'
    if s.strip() == '': return f"'{s}'"
    return s if len(s) <= n else s[:n - 1] + '…'


L = ['# Dirty datasets: answer key', '',
     'Ground truth for the 10 CSVs in the parent folder. Every injected problem is listed cell by cell in `issue_log.csv`; '
     'this page summarises it.', '',
     '**Blind testing:** the file names describe the main problems. If the model under test can see file names, '
     'rename the files (e.g. `dataset_01.csv`) first. Keep this `_answer_key` folder away from the model.', '',
     '## How to read issue_log.csv', '',
     '| column | meaning |', '|---|---|',
     '| file | dataset file name |',
     '| row | 1-based DATA row (first row under the header row(s) = 1, i.e. pandas index + 1). `HEADER` = the column name itself, '
     '`ALL` = the whole column (pattern or rule), `FILE` = whole-file finding |',
     '| col_index | 1-based column position (`*` = whole row / not one column) |',
     '| column | header text as it appears in the file (two-row headers joined with ` / `) |',
     '| issue_id / issue | which of the 19 Quartz Bad Data Guide problems it is |',
     '| dirty_value | exactly what is in the cell |',
     '| expected_clean_value | what a correct cleaner should produce; blank = should become null/unknown |',
     '| note | why it is wrong, plus the true value when the clean value has to be null |', '',
     'Regenerate or tweak: `cd _generator && python3 run_all.py && python3 verify.py` (seeded, so output is identical; '
     'verify.py re-checks every cell-level entry against the CSVs).', '',
     '## Coverage: logged findings per issue and file', '',
     '| # | Issue | ' + ' | '.join(f[:2] for f in files) + ' |', '|---|---|' + '---|' * len(files)]
for iid, name in ISSUES.items():
    L.append(f'| {iid} | {name} | ' + ' | '.join(str(len(by[f][iid])) if by[f][iid] else '' for f in files) + ' |')
conf = [f[:2] for f in files if 'CONFUSING_HEADERS' in f]
L += ['', f"Files {', '.join(conf[:-1])} and {conf[-1]} have deliberately cryptic/confusing column names; "
          f"the other {len(files) - len(conf)} have messy but readable headers.", '']
for f in files:
    m = META[f]; n_log = sum(len(v) for v in by[f].values())
    L += [f'## {f[:2]}. {m["title"]}', '', f'`{f}`', '',
          f'- Data rows: **{m["rows"]:,}**. {m["read"]}', f'- Logged findings: {n_log:,} across {sum(1 for v in by[f].values() if v)} of the 19 issue types.']
    L += [f'- {x}' for x in m.get('notes', [])]
    L += ['', '**What each column really is**', '', '| header in file | true meaning |', '|---|---|']
    L += [f'| `{esc(h, 70)}` | {esc(mn, 200)} |' for h, mn in m['cols']]
    L += ['', '**Problems planted**', '', '| # | issue | count | examples (`dirty` → expected) or finding |', '|---|---|---|---|']
    for iid in sorted(by[f]):
        es = by[f][iid]
        if not es: continue
        facts = [e for e in es if e['row'] in ('FILE', 'ALL', 'HEADER') or e['col_index'] == '*']
        cells = [e for e in es if e not in facts]
        ex, seen = [], set()
        for e in facts[:4]:
            if e['row'] == 'FILE' or e['col_index'] == '*': ex.append(esc(e['note'], 220))
            elif e['row'] == 'HEADER': ex.append(f"`{esc(e['dirty_value'], 40)}` = {esc(e['note'], 120)}")
            else: ex.append(f"{esc(e['column'], 30)}: " + (f"`{esc(e['dirty_value'], 30)}` → `{esc(e['expected_clean_value'], 30)}` "
                                                         if e['dirty_value'] else '') + f"({esc(e['note'], 140)})")
        for e in cells:
            k = (e['column'], e['note'][:25])
            if k in seen or len(ex) >= 6: continue
            seen.add(k)
            ex.append(f"{esc(e['column'], 25)}: `{esc(e['dirty_value'], 28)}` → `{esc(e['expected_clean_value'], 28)}` ({esc(e['note'], 70)})")
        L.append(f'| {iid} | {ISSUES[iid]} | {len(es)} | ' + '<br>'.join(ex) + ' |')
    L.append('')
with open(os.path.join(KEY, 'ANSWER_KEY.md'), 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(L) + '\n')

cov = {iid: sum(1 for f in files if by[f][iid]) for iid in ISSUES}
print('log entries:', len(LOG))
print('issues not covered:', [i for i, c in cov.items() if c == 0] or 'none')
print('files per issue:', cov)
