# ホームページ案内文（第3版）の差し込み印刷。
# 送り先リストのCSVを読んで、1社1枚のPDFと、印刷用まとめ.pdf・一覧.csv を作る。
#
#   python3 make_letters.py                 … 送り先リスト/ のいちばん新しいCSVを使う
#   python3 make_letters.py 送り先リスト/xxx.csv
#
# 紙面のデザイン・文面は build_letter_v3.py のものをそのまま使う（ここでは空欄を埋めるだけ）。
# 分類 A → 案内文A ／ B・C・D → 案内文B ／ E・空欄 → 作らない
import csv, datetime, json, pathlib, re, subprocess, sys, tempfile, unicodedata
import segno
from pypdf import PdfReader, PdfWriter

D = pathlib.Path(__file__).resolve().parent
LIST_DIR = D / "送り先リスト"
OUT_DIR = D / "出力"


# ---------- 1. 第3版の紙面（A・B）を取り出す（letter_v3.html は書き換えない） ----------
def load_pages():
    code = (D / "build_letter_v3.py").read_text()
    write_line = '(D / "letter_v3.html").write_text(out)'
    assert write_line in code, "build_letter_v3.py の形が変わっています"
    code = code.replace(write_line, "").replace('print("ok")', "")
    ns = {"__file__": str(D / "build_letter_v3.py")}
    exec(compile(code, "build_letter_v3", "exec"), ns)
    return ns["HEAD"], ns["PAGE_A"], ns["PAGE_B"]


# 差し込みのための追加CSS（空欄の中に文字・QRを入れるだけ。ほかの見た目は変えない）
MERGE_CSS = """<style>
.addr .to .mm-name{white-space:nowrap;margin-right:1.5mm}
.sec-h h2 .blank.mm-fill{width:auto;min-width:28mm;padding:0 1.2mm;white-space:nowrap;text-align:center;line-height:5mm}
.sec-h h2:has(.mm-fill){white-space:nowrap}
.qrbox.paste .mm-qr{position:absolute;left:2mm;top:2mm;width:22mm;height:22mm;display:block}
</style>"""


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def norm(s):
    return unicodedata.normalize("NFKC", (s or "")).strip()


def parse_date(s):
    s = norm(s)
    if not s:
        return None
    m = re.match(r"(\d{4})\D(\d{1,2})\D(\d{1,2})", s)
    if not m:
        raise ValueError(f"日付が読めません: {s}（例 2026-12-01）")
    return datetime.date(int(m[1]), int(m[2]), int(m[3]))


def reiwa(d):
    y = d.year - 2018
    return f"令和{'元' if y == 1 else y}年{d.month}月{d.day}日"


def qr_img(url):
    q = segno.make(url, error="m")
    return q.svg_inline(border=1, dark="#000", light="#fff", omitsize=True, svgclass="mm-qr", lineclass=None)


HOUJIN = r"(株式会社|有限会社|合同会社|合資会社|合名会社|一般社団法人|一般財団法人|社会福祉法人|医療法人社団|医療法人|NPO法人|特定非営利活動法人|（株）|\(株\)|㈱|（有）|\(有\)|㈲)"


def short_name(name):
    """見出しに入りきらないとき用：法人の種類（株式会社など）を外した名前"""
    s = re.sub(HOUJIN, "", name).strip(" 　")
    return s or name


def fill(page, name, sent, limit, url, heading_short=""):
    n = esc(name)
    alt = esc(heading_short or short_name(name))
    def rep(old, new):
        nonlocal page
        assert old in page, "差し込み位置が見つかりません: " + old
        page = page.replace(old, new)
    rep('<div class="to">様</div>', f'<div class="to"><span class="mm-name">{n}</span>様</div>')
    if sent:
        rep('令和　　年　　月　　日', reiwa(sent))
    if limit:
        rep('＿＿月＿＿日まで', f'{limit.month}月{limit.day}日まで')
    rep('<span class="blank"></span>', f'<span class="blank mm-fill" data-short="{alt}" data-fixed="{1 if heading_short else 0}">'
        f'<span class="mm-t">{alt if heading_short else n}</span></span>')
    if url:
        rep('<div class="qrbox paste" aria-label="QRコード貼り付け欄"></div>',
            f'<div class="qrbox paste">{qr_img(url)}</div>')
    return page


def read_csv(path):
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "cp932"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise SystemExit("CSVの文字コードが読めません（UTF-8 か Shift_JIS で保存してください）")
    rows = list(csv.DictReader(text.splitlines()))
    return [{norm(k): (v or "").strip() for k, v in r.items() if k} for r in rows]


