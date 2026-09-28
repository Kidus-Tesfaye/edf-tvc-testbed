"""Build the fixed / buy-now / can-wait BOM documents from the unpacked original.

Only these things change relative to the original document.xml:
  * the two BOM tables are merged into one (second table's rows appended to the first;
    the two empty spacer rows and the empty paragraph between the tables are dropped)
  * table is made inline (floating anchor removed), given a new grid that fits the page,
    cell widths/margins updated, every font size inside the table normalised
  * page margins reduced
  * price cells listed in PRICE_EDITS and the total cell
  * for the split files: rows removed, '*' appended to the # cell of flagged rows, total recomputed
Nothing else in the document is touched; hyperlink elements and relationships are untouched.
"""
import re, sys, shutil, zipfile, os
from pathlib import Path

ROOT = Path(__file__).parent
SRC_DIR = ROOT / 'unpacked'
OUT = Path(os.environ.get('TEMP', '.')) / 'bom_out'
OUT.mkdir(exist_ok=True)
NAME = 'Updated_Gimbal_Testbed_BOM_with_Arduino_with_Embedded'

# ---- layout knobs (allowed changes) ----------------------------------------
FONT_SZ = int(sys.argv[1]) if len(sys.argv) > 1 else 13      # half-points: 13 = 6.5 pt
MARGIN = int(sys.argv[2]) if len(sys.argv) > 2 else 504      # twips: 504 = 0.35"
PAGE_W, PAGE_H = 16834, 11909                                 # A4 landscape, unchanged
USABLE_W = PAGE_W - 2 * MARGIN
# column widths (twips): #, Category, Component, Qty, Unit, Total, Vendor, Purpose
GRID = [380, 1180, 3300, 520, 760, 1020, 2000, 0]
GRID[7] = USABLE_W - sum(GRID[:7])
CELL_MAR_TB, CELL_MAR_LR = 15, 40

# ---- content edits ---------------------------------------------------------
# row number -> (new unit text, new total text)
PRICE_EDITS = {
    '1': ('168.39', '336.78'),
    '7': ('252.41', '252.41'),
    '20': ('24.08', '24.08'),
    '29': ('109.90', '109.90'),
    '36': ('211.70', '211.70'),
}
ROW_TOTALS = {  # after edits; used for the recomputed totals
    '1': 336.78, '2': 316, '3': 649, '4': 173, '5': 28, '6': 52, '7': 252.41, '8': 807.4,
    '10': 210, '11': 31, '12': 175, '13': 47, '14': 90, '15': 156, '16': 70, '17': 123,
    '18': 66, '19': 126, '20': 24.08, '21': 98, '22': 140, '23': 220, '24': 47, '25': 41,
    '26': 52, '27': 130, '28': 111, '29': 109.90, '30': 69, '31': 294, '32': 92, '33': 202,
    '34': 190, '35': 49, '36': 211.70,
}
CAN_WAIT = {'6'}
FLAG_STAR = {'22', '29', '31', '36'}   # buy-now rows marked * for review

