"""Shared helpers for the dirty-dataset generators. Everything is seeded/deterministic."""
import csv, os, random, datetime as dt

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('DIRTY_OUT') or os.path.dirname(BASE)  # CSVs go next to the _generator folder
os.makedirs(OUT, exist_ok=True)

ISSUES = {
    1: 'Values are missing',
    2: 'Zeros replace missing values',
    3: 'Data are missing you know should be there',
    4: 'Rows or values are duplicated',
    5: 'Spelling is inconsistent',
    6: 'Name order is inconsistent',
    7: 'Date formats are inconsistent',
    8: 'Units are not specified',
    9: 'Categories are badly chosen',
    10: 'Field names are ambiguous',
    11: 'Provenance is not documented',
    12: 'Suspicious values are present',
    13: 'Data are too coarse',
    14: 'Totals differ from published aggregates',
    15: 'Spreadsheet has 65536 rows',
    16: 'Spreadsheet has 255 columns',
    17: 'Spreadsheet has dates in 1900, 1904, 1969, or 1970',
    18: 'Text has been converted to numbers',
    19: 'Numbers have been stored as text',
}

LOG, META = [], {}


def log(file, row, col_idx, column, iid, dirty='', clean='', note=''):
    LOG.append(dict(file=file, row=row, col_index=col_idx, column=column, issue_id=iid,
                    issue=ISSUES[iid], dirty_value=dirty, expected_clean_value=clean, note=note))


def flog(file, iid, note, column='*', col_idx='*', dirty='', clean=''):
    """File-level (column='*') or whole-column finding, not tied to a single cell."""
    log(file, 'FILE' if column == '*' else 'ALL', col_idx, column, iid, dirty, clean, note)


MISSING = ['', '', '', '', 'N/A', 'n/a', 'NA', 'null', 'NULL', '-', '--', '?', 'none',
           '#N/A', 'nan', ' ', 'TBD', 'unknown', 'NIL']