def pick_csv():
    if len(sys.argv) > 1:
        p = pathlib.Path(sys.argv[1])
        return p if p.is_absolute() else (pathlib.Path.cwd() / p)
    files = sorted(LIST_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    real = [p for p in files if not p.name.startswith("sample")]
    if not (real or files):
        raise SystemExit(f"CSVがありません: {LIST_DIR} に送り先リストのCSVを入れてください")
    return (real or files)[0]


def safe(s):
    return re.sub(r'[\\/:*?"<>|\s]+', "", s) or "名前なし"


def prio_key(p):
    return (0, int(p)) if p.isdigit() else (1, p)


def main():
    src = pick_csv()
    print("読み込むCSV:", src)
    HEAD, PAGE_A, PAGE_B = load_pages()
    head = HEAD.replace("<head>", f'<head><base href="{D.as_uri()}/">', 1).replace("</head>", MERGE_CSS + "</head>", 1)

    rows = read_csv(src)
    jobs, skipped = [], []
    for i, r in enumerate(rows):
        name = r.get("会社名", "")
        kind = norm(r.get("分類", ""))[:1].upper()
        if not name:
            continue
        if kind not in "ABCD" or not kind:
            skipped.append({"会社名": name, "分類": kind or "空欄"})
            continue
        sent, limit = parse_date(r.get("送付日")), parse_date(r.get("期限"))
        url = r.get("見本URL", "").strip()
        prio = norm(r.get("優先順位", ""))
        notes = []
        if not url: notes.append("QR未設定")
        if not sent: notes.append("送付日未設定（日付は空欄）")
        if not limit: notes.append("期限未設定（空欄）")
        ver = "A" if kind == "A" else "B"
        page = fill(PAGE_A if ver == "A" else PAGE_B, name, sent, limit, url, r.get("略称", ""))
        folder = OUT_DIR / (sent.isoformat() if sent else "送付日未設定")
        pfx = f"{int(prio):02d}" if prio.isdigit() else (safe(prio) if prio else "00")
        jobs.append({"i": i, "name": name, "kind": kind, "ver": ver, "qr": bool(url), "prio": prio,
                     "notes": notes, "folder": folder, "pdf": folder / f"{pfx}_{safe(name)}.pdf",
                     "html": head + page + "\n</body></html>\n"})

    if not jobs:
        raise SystemExit("作る対象（分類A〜D）がありません")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        spec = []
        for k, j in enumerate(jobs):
            j["folder"].mkdir(parents=True, exist_ok=True)
            h = tmp / f"{k}.html"
            h.write_text(j["html"])
            spec.append({"html": str(h), "pdf": str(j["pdf"])})
        (tmp / "jobs.json").write_text(json.dumps(spec, ensure_ascii=False))
        res = subprocess.run(["node", str(D / "render_letters.js"), str(tmp / "jobs.json")],
                             capture_output=True, text=True)
        if res.returncode != 0:
            print(res.stdout, res.stderr)
            raise SystemExit("PDFづくりに失敗しました")
        checks = json.loads(res.stdout.strip().splitlines()[-1])

    problems = 0
    for j, c in zip(jobs, checks):
        if c["warn"]:
            j["notes"] += c["warn"]
            problems += 1
        j["check"] = c

    # 送付日ごとに：印刷用まとめ.pdf と 一覧.csv
    for folder in sorted({j["folder"] for j in jobs}):
        group = sorted([j for j in jobs if j["folder"] == folder], key=lambda j: (prio_key(j["prio"]), j["i"]))
        w = PdfWriter()
        for j in group:
            pages = PdfReader(str(j["pdf"])).pages
            if len(pages) != 1:
                j["notes"].append(f"ページ数が{len(pages)}枚（要確認）")
            w.add_page(pages[0])
        with open(folder / "印刷用まとめ.pdf", "wb") as f:
            w.write(f)
        with open(folder / "一覧.csv", "w", newline="", encoding="utf-8-sig") as f:
            cw = csv.writer(f)
            cw.writerow(["印刷順", "優先順位", "会社名", "分類", "使った版", "QRの有無", "ファイル", "備考"])
            for n, j in enumerate(group, 1):
                cw.writerow([n, j["prio"], j["name"], j["kind"], "案内文" + j["ver"],
                             "あり" if j["qr"] else "QR未設定", j["pdf"].name, "・".join(j["notes"])])
            for s in skipped:
                cw.writerow(["", "", s["会社名"], s["分類"], "作成なし（対象外）", "", "", ""])
        print(f"出力: {folder}（{len(group)}社）")

    for j in jobs:
        c = j["check"]
        print(f"  {j['pdf'].name}  版{j['ver']}  QR:{'あり' if j['qr'] else 'なし'}  下余白{c['bottomMM']}mm"
              f"  宛名{c['nameSize']}pt  感謝価格の見出し「{c['blankText']}」{c['blankSize']}pt  {' '.join(j['notes'])}")
    if skipped:
        print(f"  対象外で作らなかった会社: {len(skipped)}社")
    if problems:
        print(f"注意：{problems}社に確認が必要な点があります（一覧.csv の備考を見てください）")


if __name__ == "__main__":
    main()