# ---- row replacements (user-approved fixes for mismatched links) ----------
# Keys: component (optional new text), unit, total, vendor = list of segments:
# a plain string is literal text, a (label, url) tuple becomes a hyperlink.
AE = 'https://www.amazon.ae/dp/'
ROW_REPLACE = {
    '12': dict(component='EV200AH-class 200 A sealed DC contactor, 12-24 V coil, 1NO',
               unit='363.03', total='363.03', vendor=[('Amazon.ae', AE + 'B0HFS8CYV8')]),
    '13': dict(component='ANL fuse holders (2) + 150 A / 32 V DC ANL fuses (2)',
               unit='62.74', total='62.74', vendor=[('Amazon.ae', AE + 'B097K598LQ')]),
    '15': dict(unit='391.63', total='391.63',
               vendor=[('Amazon.ae (10 AWG)', AE + 'B07Z4S98J4'), ' / ', ('Amazon.ae (12 AWG)', AE + 'B07ZHXLLGC')]),
    '16': dict(unit='133.40', total='133.40',
               vendor=['Amazon.ae: ', ('crimp kit', 'https://amzn.eu/d/04nibuGm'), ' / ',
                       ('heat-shrink', 'https://amzn.eu/d/0gbopxeT'), ' / ', ('braided sleeve', AE + 'B075VR7ZQS')]),
    '19': dict(component='M3 adjustable pushrods with ball-link ends, 100 mm, 2-pack',
               unit='79.90', total='79.90', vendor=[('Amazon.ae', AE + 'B0F4Y2ZS9M')]),
    '21': dict(component='Stainless shoulder bolts, 5 mm shoulder x M4 x 16 mm (fit 625ZZ), 10-pack',
               unit='54.96', total='54.96', vendor=[('Amazon.ae', AE + 'B077GYHYSB')]),
    '22': dict(unit='33.67', total='134.68',
               vendor=[('Amazon.ae (sold in 2-packs; order 2)', AE + 'B0CTG7TPDM')]),
    '31': dict(component='Temperature sensors: 4x MAX6675 + K-type thermocouples, 5x DS18B20 probes',
               unit='117.22', total='117.22',
               vendor=[('Amazon.ae (MAX6675)', AE + 'B092VV1D2N'), ' / ', ('Amazon.ae (DS18B20)', AE + 'B0CG3HMVWL')]),
    '32': dict(unit='136.39', total='136.39',
               vendor=[('SanDisk High Endurance 64 GB', AE + 'B07P3D6Y5B'), ' and ', ('Amazon.ae (reader)', 'https://amzn.eu/d/0f8epI5R')]),
}
ROW_TOTALS.update({'12': 363.03, '13': 62.74, '15': 391.63, '16': 133.40, '19': 79.90,
                   '21': 54.96, '22': 134.68, '31': 117.22, '32': 136.39})
NEW_RELS = []   # filled by apply_replacements: (rId, url)


def xml_escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def keep_tcpr(tc):
    return re.search(r'<w:tc><w:tcPr>.*?</w:tcPr>', tc, re.S).group(0)


def build_text_cell(tc, text, jc=None):
    ppr = '<w:pPr>' + (f'<w:jc w:val="{jc}"/>' if jc else '') + '<w:rPr><w:sz w:val="14"/></w:rPr></w:pPr>'
    return keep_tcpr(tc) + f'<w:p>{ppr}<w:r><w:rPr><w:sz w:val="14"/></w:rPr><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r></w:p></w:tc>'


def build_vendor_cell(tc, segments):
    runs = []
    for seg in segments:
        if isinstance(seg, str):
            runs.append(f'<w:r><w:rPr><w:sz w:val="14"/></w:rPr><w:t xml:space="preserve">{xml_escape(seg)}</w:t></w:r>')
        else:
            label, url = seg
            rid = f'rId{900 + len(NEW_RELS)}'
            NEW_RELS.append((rid, url))
            runs.append(f'<w:hyperlink r:id="{rid}" w:history="1"><w:r><w:rPr><w:rStyle w:val="Hyperlink"/>'
                        f'<w:sz w:val="14"/></w:rPr><w:t xml:space="preserve">{xml_escape(label)}</w:t></w:r></w:hyperlink>')
    return keep_tcpr(tc) + '<w:p><w:pPr><w:rPr><w:sz w:val="14"/></w:rPr></w:pPr>' + ''.join(runs) + '</w:p></w:tc>'


def apply_replacements(rows):
    out = []
    for r in rows:
        n = row_number(r)
        if n in ROW_REPLACE:
            spec = ROW_REPLACE[n]
            cells = re.findall(r'<w:tc>.*?</w:tc>', r, re.S)
            new = list(cells)
            if 'component' in spec:
                new[2] = build_text_cell(cells[2], spec['component'])
            new[4] = set_first_text(cells[4], spec['unit'])
            new[5] = set_first_text(cells[5], spec['total'])
            new[6] = build_vendor_cell(cells[6], spec['vendor'])
            pos, res = 0, ''
            for old, nw in zip(cells, new):
                i = r.find(old, pos); res += r[pos:i] + nw; pos = i + len(old)
            r = res + r[pos:]
        out.append(r)
    return out


def rels_with_new_links():
    rels = (SRC_DIR / 'word' / '_rels' / 'document.xml.rels').read_text(encoding='utf-8')
    extra = ''.join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" '
                    f'Target="{xml_escape(url)}" TargetMode="External"/>' for rid, url in NEW_RELS)
    return rels.replace('</Relationships>', extra + '</Relationships>')