class Row(dict):
    """A data row plus the issues injected into it (logged with the final row number)."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.issues, self.uid, self.dup_of, self.dup_note = [], None, None, ''

    def put(self, col, dirty, clean='', iid=None, note=''):
        self.clear(col)  # an overwritten cell keeps only the issues of its final value
        self[col] = dirty
        if iid is not None:
            for i in (iid if isinstance(iid, (list, tuple)) else [iid]):
                self.issues.append((col, i, dirty, clean, note))
        return dirty

    def clear(self, col):
        self.issues = [x for x in self.issues if x[0] != col]

    def miss(self, col, rng, true='', tokens=None):
        tok = rng.choice(tokens or MISSING)
        return self.put(col, tok, '', 1, f'missing (true value: {true})' if true != '' else 'missing')

    def dup(self, note='exact duplicate of row {row}'):
        if self.uid is None:
            self.uid = id(self)
        r = Row(**self)
        r.__dict__.update({k: v for k, v in self.__dict__.items() if k not in ('issues', 'uid', 'dup_of', 'dup_note')})
        r.issues, r.dup_of, r.dup_note = list(self.issues), self.uid, note
        return r


def write(fname, cols, rows, header_rows=None, bom=False, header_issues=()):
    """Write CSV, then log every injected issue with its final 1-based data-row number."""
    header_rows = header_rows or [cols]
    first = {}
    for i, r in enumerate(rows, 1):
        if r.uid is not None and r.dup_of is None:
            first.setdefault(r.uid, i)
    path = os.path.join(OUT, fname)
    with open(path, 'w', newline='', encoding='utf-8-sig' if bom else 'utf-8') as f:
        w = csv.writer(f, lineterminator='\r\n')
        w.writerows(header_rows)
        for r in rows:
            w.writerow([r.get(c, '') for c in cols])
    disp = []
    for j in range(len(cols)):
        parts = [h[j] for h in header_rows if h[j].strip()]
        disp.append(' / '.join(parts) if parts else f'(blank header, col {j + 1})')
    idx = {c: j for j, c in enumerate(cols)}
    for c, iid, note in header_issues:
        j = idx[c]
        log(fname, 'HEADER', j + 1, disp[j], iid, ' || '.join(h[j] for h in header_rows), '', note)
    for i, r in enumerate(rows, 1):
        for c, iid, dirty, clean, note in r.issues:
            j = idx[c]
            log(fname, i, j + 1, disp[j], iid, dirty, clean, note)
        if r.dup_of is not None:
            log(fname, i, '*', '(whole row)', 4, '', '(drop)',
                r.dup_note.format(row=first.get(r.dup_of, '?')))
    return path


# ---------- dates ----------
XL0 = dt.date(1899, 12, 30)
DFMT = {'iso': '%Y-%m-%d', 'dmy': '%d/%m/%Y', 'mdy': '%m/%d/%Y', 'd-mon-y': '%d-%b-%Y',
        'd-mon-yy': '%d-%b-%y', 'long': '%B %d, %Y', 'compact': '%Y%m%d', 'dot': '%d.%m.%Y',
        'ymd/': '%Y/%m/%d', 'dow': '%a %d %b %Y', 'dmy-': '%d-%m-%Y'}


def _d(x):
    return x.date() if isinstance(x, dt.datetime) else x


def fdate(x, style):
    if style == 'serial':
        return str((_d(x) - XL0).days)
    if style == 'unix':
        d = _d(x)
        return str(int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp()))
    if style == 'm/d/yyyy':
        d = _d(x); return f'{d.month}/{d.day}/{d.year}'
    if style == 'm/d/yy':
        d = _d(x); return f'{d.month}/{d.day}/{d.year % 100:02d}'
    if style == 'd/m/yy':
        d = _d(x); return f'{d.day}/{d.month}/{d.year % 100:02d}'
    return x.strftime(DFMT[style])


EPOCH_JUNK = ['1900-01-01', '01/01/1900', '1/1/1970', '1970-01-01 00:00:00', '1904-01-01',
              '00/01/1900', '1900-01-00', '1969-12-31 18:30:00', '1970-01-01 05:30:00', '31/12/1969']

# ---------- people ----------
FIRST = ['Nimal', 'Kamal', 'Sunil', 'Tharindu', 'Kasun', 'Ruwan', 'Arjun', 'Suresh', 'Mohamed', 'Rizwan',
         'Dinesh', 'Sanjeewa', 'Harsha', 'Pradeep', 'Gayan', 'Ravi', 'Niroshan', 'Kumaran', 'Sivakumar',
         'Lahiru', 'Chaminda', 'Asanka', 'Imran', 'Janaka', 'Dhanushka', 'Ramesh', 'Nuwan', 'Prasanna',
         'Dilani', 'Ishara', 'Chamari', 'Nadeesha', 'Priyanka', 'Kavitha', 'Lakshmi', 'Fathima', 'Ayesha',
         'Malini', 'Thilini', 'Shanika', 'Anjali', 'Vithya', 'Janani', 'Sachini', 'Nirmala', 'Hiruni']
LAST = ['Perera', 'Fernando', 'Silva', 'de Silva', 'Jayasinghe', 'Wickramasinghe', 'Bandara', 'Gunawardena',
        'Herath', 'Kumara', 'Mendis', 'Weerasinghe', 'Ranasinghe', 'Karunaratne', 'Samarasinghe',
        'Abeysekera', 'Liyanage', 'Ratnayake', 'Rajendran', 'Selvaraj', 'Kanagaratnam', 'Nadarajah',
        'Ismail', 'Marikar', 'Hameed', 'Wijesinghe', 'Jayawardena', 'Gamage', 'Pathirana', 'Rathnayake']
NAME_STYLES = ['fl'] * 6 + ['l, f', 'L f', 'l f', 'i. l', 'l i.', 'inits l', 'f m l', 'hon f l', 'lower']


def name_fmt(first, last, style, rng):
    """Return (text, issue_id or None, note) for a person name rendered in `style`."""
    if style == 'fl':
        return f'{first} {last}', None, ''
    if style == 'l, f':
        return f'{last}, {first}', 6, 'Last, First'
    if style == 'L f':
        return f'{last.upper()} {first}', 6, 'SURNAME First'
    if style == 'l f':
        return f'{last} {first}', 6, 'Last First (no comma)'
    if style == 'i. l':
        return f'{first[0]}. {last}', 6, 'initial + surname: first name not recoverable'
    if style == 'l i.':
        return f'{last} {first[0]}.', 6, 'surname + initial: first name not recoverable'
    if style == 'inits l':
        inits = '.'.join(rng.sample('ABDGHJKMNPRSW', rng.randint(1, 3)) + [first[0]]) + '.'
        return f'{inits} {last}', 6, 'Sri Lankan initials format: first name not recoverable'
    if style == 'f m l':
        return f'{first} {rng.choice("ABDKMNPRS")}. {last}', 6, 'middle initial added'
    if style == 'hon f l':
        return f'{rng.choice(["Dr.", "Eng.", "Prof."])} {first} {last}', 6, 'honorific prefix'
    return f'{first.lower()} {last.lower()}', 5, 'lower-cased name'


# ---------- numbers ----------
def mobile(rng):
    return '07' + rng.choice('0124567') + ''.join(rng.choice('0123456789') for _ in range(7))


def xl_sci(n):
    """How Excel's General format shows a big integer, e.g. 94771234567 -> 9.47712E+10."""
    m, e = f'{n:.5E}'.split('E')
    m = m.rstrip('0').rstrip('.')
    return f'{m}E{e[0]}{int(e[1:]):02d}'


def money_text(v, rng, styles=None):
    """Return (text, issue_id or None, note) for an LKR amount, often stored as non-numeric text."""
    st = rng.choice(styles or ['plain'] * 4 + ['comma', 'rs', 'rs_eq', 'dash', 'lkr', 'euro', 'pad', 'lakh', 'k'])
    if st == 'plain':
        return f'{v:.2f}', None, ''
    if st == 'comma':
        return f'{v:,.2f}', 19, 'thousands separator'
    if st == 'rs':
        return f'Rs. {v:,.2f}', 19, 'currency prefix'
    if st == 'rs_eq':
        return f'Rs {v:,.0f}/=', 19, "Sri Lankan '/=' suffix"
    if st == 'dash':
        return f'{v:,.0f}/-', 19, "'/-' suffix"
    if st == 'lkr':
        return f'LKR{v:.0f}', 19, 'currency code glued to number'
    if st == 'euro':
        return f'{v:,.2f}'.replace(',', '#').replace('.', ',').replace('#', '.'), 19, 'European format (decimal comma)'
    if st == 'pad':
        return f' {v:.2f} ', 19, 'padded with spaces'
    if st == 'lakh':
        return f'{v / 100000:.2f}L', 19, 'in lakhs (x100,000), precision lost'
    return f'{v / 1000:.1f}k', 19, "'k' suffix, precision lost"