def fmt_total(v):
    return f'AED {v:,.2f}'


def cell_texts(tc):
    return [''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)) for p in re.findall(r'<w:p[ >].*?</w:p>', tc, re.S)]


def set_first_text(tc, new):
    """Replace the text of the first <w:t> in a cell (used for numeric cells with one run)."""
    return re.sub(r'(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)', lambda m: m.group(1) + new + m.group(3), tc, count=1)


def rewrite_row_widths(row):
    cells = re.findall(r'<w:tc>.*?</w:tc>', row, re.S)
    out, col = [], 0
    for tc in cells:
        span = int(re.search(r'<w:gridSpan w:val="(\d+)"/>', tc).group(1)) if '<w:gridSpan' in tc else 1
        w = sum(GRID[col:col + span]); col += span
        tc = re.sub(r'<w:tcW w:w="\d+" w:type="dxa"/>', f'<w:tcW w:w="{w}" w:type="dxa"/>', tc, count=1)
        tc = re.sub(r'<w:top w:w="\d+" w:type="dxa"/>', f'<w:top w:w="{CELL_MAR_TB}" w:type="dxa"/>', tc)
        tc = re.sub(r'<w:bottom w:w="\d+" w:type="dxa"/>', f'<w:bottom w:w="{CELL_MAR_TB}" w:type="dxa"/>', tc)
        tc = re.sub(r'<w:left w:w="\d+" w:type="dxa"/>', f'<w:left w:w="{CELL_MAR_LR}" w:type="dxa"/>', tc)
        tc = re.sub(r'<w:right w:w="\d+" w:type="dxa"/>', f'<w:right w:w="{CELL_MAR_LR}" w:type="dxa"/>', tc)
        out.append(tc)
    # stitch back: replace cells in order
    pos, res = 0, ''
    for old, new in zip(cells, out):
        i = row.find(old, pos); res += row[pos:i] + new; pos = i + len(old)
    return res + row[pos:]


def build_table_rows(x):
    starts = [m.start() for m in re.finditer(r'<w:tbl>', x)]
    ends = [m.end() for m in re.finditer(r'</w:tbl>', x)]
    t1, t2 = x[starts[0]:ends[0]], x[starts[1]:ends[1]]
    head = re.search(r'<w:tbl>.*?</w:tblGrid>', t1, re.S).group(0)
    rows1 = re.findall(r'<w:tr[ >].*?</w:tr>', t1, re.S)
    rows2 = re.findall(r'<w:tr[ >].*?</w:tr>', t2, re.S)
    assert not any(re.findall(r'<w:t[^>]*>[^<]+</w:t>', r) for r in rows1[-2:]), 'expected two empty spacer rows'
    rows = rows1[:-2] + rows2
    # table properties: inline, full usable width, new grid
    head = re.sub(r'<w:tblpPr [^>]*/>', '', head)
    head = re.sub(r'<w:tblW w:w="\d+" w:type="dxa"/>', f'<w:tblW w:w="{USABLE_W}" w:type="dxa"/>', head)
    head = re.sub(r'<w:tblGrid>.*?</w:tblGrid>', '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in GRID) + '</w:tblGrid>', head, flags=re.S)
    return (starts[0], ends[1]), head, rows


def finish_rows(rows):
    out = []
    for r in rows:
        r = rewrite_row_widths(r)
        r = re.sub(r'<w:sz w:val="\d+"/>', f'<w:sz w:val="{FONT_SZ}"/>', r)
        r = re.sub(r'<w:szCs w:val="\d+"/>', f'<w:szCs w:val="{FONT_SZ}"/>', r)
        r = re.sub(r'<w:trHeight [^>]*/>', '', r)
        # keep the header row on one page with the table (harmless; it's one page anyway)
        out.append(r)
    return out


def row_number(r):
    cells = re.findall(r'<w:tc>.*?</w:tc>', r, re.S)
    t = cell_texts(cells[0])
    return t[0].strip() if t else ''


def apply_prices(rows):
    out = []
    for r in rows:
        n = row_number(r)
        if n in PRICE_EDITS:
            cells = re.findall(r'<w:tc>.*?</w:tc>', r, re.S)
            unit, total = PRICE_EDITS[n]
            new4, new5 = set_first_text(cells[4], unit), set_first_text(cells[5], total)
            r = r.replace(cells[4], new4, 1).replace(cells[5], new5, 1)
        out.append(r)
    return out


def set_total(rows, value_text):
    last = rows[-1]
    assert 'AED 6,510' in last or 'Estimated purchased-component total' in last
    rows[-1] = re.sub(r'(<w:t(?: [^>]*)?>)AED [0-9,]+(?:\.\d+)?(</w:t>)', lambda m: m.group(1) + value_text + m.group(2), last, count=1)
    return rows


def star_rows(rows, flagged):
    out = []
    for r in rows:
        n = row_number(r)
        if n in flagged:
            cells = re.findall(r'<w:tc>.*?</w:tc>', r, re.S)
            first = re.sub(r'(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)', lambda m: m.group(1) + m.group(2).rstrip() + '*' + m.group(3), cells[0], count=1)
            r = r.replace(cells[0], first, 1)
        out.append(r)
    return out


def write_docx(xml, name):
    outdir = OUT / '_build'
    if outdir.exists(): shutil.rmtree(outdir)
    shutil.copytree(SRC_DIR, outdir)
    (outdir / 'word' / 'document.xml').write_text(xml, encoding='utf-8')
    (outdir / 'word' / '_rels' / 'document.xml.rels').write_text(rels_with_new_links(), encoding='utf-8')
    target = OUT / f'{name}.docx'
    if target.exists(): target.unlink()
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml first, as Word prefers
        z.write(outdir / '[Content_Types].xml', '[Content_Types].xml')
        for p in sorted(outdir.rglob('*')):
            if p.is_file() and p.name != '[Content_Types].xml':
                z.write(p, p.relative_to(outdir).as_posix())
    shutil.rmtree(outdir)
    return target


def main():
    x = (SRC_DIR / 'word' / 'document.xml').read_text(encoding='utf-8')
    (a, b), head, rows = build_table_rows(x)
    rows = apply_replacements(rows)
    rows = finish_rows(rows)
    rows = apply_prices(rows)
    grand = sum(ROW_TOTALS.values())
    fixed_rows = set_total(list(rows), fmt_total(grand))
    # page margins
    x2 = re.sub(r'<w:pgMar [^>]*/>', f'<w:pgMar w:top="{MARGIN}" w:right="{MARGIN}" w:bottom="{MARGIN}" w:left="{MARGIN}" w:header="360" w:footer="288" w:gutter="0"/>', x)
    # note: offsets a,b were computed on x; the pgMar edit is after the tables so they still hold
    assert x2[:a] == x[:a]
    def assemble(rws):
        return x2[:a] + head + ''.join(rws) + '</w:tbl>' + x2[b:]
    fixed = write_docx(assemble(fixed_rows), f'{NAME}-fixed')
    # splits: header row + selected data rows + total row
    header, data, total = rows[0], rows[1:-1], rows[-1]
    buy = [r for r in data if row_number(r) not in CAN_WAIT]
    wait = [r for r in data if row_number(r) in CAN_WAIT]
    buy_sum = sum(ROW_TOTALS[row_number(r)] for r in buy)
    wait_sum = sum(ROW_TOTALS[row_number(r)] for r in wait)
    buy_rows = set_total([header] + star_rows(buy, FLAG_STAR) + [total], fmt_total(buy_sum))
    wait_rows = set_total([header] + wait + [total], fmt_total(wait_sum))
    b1 = write_docx(assemble(buy_rows), f'{NAME}-buy-now')
    b2 = write_docx(assemble(wait_rows), f'{NAME}-can-wait')
    print(f'font {FONT_SZ/2} pt, margins {MARGIN/1440:.2f} in, grid {GRID} (sum {sum(GRID)} of {USABLE_W})')
    print(f'grand total {fmt_total(grand)} | buy-now {len(buy)} rows {fmt_total(buy_sum)} | can-wait {len(wait)} rows {fmt_total(wait_sum)}')
    print('wrote', fixed.name, b1.name, b2.name)


if __name__ == '__main__':
    main()
