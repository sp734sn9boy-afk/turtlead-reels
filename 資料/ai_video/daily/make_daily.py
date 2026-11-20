# -*- coding: utf-8 -*-
"""AI動画編集部・毎日のショート動画を、台本.json 1つから作る（HyperFrames版の型）。

使い方（リポジトリの一番上で）:
  python3 資料/ai_video/daily/make_daily.py 資料/ai_video/daily/2026-11-21/台本.json
  オプション:
    --no-render   声づくり・場面組み立て・チェックまで（書き出ししない）
    --draft       書き出しを下書き画質で（速い・確認用）
    --force       チェックでエラーが出ても書き出す

流れ: ①声づくり（VOICEVOX:春日部つむぎ）→ ②HyperFramesの場面組み立て → ③チェック（hyperframes check・字幕のはみ出し・秒数）
      → ④書き出し（MP4）→ ⑤確認（長さの照合・確認コマの画像・コンタクトシート）
出力（台本.json と同じフォルダ）:
  turtle_ai_<日付>.mp4 / 確認コマ/ / 秒数表.md / 概要欄.txt / チェック結果.txt / project/（HyperFramesの中身） / voice/（声のキャッシュ）
前提: VOICEVOX ENGINE が 127.0.0.1:50021 で動いていること（手順は 毎日の手順.md）。
公開・投稿はしない（作るだけ）。
"""
import hashlib, json, math, os, re, shutil, subprocess, sys, time, urllib.parse, urllib.request, wave, datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
AV = os.path.abspath(os.path.join(HERE, ".."))
TEMPLATE = os.path.join(HERE, "template")
FONT_DIR = os.path.join(AV, "fonts")
VV = os.environ.get("VOICEVOX_URL", "http://127.0.0.1:50021")
HF_CLI = os.environ.get("HF_CLI", os.path.expanduser("~/.claude/skills/hyperframes/scripts/plugin-cli.mjs"))
TELEMETRY_OFF = {"HYPERFRAMES_NO_TELEMETRY": "1", "DO_NOT_TRACK": "1", "DISABLE_TELEMETRY": "1"}
os.environ.update(TELEMETRY_OFF)

W, H, FPS, SR = 1080, 1920, 30, 48000
LINE_ID = "@486zunqz"
SITE = "turtle-ad.com"
DISCLOSURE = "この動画は、タートルアドのAIチームが<br/>情報収集から台本・音声・映像まで作っています"
CREDIT = "VOICEVOX:春日部つむぎ"
WEEK = "月火水木金土日"

TYPES = {
    "weekday":  {"program": "今日のAIニュース",          "icon": "AI", "min": 30, "max": 45},
    "saturday": {"program": "AIで仕事が楽になった実例",  "icon": "例", "min": 30, "max": 45},
    "sunday":   {"program": "今週のまとめ",              "icon": "週", "min": 30, "max": 90},
    "greeting": {"program": "チャンネル開設のごあいさつ", "icon": "初", "min": 30, "max": 40},
}
ROOT = os.path.abspath(os.path.join(AV, "..", ".."))  # リポジトリの一番上
TIP_LABEL = "中小企業ならこう使える"

# 宣伝カードのセリフ（台本の "cta_say" で変えられる）
CTA_SAY = [{"sub": "このキャラクターのようなAI動画を、", "read": "このキャラクターのようなエーアイ動画を、"},
           {"sub": "御社のロゴから作ります。", "read": "おんしゃのロゴから作ります。"}]

# 読み方の置きかえ（字幕 → 読み上げ）。長いものから置きかえる。台本の "readings" で追加できる。
READING = {
    "Claude Fable 5.2": "くろーどふぇいぶるごーてんに", "Claude": "クロード", "ChatGPT": "チャットジーピーティー",
    "Googleマップ": "グーグルマップ", "Google": "グーグル", "Gemini": "ジェミニ", "Anthropic": "アンソロピック",
    "OpenAI": "オープンエーアイ", "Microsoft": "マイクロソフト", "Copilot": "コパイロット", "Canva": "キャンバ",
    "Instagram": "インスタグラム", "YouTube": "ユーチューブ", "LINE": "ライン", "AI": "エーアイ",
    "十分": "じゅうぶん", "日本": "にほん", "御社": "おんしゃ",
}

def log(*a):
    print(*a, flush=True)

# ------------------------------------------------------------------ 台本を読む
def load_script(path):
    raw = open(path, encoding="utf-8").read()
    if "【" in raw and "】" in raw and re.search(r"【[^】]*(ここに|手順|出典|説明|困って|こう使える|前は|結果|一言|概要欄)", raw):
        sys.exit("台本にひな形の【…】が残っています。中身を書きかえてから実行してください。")
    sc = json.loads(raw)
    for k in ("date", "hook", "items"):
        if k not in sc: sys.exit(f"台本に「{k}」がありません: {path}")
    d = datetime.date.fromisoformat(sc["date"])
    if "type" not in sc:
        sc["type"] = "saturday" if d.weekday() == 5 else "sunday" if d.weekday() == 6 else "weekday"
    if sc["type"] not in TYPES: sys.exit(f"type は weekday / saturday / sunday のどれか: {sc['type']}")
    if sc["type"] not in ("sunday",) and len(sc["items"]) != 1:
        log(f"注意: {sc['type']} は1本1ネタの型です（items が {len(sc['items'])} 個）。そのまま作ります。")
    sc["_date"] = d
    return sc

def norm_chunk(c):
    if isinstance(c, str): return {"sub": c, "read": None, "speed": None}
    return {"sub": c["sub"], "read": c.get("read"), "speed": c.get("speed")}

# 型のきまり：冒頭（hook）で「タートルアド」と名乗る行は、聞き取りやすいように自動でゆっくり読む
NAME_LINE_SPEED = 1.0

def to_read(sub, extra):
    t = sub.replace("**", "").replace("/", "")
    table = dict(READING); table.update(extra or {})
    for k in sorted(table, key=len, reverse=True):
        t = t.replace(k, table[k])
    return t

# ------------------------------------------------------------------ ① 声づくり（VOICEVOX）
_op = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # localhost はプロキシを通さない

def vv(path, params, body=None, method="POST"):
    url = VV + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, data=body if method == "POST" else None, method=method,
                                 headers={"Content-Type": "application/json"})
    return _op.open(req, timeout=180).read()

def speaker_id(name="春日部つむぎ"):
    try:
        for s in json.loads(vv("/speakers", None, method="GET")):
            if s["name"] == name:
                return next((x["id"] for x in s["styles"] if x["name"] == "ノーマル"), s["styles"][0]["id"])
    except Exception as e:
        sys.exit(f"VOICEVOX につながりません（{VV}）。毎日の手順.md の「VOICEVOXを起動」を先に。詳細: {e}")
    sys.exit(f"VOICEVOX に「{name}」がいません")

def read_wav(p):
    with wave.open(p) as f:
        sr = f.getframerate(); a = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
        if f.getnchannels() == 2: a = a.reshape(-1, 2).mean(1)
    if sr != SR:
        x = np.arange(len(a)) / sr; a = np.interp(np.arange(int(len(a) * SR / sr)) / SR, x, a).astype(np.float32)
    return a

def write_wav(p, a):
    a = np.clip(a, -1, 1)
    with wave.open(p, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((a * 32767).astype(np.int16).tobytes())

def synth(text, spk, speed, cache_dir):
    key = hashlib.sha1(f"{spk}|{speed}|v2|{text}".encode()).hexdigest()[:16]
    wp, jp = os.path.join(cache_dir, key + ".wav"), os.path.join(cache_dir, key + ".json")
    if os.path.exists(wp) and os.path.exists(jp):
        return read_wav(wp), json.load(open(jp))
    q = json.loads(vv("/audio_query", {"text": text, "speaker": spk}))
    q["speedScale"] = speed; q["intonationScale"] = 1.15; q["prePhonemeLength"] = 0.06
    q["postPhonemeLength"] = 0.06; q["pauseLengthScale"] = 0.85
    open(wp, "wb").write(vv("/synthesis", {"speaker": spk}, json.dumps(q).encode()))
    a = read_wav(wp); dur = len(a) / SR
    t = q["prePhonemeLength"] / speed; vis = []
    for ap in q["accent_phrases"]:
        for m in ap["moras"]:
            c = (m.get("consonant_length") or 0) / speed; v = m["vowel_length"] / speed
            vis.append([t + c * 0.6, t + c + v, m["vowel"]]); t += c + v
        if ap.get("pause_mora"):
            t += ap["pause_mora"]["vowel_length"] * 0.85 / speed
    k = dur / (t + q["postPhonemeLength"] / speed)
    meta = {"dur": dur, "kana": q["kana"], "vis": [[round(a_ * k, 3), round(b_ * k, 3), v] for a_, b_, v in vis]}
    json.dump(meta, open(jp, "w"), ensure_ascii=False)
    return a, meta

# ------------------------------------------------------------------ 文字の幅（はみ出し防止）
_fonts = {}
def font(kind, sz):
    if (kind, sz) not in _fonts:
        f = "NotoSansJP-Bold.ttf" if kind == "B" else "RoundedMplus1c-ExtraBold.ttf"
        _fonts[(kind, sz)] = ImageFont.truetype(os.path.join(FONT_DIR, f), sz)
    return _fonts[(kind, sz)]
def plain(s): return re.sub(r"<[^>]+>", "", s.replace("**", ""))
def width(s, sz, kind="B"): return font(kind, sz).getlength(plain(s)) * 1.03
def fit(lines, start, minimum, maxw, kind="B"):
    sz = start
    while sz > minimum and max(width(x, sz, kind) for x in lines) > maxw: sz -= 2
    return sz

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def mark(s, hl=()):
    """**強調** → 黄色。"/" → 改行。hl の言葉も黄色に。"""
    out = []
    for line in s.split("/"):
        parts = line.split("**"); h = ""
        for i, p in enumerate(parts):
            p = esc(p)
            if i % 2 == 0:
                for w in hl:
                    if w and esc(w) in p and "hl" not in p:
                        p = p.replace(esc(w), f'<span class="hl">{esc(w)}</span>', 1)
                h += p
            else:
                h += f'<span class="hl">{p}</span>'
        out.append(h)
    return "<br/>".join(out)

def wrap_sub(sub, maxw=790):
    """字幕：1行が長すぎるときは「、」か真ん中で2行にする。"""
    lines = sub.split("/")
    out = []
    for ln in lines:
        if width(ln, 44) <= maxw or len(lines) > 1:
            out.append(ln); continue
        p = plain(ln); mid = len(p) // 2
        cands = [i + 1 for i, ch in enumerate(p) if ch in "、。，" and 0 < i + 1 < len(p)]
        cut = min(cands, key=lambda i: abs(i - mid)) if cands else mid
        # ** の中で切らないよう、plain の位置を元の文字列の位置に直す
        j = 0; seen = 0
        while seen < cut and j < len(ln):
            if ln.startswith("**", j): j += 2; continue
            j += 1; seen += 1
        out += [ln[:j], ln[j:]]
    return "/".join(out)

# ------------------------------------------------------------------ 音（効果音・BGM。すべて自作の音で著作権の心配なし）
def tone(freq, dur, decay, harm=0.3):
    tt = np.arange(int(SR * dur)) / SR
    env = np.exp(-tt * decay) * np.minimum(1, tt / 0.006)
    return (np.sin(2 * np.pi * freq * tt) + harm * np.sin(2 * np.pi * freq * 2 * tt)) * env
def chime(freq=1318.5, dur=0.45):
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 9) * np.minimum(1, t / 0.005)
    return (0.6 * np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 1.5 * t)) * env
def whoosh(dur=0.55):
    rng = np.random.default_rng(7); n = int(SR * dur); x = rng.standard_normal(n)
    out = np.zeros(n); acc = 0.0
    for i in range(n):
        a = 0.02 + 0.25 * math.sin(math.pi * i / n); acc += a * (x[i] - acc); out[i] = acc
    return out * np.sin(np.pi * np.arange(n) / n) ** 2 * 0.9
def bgm_track(total, N):
    def note(f): return 440 * 2 ** ((f - 69) / 12)
    CH = [[48, 55, 59, 64, 67], [45, 52, 55, 60, 64], [41, 48, 52, 57, 60], [43, 50, 55, 59, 64]]
    b = np.zeros(N, np.float32)
    for bar in range(int(total / 2.4) + 2):
        ch = CH[bar % 4]; t0 = bar * 2.4
        pad = tone(note(ch[0] - 12), 2.6, 0.6, 0.15) * 0.35; i = int(t0 * SR); b[i:i + len(pad)] += pad[:max(0, N - i)]
        for e in range(8):
            a = tone(note(ch[1 + (e * 3) % 4] + 12), 0.9, 5.5, 0.12) * (0.32 if e % 2 == 0 else 0.22)
            i = int((t0 + e * 0.3) * SR); b[i:i + len(a)] += a[:max(0, N - i)]
    b = b / np.abs(b).max() * 0.5
    fade = np.ones(N); fo = int(1.5 * SR); e_i = int(total * SR); fade[max(0, e_i - fo):e_i] = np.linspace(1, 0, min(fo, e_i)); fade[e_i:] = 0
    fade[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
    return b * fade

# ------------------------------------------------------------------ HTML の共通部品
FONT_CSS = """
    @font-face { font-family: "NotoJP"; src: url("assets/fonts/NotoSansJP-Bold.ttf"); font-weight: 700; }
    @font-face { font-family: "RoundM"; src: url("assets/fonts/RoundedMplus1c-ExtraBold.ttf"); font-weight: 800; }"""
COLORS = "--navy:#08101f; --cyan:#3cd6f0; --yellow:#ffcc4d; --ink:#08101f; --white:#ffffff; --dim:#b9c8e6; --card:rgba(4,7,15,0.86); --line:#06c755;"
BASE_CSS = """
    .card { position:absolute; left:100px; right:100px; background:var(--card); border:3px solid var(--cyan); border-radius:34px; }
    .center { display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }
    .num { position:absolute; left:28px; top:22px; width:92px; height:92px; border-radius:50%; background:var(--cyan); color:var(--ink);
      font-family:"RoundM"; font-size:52px; line-height:92px; text-align:center; }
    .htitle { position:absolute; left:142px; right:20px; top:20px; line-height:1.3; white-space:nowrap; }
    .hmeta { position:absolute; left:142px; right:20px; top:76px; font-size:28px; color:var(--dim); white-space:nowrap; }
    .big { line-height:1.3; white-space:nowrap; }
    .tag { display:inline-block; background:var(--yellow); color:var(--ink); font-size:34px; padding:6px 26px; border-radius:40px; }
    .hl { color:var(--yellow); }
    .c { color:var(--cyan); }
    .row { line-height:1.25; margin:8px 0; white-space:nowrap; }
    .small { font-size:28px; color:var(--dim); }
    .mem { display:flex; flex-direction:column; align-items:center; width:200px; }
    .ntag { margin-top:-6px; padding:2px 16px; border-radius:16px; color:#08101f; font-size:28px; line-height:1.35; white-space:nowrap; }"""

def comp_file(proj, name, body, js, css=""):
    open(os.path.join(proj, "compositions", f"{name}.html"), "w").write(f"""<template>
  <style>{FONT_CSS}
    #root {{ position:absolute; inset:0; {COLORS} font-family:"NotoJP"; color:#fff; }}{BASE_CSS}
{css}
  </style>
  <div id="root" data-composition-id="{name}" data-width="1080" data-height="1920">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{name}"] = tl;
  </script>
</template>
""")

ICON = {
    "pin": '<svg width="96" height="96" viewBox="0 0 100 100"><path d="M50 6C32 6 18 20 18 38c0 24 32 56 32 56s32-32 32-56C82 20 68 6 50 6z" fill="#ff6b6b"/><circle cx="50" cy="38" r="13" fill="#fff"/></svg>',
    "phone": '<svg width="96" height="96" viewBox="0 0 100 100"><path d="M30 8c4 0 8 12 10 20 1 4-6 8-6 12 0 8 18 26 26 26 4 0 8-7 12-6 8 2 20 6 20 10 0 6-8 22-22 22C42 92 8 58 8 30 8 16 24 8 30 8z" fill="#3cd6f0"/></svg>',
    "clock": '<svg width="96" height="96" viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" fill="none" stroke="#3cd6f0" stroke-width="9"/><path d="M50 24v28l18 12" fill="none" stroke="#ffcc4d" stroke-width="9" stroke-linecap="round"/></svg>',
    "check": '<svg width="56" height="56" viewBox="0 0 100 100"><circle cx="50" cy="50" r="44" fill="#3cd6f0"/><path d="M28 52l15 15 30-32" fill="none" stroke="#08101f" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}

# ------------------------------------------------------------------ メイン
def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if not args: sys.exit(__doc__)
    t_begin = time.time(); times = {}
    spath = os.path.abspath(args[0]); OUT = os.path.dirname(spath)
    sc = load_script(spath); T = TYPES[sc["type"]]; d = sc["_date"]
    speed = float(sc.get("speed", 1.22)); hl = sc.get("highlight", []); extra_read = sc.get("readings", {})
    date_tag = f"{d.month}/{d.day}({WEEK[d.weekday()]})"
    program = sc.get("program", T["program"])
    log(f"== {sc['date']} {program}（{sc['type']}）速さ {speed}")

    # ---------------- ① 声づくり
    t0 = time.time()
    cache = os.path.join(OUT, "voice"); os.makedirs(cache, exist_ok=True)
    spk = speaker_id()
    # 場面の並び：intro → item1..N → cta。各場面は beat（カード1枚）のリスト、beat はセリフ chunk のリスト
    scenes = [{"name": "intro", "beats": [{"card": None, "say": sc["hook"]["say"]}]}]
    for i, it in enumerate(sc["items"]):
        scenes.append({"name": f"item{i + 1}", "item": it, "beats": it["beats"]})
    scenes.append({"name": "cta", "beats": [{"card": None, "say": sc.get("cta_say", CTA_SAY)}]})
    HEAD, GAP_CHUNK, GAP_BEAT, GAP_SCENE = 0.12, 0.12, 0.25, 0.42
    t = HEAD; chunks = []
    for si, s in enumerate(scenes):
        if si: t += GAP_SCENE
        for bi, b in enumerate(s["beats"]):
            if bi: t += GAP_BEAT
            b["chunks"] = []
            for ci, c in enumerate(b["say"]):
                if ci: t += GAP_CHUNK
                c = norm_chunk(c); c["sub"] = wrap_sub(c["sub"])
                read = c["read"] or to_read(c["sub"], extra_read)
                sp = c["speed"]
                if sp is None and s["name"] == "intro" and "タートルアド" in c["sub"]: sp = NAME_LINE_SPEED
                sp = float(sp or speed); c["speed"] = sp
                a, meta = synth(read, spk, sp, cache)
                c.update(read=read, audio=a, dur=meta["dur"], vis=meta["vis"], kana=meta["kana"], s=round(t, 3), e=round(t + meta["dur"], 3))
                b["chunks"].append(c); chunks.append(c); t = c["e"]
            b["s"], b["e"] = b["chunks"][0]["s"], b["chunks"][-1]["e"]
        s["vs"], s["ve"] = s["beats"][0]["s"], s["beats"][-1]["e"]
    cta = scenes[-1]
    cta_voice_end = cta["ve"]
    # 宣伝カードは 4.5〜5.5 秒。声のあと少なくとも 1.3 秒残す
    for i, s in enumerate(scenes):
        s["start"] = 0.0 if i == 0 else round((scenes[i - 1]["ve"] + s["vs"]) / 2, 3)
    for i, s in enumerate(scenes[:-1]): s["end"] = scenes[i + 1]["start"]
    TOTAL = round(max(cta["start"] + 4.6, cta_voice_end + 1.3), 2)
    cta["end"] = TOTAL
    times["voice"] = time.time() - t0
    log(f"① 声づくり {times['voice']:.1f}秒 / セリフ {len(chunks)} 個 / 全体 {TOTAL} 秒")

    # ---------------- ② 場面組み立て
    t0 = time.time()
    PROJ = os.path.join(OUT, "project")
    if os.path.isdir(os.path.join(PROJ, "compositions")): shutil.rmtree(os.path.join(PROJ, "compositions"))
    os.makedirs(os.path.join(PROJ, "compositions"), exist_ok=True)
    for sub in ("img", "vendor"):
        shutil.copytree(os.path.join(TEMPLATE, "assets", sub), os.path.join(PROJ, "assets", sub), dirs_exist_ok=True)
    os.makedirs(os.path.join(PROJ, "assets", "fonts"), exist_ok=True)
    for f in ("NotoSansJP-Bold.ttf", "RoundedMplus1c-ExtraBold.ttf", "README.txt"):
        shutil.copy(os.path.join(FONT_DIR, f), os.path.join(PROJ, "assets", "fonts", f))
    shutil.copy(os.path.join(TEMPLATE, "hyperframes.json"), PROJ)
    if not os.path.exists(os.path.join(PROJ, "meta.json")):
        json.dump({"id": f"daily-{sc['date']}", "name": f"daily-{sc['date']}"}, open(os.path.join(PROJ, "meta.json"), "w"))
    AUD = os.path.join(PROJ, "assets", "audio"); os.makedirs(AUD, exist_ok=True)

    # 音
    N = int(TOTAL * SR) + SR
    voice = np.zeros(N, np.float32)
    for c in chunks:
        i = int(c["s"] * SR); voice[i:i + len(c["audio"])] += c["audio"][:max(0, N - i)]
    write_wav(os.path.join(AUD, "voice.wav"), voice[:int(TOTAL * SR)])
    sfx = np.zeros(N, np.float32)
    def put(a, t_abs, gain):
        i = max(0, int(t_abs * SR)); sfx[i:i + len(a)] += a[:max(0, N - i)] * gain
    WH = whoosh(); POP = tone(880, 0.18, 30, 0.2)
    for s in scenes[1:]:
        put(WH, s["start"] - 0.27, 0.22); put(chime(), s["vs"] - 0.02, 0.10)
    write_wav(os.path.join(AUD, "bgm.wav"), bgm_track(TOTAL, N)[:int(TOTAL * SR)])

    def loc(s, t_abs): return round(t_abs - s["start"], 3)

    # --- 字幕
    caps = []
    for c in chunks: caps.append([c["s"], c["e"], c["sub"]])
    for i in range(len(caps)):
        s_, e_, _ = caps[i]
        caps[i][0] = round(max(0.05, s_ - 0.04), 3)
        nxt = caps[i + 1][0] - 0.04 if i + 1 < len(caps) else e_ + 0.6
        caps[i][1] = round(min(nxt, e_ + 0.3, TOTAL), 3)
    cap_html, cap_js, warn = [], [], []
    for i, (s_, e_, text) in enumerate(caps):
        lines = text.split("/")
        fs = fit(lines, 54, 40, 790)
        if max(width(x, fs) for x in lines) > 820: warn.append(f"字幕がはみ出しそう: {plain(text)}")
        if len(lines) > 2: warn.append(f"字幕が3行以上: {plain(text)}")
        cap_html.append(f'    <div id="cap{i}" class="clip cap" data-start="{s_:.3f}" data-duration="{e_ - s_:.3f}" data-track-index="0"><span class="capbox" id="capb{i}" style="font-size:{fs}px;">{mark(text, hl)}</span></div>')
        cap_js.append(f'    tl.fromTo("#capb{i}", {{opacity:0, y:26, scale:0.94}}, {{opacity:1, y:0, scale:1, duration:0.2, ease:"back.out(2)"}}, {s_:.3f});\n'
                      f'    tl.to("#capb{i}", {{opacity:0, duration:0.1, ease:"power2.in"}}, {e_ - 0.1:.3f});')
    comp_file(PROJ, "captions", "\n".join(cap_html), "\n".join(cap_js), """    .cap { position:absolute; left:0; right:0; bottom:690px; text-align:center; overflow:visible; }
    .capbox { display:inline-block; padding:20px 40px; border-radius:28px; background:rgba(4,7,15,0.82);
      border:3px solid rgba(60,214,240,0.55); color:#fff; font-family:"NotoJP"; font-weight:700;
      line-height:1.42; letter-spacing:0.02em; white-space:nowrap; }""")

    # --- intro（0秒目から番組名と今日の見出しが出ている＝つかみ）
    intro = scenes[0]; di = intro["end"]
    hook_head = sc["hook"].get("headline", "")
    tsz = fit([program], 92, 56, 840)
    hsz = fit([hook_head], 54, 34, 820) if hook_head else 0
    dots = ""
    if len(sc["items"]) > 1:
        dots = "".join(f'<div id="in-d{k + 1}" class="num" style="position:static;width:64px;height:64px;line-height:64px;font-size:40px;">{k + 1}</div>' for k in range(len(sc["items"])))
    intro_html = f"""    <div id="in-title" class="clip" data-start="0" data-duration="{di:.3f}" data-track-index="0" style="position:absolute;left:0;top:385px;width:1080px;height:300px;">
      <div id="in-title-in" class="card center" style="top:0;height:300px;">
        <div id="in-kicker" style="font-family:RoundM;font-size:34px;line-height:1.2;" class="c">AI動画編集部</div>
        <div id="in-t1" class="big" style="font-size:{tsz}px;line-height:1.15;">{mark(program, ["AI"])}</div>
        {f'<div id="in-hook" class="big hl" style="font-size:{hsz}px;line-height:1.3;">{mark(hook_head)}</div>' if hook_head else ''}
        <div style="margin-top:8px;display:flex;gap:18px;align-items:center;">
          <div id="in-date" class="tag" style="font-size:36px;">{date_tag}</div>{dots}
        </div>
      </div>
    </div>
    <div id="in-disc" class="clip" data-start="0" data-duration="{di:.3f}" data-track-index="1" style="position:absolute;left:0;top:700px;width:1080px;height:100px;">
      <div id="in-disc-in" style="position:absolute;left:110px;right:110px;top:0;padding:9px 20px;background:rgba(4,7,15,0.78);border:2px solid rgba(185,200,230,0.6);border-radius:22px;font-size:28px;line-height:1.35;text-align:center;color:#dfe8fb;">{DISCLOSURE}</div>
    </div>"""
    intro_js = [f'    tl.fromTo("#in-title-in", {{scale:1.06}}, {{scale:1, duration:0.5, ease:"expo.out"}}, 0);',
                f'    tl.fromTo("#in-date", {{scale:2.2, opacity:0, rotation:-12}}, {{scale:1, opacity:1, rotation:-4, duration:0.3, ease:"power4.in"}}, 0.3);',
                f'    tl.fromTo("#in-disc-in", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.4, ease:"power2.out"}}, 0.1);',
                f'    tl.to("#in-title-in", {{opacity:0, scale:0.96, duration:0.2, ease:"power2.in"}}, {di - 0.22:.3f});',
                f'    tl.to("#in-disc-in", {{opacity:0, duration:0.2}}, {di - 0.22:.3f});']
    if hook_head: intro_js.insert(1, '    tl.fromTo("#in-hook", {scale:0.9}, {scale:1, duration:0.4, ease:"back.out(2)"}, 0);')
    for k in range(len(sc["items"]) if dots else 0):
        intro_js.append(f'    tl.fromTo("#in-d{k + 1}", {{scale:0}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}, {0.7 + 0.18 * k:.3f});')
    comp_file(PROJ, "intro", intro_html, "\n".join(intro_js))

    # --- ニュース（1つの場面＝見出しカード＋ポイントのカード）
    BODY_TOP, BODY_H = 520, 260
    team_windows = []
    pop_times = []
    multi = len(sc["items"]) > 1
    def card_html(bid, card, nrows_out):
        ty = card.get("type", "title")
        if ty == "title":
            lines = card["text"].split("/"); sz = fit(lines, 58 if (card.get("chip") and len(lines) > 1) else 72, 40, 820)
            h = f'<div class="big" style="font-size:{sz}px;">{mark(card["text"], hl)}</div>'
            if card.get("chip"): h += f'<div id="{bid}-chip" class="tag" style="margin-top:12px;font-size:32px;">{esc(card["chip"])}</div>'
            return h, []
        if ty == "number":
            top = card.get("top", ""); val = card["value"]
            numline = f'{card.get("prefix", "")}{val}{card.get("suffix", "")}{card.get("after", "")}'
            nsz = fit([numline], 112, 64, 840)
            h = (f'<div style="font-size:40px;">{mark(top)}</div>' if top else "") + \
                f'<div style="font-size:{nsz}px;line-height:1.1;white-space:nowrap;" class="hl">{esc(card.get("prefix", ""))}<span id="{bid}-count">{val}</span>{esc(card.get("suffix", ""))}<span style="font-size:{int(nsz * 0.64)}px;color:#fff;">{esc(card.get("after", ""))}</span></div>' + \
                (f'<div class="small">{esc(card["note"])}</div>' if card.get("note") else "")
            return h, ["count"]
        if ty == "stamp":
            h = f'<div id="{bid}-stamp" style="font-family:RoundM;font-size:96px;color:#ff6b6b;border:10px solid #ff6b6b;border-radius:26px;padding:0 40px;line-height:1.3;">{esc(card["stamp"])}</div>'
            if card.get("text"): h += f'<div style="font-size:40px;margin-top:14px;">{mark(card["text"], hl)}</div>'
            return h, ["stamp"]
        if ty in ("points", "tip"):
            items = card["items"][:3]
            rows = [(x.replace("→", "<span class=\"c\">→</span>") if "<" not in x else x) for x in items]
            maxw = 760 if ty == "points" else 820
            sz = fit([plain(x) + ("　" if ty == "points" else "") for x in items], 46 if len(items) < 3 else 42, 30, maxw)
            h = ""
            if ty == "tip": h += f'<div class="tag" style="margin-bottom:10px;font-size:32px;">{esc(card.get("label", TIP_LABEL))}</div>'
            elif card.get("title"): h += f'<div style="font-size:34px;color:var(--dim);margin-bottom:6px;">{esc(card["title"])}</div>'
            for r_i, (raw, x) in enumerate(zip(items, rows)):
                html_x = mark(raw, hl).replace("→", '<span class="c">→</span>')
                pre = f'<span style="display:inline-block;vertical-align:middle;margin-right:14px;">{ICON["check"]}</span>' if ty == "points" else ""
                h += f'<div id="{bid}-r{r_i}" class="row" style="font-size:{sz}px;">{pre}{html_x}</div>'
            nrows_out.append(len(items))
            return h, ["rows"]
        if ty == "team":
            # 仲間の紹介：キャラクター画像＋名札（3体＋2体の2段）
            mem = card["members"]; cells = []
            for k, m in enumerate(mem):
                src = os.path.join(ROOT, m["img"]); dst = f"team_{k}.png"
                shutil.copy(src, os.path.join(PROJ, "assets", "img", dst))
                col = m.get("color", "#3cd6f0")
                cells.append(f'<div id="{bid}-m{k}" class="mem"><img src="assets/img/{dst}" style="width:176px;height:176px;image-rendering:pixelated;" />'
                             f'<div class="ntag" style="background:{col};">{esc(m["name"])}</div></div>')
            top = f'<div style="font-size:36px;margin-bottom:4px;">{mark(card.get("title", "AIの仲間たち"), hl)}</div>'
            rows_ = [cells[:3], cells[3:]] if len(cells) > 3 else [cells]
            h = top + "".join(f'<div style="display:flex;gap:30px;justify-content:center;">{"".join(r)}</div>' for r in rows_)
            nrows_out.append(len(mem))
            return h, ["team"]
        if ty == "icon":
            ic = ICON.get(card.get("icon", "pin"), ICON["pin"])
            lines = card["text"].split("/"); sz = fit(lines, 50, 34, 640)
            return f'<div style="display:flex;gap:26px;align-items:center;"><span id="{bid}-ic" style="display:inline-block;">{ic}</span><div style="font-size:{sz}px;text-align:left;line-height:1.3;">{mark(card["text"], hl)}</div></div>' + \
                   (f'<div class="small" style="margin-top:10px;">{esc(card["note"])}</div>' if card.get("note") else ""), ["icon"]
        sys.exit(f"カードの type が不明: {ty}")

    for n, s in enumerate(scenes[1:-1]):
        it = s["item"]; sid = s["name"]; dur = round(s["end"] - s["start"], 3)
        num = str(n + 1) if multi else T["icon"]
        meta = "　｜　".join(x for x in (it.get("date_label", ""), it.get("source_label", "")) if x)
        htsz = fit([it["headline"]], 40, 28, 760)
        html = [f"""    <div id="{sid}-head" class="clip" data-start="0" data-duration="{dur:.3f}" data-track-index="0" style="position:absolute;left:0;top:385px;width:1080px;height:120px;">
      <div id="{sid}-headin" class="card" style="top:0;height:120px;">
        <div id="{sid}-num" class="num" style="{'font-size:44px;' if len(num) > 1 else ''}">{esc(num)}</div>
        <div id="{sid}-ht" class="htitle" style="font-size:{htsz}px;">{mark(it['headline'], [])}</div>
        <div id="{sid}-hm" class="hmeta">{esc(meta)}</div>
      </div>
    </div>"""]
        js = [f'    tl.fromTo("#{sid}-headin", {{x:900, opacity:0}}, {{x:0, opacity:1, duration:0.45, ease:"expo.out"}}, 0.05);',
              f'    tl.fromTo("#{sid}-num", {{scale:0, rotation:-90}}, {{scale:1, rotation:0, duration:0.5, ease:"back.out(2.4)"}}, 0.2);',
              f'    tl.fromTo("#{sid}-hm", {{opacity:0}}, {{opacity:1, duration:0.3}}, 0.5);',
              f'    tl.to("#{sid}-headin", {{opacity:0, duration:0.2, ease:"power2.in"}}, {dur - 0.22:.3f});']
        beats = s["beats"]
        for i, b in enumerate(beats):
            bid = f"{sid}-b{i}"
            bs = 0.2 if i == 0 else loc(s, b["s"]) - 0.1
            be = loc(s, beats[i + 1]["s"]) - 0.1 if i + 1 < len(beats) else dur
            nrows = []
            inner, feats = card_html(bid, b["card"] or {"type": "title", "text": it["headline"]}, nrows)
            bh = 500 if "team" in feats else BODY_H
            if "team" in feats: team_windows.append((s["start"] + bs, s["start"] + be))
            html.append(f"""    <div id="{bid}" class="clip" data-start="{bs:.3f}" data-duration="{be - bs:.3f}" data-track-index="1" style="position:absolute;left:0;top:{BODY_TOP}px;width:1080px;height:{bh}px;">
      <div id="{bid}-in" class="card center" style="top:0;height:{bh}px;">
        {inner}
      </div>
    </div>""")
            kind = "pop" if b["card"] and b["card"].get("type") in ("number", "stamp") else "up"
            if kind == "up":
                js.append(f'    tl.fromTo("#{bid}-in", {{opacity:0, y:60}}, {{opacity:1, y:0, duration:0.38, ease:"power3.out"}}, {bs:.3f});')
            else:
                js.append(f'    tl.fromTo("#{bid}-in", {{opacity:0, scale:0.8}}, {{opacity:1, scale:1, duration:0.34, ease:"back.out(1.8)"}}, {bs:.3f});')
            js.append(f'    tl.to("#{bid}-in", {{opacity:0, y:-30, duration:0.18, ease:"power2.in"}}, {be - 0.2:.3f});')
            cs = [loc(s, c["s"]) for c in b["chunks"]]
            if "count" in feats:
                v = b["card"]["value"]; dec = 1 if isinstance(v, float) and not float(v).is_integer() else 0
                js.append(f'    const {bid.replace("-", "_")}c = {{v:0}};\n    tl.fromTo({bid.replace("-", "_")}c, {{v:0}}, {{v:{v}, duration:0.7, ease:"power2.out", onUpdate:()=>{{ document.querySelector("#{bid}-count").textContent = {bid.replace("-", "_")}c.v.toFixed({dec}); }}}}, {bs + 0.3:.3f});')
                for k in range(10): pop_times.append((s["start"] + bs + 0.3 + 0.06 * k, "tick"))
            if "stamp" in feats:
                js.append(f'    tl.fromTo("#{bid}-stamp", {{scale:2.6, rotation:-20, opacity:0}}, {{scale:1, rotation:-8, opacity:1, duration:0.22, ease:"power4.in"}}, {bs + 0.12:.3f});')
                pop_times.append((s["start"] + bs + 0.34, "thud"))
            if "icon" in feats:
                js.append(f'    tl.fromTo("#{bid}-ic", {{y:-50, opacity:0}}, {{y:0, opacity:1, duration:0.45, ease:"bounce.out"}}, {bs + 0.25:.3f});')
            if "team" in feats:
                for k in range(nrows[0]):
                    js.append(f'    tl.fromTo("#{bid}-m{k}", {{opacity:0, y:40, scale:0.6}}, {{opacity:1, y:0, scale:1, duration:0.32, ease:"back.out(2.2)"}}, {bs + 0.25 + 0.14 * k:.3f});')
                    js.append(f'    tl.fromTo("#{bid}-m{k}", {{y:0}}, {{y:-10, duration:0.25, ease:"sine.inOut", yoyo:true, repeat:1, immediateRender:false}}, {bs + 1.2 + 0.1 * k:.3f});')
                    pop_times.append((s["start"] + bs + 0.25 + 0.14 * k, "pop"))
            if "rows" in feats:
                nr = nrows[0]
                if len(cs) >= nr: at = [cs[0] + 0.3] + cs[1:nr]
                else:
                    span = (be - 0.6) - (bs + 0.3); at = [bs + 0.3 + span * k / max(1, nr) for k in range(nr)]
                for k in range(nr):
                    js.append(f'    tl.fromTo("#{bid}-r{k}", {{opacity:0, x:-60}}, {{opacity:1, x:0, duration:0.35, ease:"power3.out"}}, {at[k]:.3f});')
                    pop_times.append((s["start"] + at[k], "pop"))
            if b["card"] and b["card"].get("chip"):
                js.append(f'    tl.fromTo("#{bid}-chip", {{scale:0}}, {{scale:1, duration:0.35, ease:"back.out(2.5)"}}, {bs + 1.0:.3f});')
        comp_file(PROJ, sid, "\n".join(html), "\n".join(js))

    for tt, kind in pop_times:
        if kind == "pop": put(POP, tt, 0.10)
        elif kind == "thud": put(tone(150, 0.35, 12, 0.6), tt, 0.35)
        else: put(tone(1500 + 60 * (tt % 1), 0.05, 60, 0.0), tt, 0.04)

    # --- 宣伝カード（最後 4.5〜5.5 秒）
    cd = round(TOTAL - cta["start"], 3); c0 = loc(cta, cta["vs"])
    cta_html = f"""    <div id="cta-card" class="clip" data-start="0.05" data-duration="{cd - 0.05:.3f}" data-track-index="0" style="position:absolute;left:0;top:385px;width:1080px;height:520px;">
      <div id="cta-in" class="card center" style="top:0;height:520px;padding:0 30px;">
        <div id="cta-h" style="font-size:46px;line-height:1.32;white-space:nowrap;">このキャラクターのような<span class="hl">AI動画</span>を、<br/><span class="hl">御社のロゴ</span>から作ります</div>
        <div id="cta-tag" class="tag" style="font-size:36px;margin-top:16px;">キャラクターAI動画のご相談はこちら</div>
        <div id="cta-line" style="margin-top:18px;display:flex;align-items:center;gap:16px;">
          <span style="display:inline-block;background:var(--line);color:#fff;font-family:RoundM;font-size:30px;padding:2px 18px;border-radius:14px;">LINE公式</span>
          <span style="font-size:48px;letter-spacing:0.02em;">{LINE_ID}</span>
        </div>
        <div id="cta-site" style="margin-top:6px;font-size:44px;" class="c">{SITE}</div>
        <div id="cta-disc" style="margin-top:12px;font-size:28px;line-height:1.45;color:#dfe8fb;">{DISCLOSURE}<br/><span style="color:var(--cyan);">音声：{CREDIT}</span></div>
      </div>
    </div>"""
    cta_js = f"""    tl.fromTo("#cta-in", {{opacity:0, scale:0.85}}, {{opacity:1, scale:1, duration:0.45, ease:"back.out(1.6)"}}, 0.05);
    tl.fromTo("#cta-h", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:0.35, ease:"power3.out"}}, 0.2);
    tl.fromTo("#cta-tag", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:0.35, ease:"power3.out"}}, 0.55);
    tl.fromTo("#cta-tag", {{scale:1}}, {{scale:1.06, duration:0.4, yoyo:true, repeat:3, ease:"sine.inOut", immediateRender:false}}, 1.4);
    tl.fromTo("#cta-line", {{opacity:0, x:-50}}, {{opacity:1, x:0, duration:0.35, ease:"power3.out"}}, 0.85);
    tl.fromTo("#cta-site", {{opacity:0, x:50}}, {{opacity:1, x:0, duration:0.35, ease:"power3.out"}}, 1.05);
    tl.fromTo("#cta-disc", {{opacity:0}}, {{opacity:1, duration:0.35}}, 1.3);"""
    comp_file(PROJ, "cta", cta_html, cta_js)
    put(chime(1046.5, 0.8), cta["start"] + 0.9, 0.10)

    # --- 上の帯・クレジット（いつも出ている）
    top_txt = f'<span style="color:var(--cyan);">AI動画編集部</span><br/>{esc(program)} <span style="color:var(--yellow);">{d.month}/{d.day}号</span>'
    tbsz = fit([f"{program} {d.month}/{d.day}号"], 38, 28, 820, "R")
    comp_file(PROJ, "chrome", f"""    <div id="topbar-in" data-layout-ignore>
      <img id="toplogo" src="assets/img/logo.png" style="width:84px;height:84px;" />
      <div style="font-family:RoundM;font-size:{tbsz}px;line-height:1.15;">{top_txt}</div>
    </div>
    <div id="band">AIが情報収集から動画まで作っています</div>
    <div id="credit" data-layout-ignore>turtle ad ｜ 音声：{CREDIT}</div>""",
    """    tl.fromTo("#topbar-in", {y:-30}, {y:0, duration:0.4, ease:"power3.out"}, 0);
    tl.fromTo("#band", {y:-12}, {y:0, duration:0.45, ease:"expo.out"}, 0);
    tl.fromTo("#toplogo", {rotation:0}, {rotation:360, duration:0.8, ease:"power2.inOut"}, 0.1);""",
    """    #topbar-in { position:absolute; left:60px; right:60px; top:150px; height:108px; display:flex; align-items:center; gap:20px; }
    #band { position:absolute; left:90px; right:90px; top:292px; height:68px; border-radius:34px; background:var(--yellow); color:var(--ink); font-size:36px; line-height:68px; text-align:center; }
    #credit { position:absolute; left:0; right:0; top:1262px; height:44px; text-align:center; font-size:26px; color:var(--dim); }""")

    # --- タートル（口パク・まばたき・手をふる・お辞儀）
    segs = []
    for c in chunks:
        for a_, b_, v in c["vis"]:
            st = 2 if v in ("a", "o", "e") else 1 if v in ("i", "u") else 0
            if st: segs.append((c["s"] + a_, c["s"] + b_, st))
    changes = [(0.0, 0)]
    for a_, b_, st in segs:
        a_ = round(a_ * FPS) / FPS; b_ = round(b_ * FPS) / FPS
        if b_ - a_ < 1 / FPS: b_ = a_ + 1 / FPS
        if changes[-1][0] > a_: a_ = changes[-1][0]
        if changes[-1][1] != st: changes.append((a_, st))
        changes.append((b_, 0))
    clean = [changes[0]]
    for i in range(1, len(changes)):
        tc, st = changes[i]
        if i + 1 < len(changes) and st == 0 and changes[i + 1][0] - tc < 1.5 / FPS: continue
        if clean[-1][1] == st: continue
        clean.append((tc, st))
    blinks = sorted(round(b_ + (0.4 if int(b_) % 2 else 0), 2) for b_ in list(np.arange(2.6, TOTAL - 0.5, 3.1)) + [0.9])
    events = sorted([(t_, "m", st) for t_, st in clean] + [(b_, "b", 1) for b_ in blinks] + [(round(b_ + 0.13, 3), "b", 0) for b_ in blinks])
    mouth_js = []; cm, cb = 0, 0
    for t_, kind, v in events:
        if kind == "m": cm = v
        else: cb = v
        mouth_js.append(f'[{t_:.3f},"#tm{cm}{cb}"]')
    imgs = "\n".join(f'        <img id="tm{m}{b}" src="assets/img/turtle_m{m}_b{b}.png" class="tface" style="opacity:{1 if (m, b) == (0, 0) else 0};" />' for m in (0, 1, 2) for b in (0, 1))
    cs_ = cta["start"]; breathe_end = cs_ - 0.4
    breathe_rep = max(0, int((breathe_end - 1.5) / 1.2) - 1)
    bow_t = max(cs_ + 1.6, TOTAL - 2.0)
    comp_file(PROJ, "turtle", f"""    <div id="mover"><div id="bow"><div id="rig">
{imgs}
    </div></div></div>""", f"""    // はじめに手をふる → 呼吸
    tl.fromTo("#rig", {{rotation:0, y:0}}, {{rotation:7, y:-14, duration:0.22, ease:"sine.inOut", yoyo:true, repeat:5, transformOrigin:"50% 90%"}}, 0.05);
    tl.fromTo("#rig", {{scaleY:1}}, {{scaleY:1.025, duration:1.2, ease:"sine.inOut", yoyo:true, repeat:{breathe_rep}, transformOrigin:"50% 100%", immediateRender:false}}, 1.5);
    // 宣伝カード：小さくなってカードの下へ → 手をふる → お辞儀
    tl.fromTo("#mover", {{scale:1, y:0}}, {{scale:0.58, y:30, duration:0.5, ease:"power3.inOut", transformOrigin:"50% 100%"}}, {cs_ - 0.2:.3f});
    tl.fromTo("#rig", {{rotation:0, y:0}}, {{rotation:9, y:-12, duration:0.2, ease:"sine.inOut", yoyo:true, repeat:5, transformOrigin:"50% 90%", immediateRender:false}}, {cs_ + 0.4:.3f});
    tl.fromTo("#bow", {{rotation:0, y:0, scaleY:1}}, {{rotation:-14, y:26, scaleY:0.9, duration:0.35, ease:"power2.out", yoyo:true, repeat:1, repeatDelay:0.45, transformOrigin:"50% 100%"}}, {bow_t:.3f});
    // 仲間の紹介のあいだは、タートルはいったん隠れる
{chr(10).join(f'    tl.to("#mover", {{opacity:0, duration:0.2}}, {a - 0.05:.3f});{chr(10)}    tl.to("#mover", {{opacity:1, duration:0.25}}, {b:.3f});' for a, b in team_windows)}
    // 口パク・まばたき（VOICEVOX の音の時刻から作った表）
    const faces = ["#tm00","#tm01","#tm10","#tm11","#tm20","#tm21"];
    const mouth = [{",".join(mouth_js)}];
    for (const [t, id] of mouth) {{ tl.set(faces.filter(f => f !== id), {{opacity:0}}, t); tl.set(id, {{opacity:1}}, t); }}""",
    """    #mover { position:absolute; left:375px; top:745px; width:330px; height:330px; }
    #bow, #rig { position:absolute; left:0; top:0; width:330px; height:330px; }
    .tface { position:absolute; left:0; top:0; width:330px; height:330px; image-rendering:pixelated; }""")

    # --- 場面転換のワイプ
    WB = [round(s["start"] - 0.32, 3) for s in scenes[1:]]
    comp_file(PROJ, "wipes", "\n".join(f'    <div id="wipe{i}-a" class="wbar" style="background:var(--cyan);" data-layout-ignore></div><div id="wipe{i}-b" class="wbar" style="background:var(--navy);" data-layout-ignore></div>' for i in range(len(WB))),
              "    tl.set(\".wbar\", {x:-2600, rotation:18}, 0);\n" + "\n".join(
                  f'    tl.fromTo("#wipe{i}-a", {{x:-2400, rotation:18}}, {{x:2400, rotation:18, duration:0.62, ease:"power2.inOut", immediateRender:false}}, {ws:.3f});\n'
                  f'    tl.fromTo("#wipe{i}-b", {{x:-2600, rotation:18}}, {{x:2200, rotation:18, duration:0.62, ease:"power2.inOut", immediateRender:false}}, {ws + 0.04:.3f});' for i, ws in enumerate(WB)),
              "    .wbar { position:absolute; left:0; top:-400px; width:900px; height:2720px; }")

    def host(n, s_, e_, track, z, kind="graphics"):
        return (f'      <div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{s_:.3f}" '
                f'data-duration="{e_ - s_:.3f}" data-track-index="{track}" data-track-kind="{kind}" data-width="1080" data-height="1920" style="z-index:{z};"></div>')
    scene_hosts = "\n".join(host(s["name"], s["start"], s["end"], 1, 10) for s in scenes)
    open(os.path.join(PROJ, "index.html"), "w").write(f"""<!doctype html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      :root {{ {COLORS} }}
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ margin:0; width:1080px; height:1920px; overflow:hidden; background:var(--navy); }}
      #root {{ position:relative; width:100%; height:100%; }}
      #bg {{ position:absolute; inset:0; }}
      #bg img {{ position:absolute; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <div id="bg" data-layout-ignore>
        <img id="bgimg" src="assets/img/bg.png" style="left:0;top:0;width:1080px;height:1920px;" />
        <img id="glow" src="assets/img/glow.png" style="left:90px;top:620px;width:900px;height:900px;" />
      </div>
{host("chrome", 0, TOTAL, 0, 5)}
{host("turtle", 0, TOTAL, 2, 20)}
{scene_hosts}
{host("captions", 0, TOTAL, 3, 30, "captions")}
{host("wipes", 0, TOTAL, 4, 40)}
      <audio id="voice" class="clip" src="assets/audio/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="6" data-volume="1"></audio>
      <audio id="bgm" class="clip" src="assets/audio/bgm.wav" data-start="0" data-duration="{TOTAL}" data-track-index="7" data-volume="0.22"></audio>
      <audio id="sfx" class="clip" src="assets/audio/sfx.wav" data-start="0" data-duration="{TOTAL}" data-track-index="8" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#glow", {{x:-60, y:0, scale:1}}, {{x:60, y:-40, scale:1.12, duration:{TOTAL / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:1}}, 0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
""")
    write_wav(os.path.join(AUD, "sfx.wav"), sfx[:int(TOTAL * SR)])
    times["build"] = time.time() - t0
    log(f"② 場面組み立て {times['build']:.1f}秒（{PROJ}）")

    # 秒数表・概要欄
    rows = ["| 時間（秒） | 場面 | 字幕 | 速さ | 読み（VOICEVOXの読み） |", "|---|---|---|---|---|"]
    for s in scenes:
        for b in s["beats"]:
            for c in b["chunks"]:
                rows.append(f"| {c['s']:.2f}〜{c['e']:.2f} | {s['name']} | {plain(c['sub']).replace('/', ' ')} | {c['speed']} | {c['kana']} |")
    open(os.path.join(OUT, "秒数表.md"), "w").write(
        f"# 秒数表（{sc['date']} {program}）\n\n- 縦1080×1920・30fps・全体 {TOTAL} 秒・声 VOICEVOX:春日部つむぎ 速さ {speed}\n- 場面："
        + " / ".join(f"{s['name']} {s['start']:.2f}〜{s['end']:.2f}" for s in scenes) + "\n\n" + "\n".join(rows) + "\n")
    srcs = [f"・{it['headline']}（{it.get('source_label', '').replace('出典：', '')}）\n  {it['source_url']}" for it in sc["items"] if it.get("source_url")]
    for it in sc["items"]:
        for u in it.get("source_urls_extra", []): srcs.append(f"  {u}")
    titles = sc.get("titles") or [f"{hook_head}｜{program} {d.month}/{d.day}"]
    title_txt = f"{sc['title']} #Shorts" if sc.get("title") else "\n".join(f"【タイトル案{k + 1}】{x} #Shorts" for k, x in enumerate(titles)) if len(titles) > 1 else f"【タイトル案】{titles[0]} #Shorts"
    src_txt = ("■ 出典\n" + "\n".join(srcs) + "\n\n") if srcs else ""
    tags = sc.get("hashtags", "#AIニュース #生成AI #中小企業 #タートルアド")
    desc = f"""{title_txt}

{sc.get('description_extra', '')}

■ キャラクターAI動画のご相談（御社のロゴからキャラクター動画を作ります）
LINE公式：https://line.me/R/ti/p/{LINE_ID}
ホームページ：https://{SITE}/

{src_txt}この動画は、タートルアドのAIチームが情報収集から台本・音声・映像まで作っています。
音声：{CREDIT}

{tags}
"""
    open(os.path.join(OUT, "概要欄.txt"), "w").write(desc)

    # ---------------- ③ チェック
    t0 = time.time()
    report = []
    if TOTAL < T["min"] or TOTAL > T["max"]:
        warn.append(f"長さ {TOTAL} 秒は、この型の目安 {T['min']}〜{T['max']} 秒の外です（セリフを足す・削る）")
    if not (4.5 <= cd <= 5.6): warn.append(f"宣伝カードの長さ {cd:.2f} 秒（目安 4.5〜5.5 秒）")
    if scenes[0]["vs"] > 0.3: warn.append("つかみの声の始まりが遅い")
    for it in (sc["items"] if sc["type"] != "greeting" else []):
        if not it.get("source_url"): warn.append(f"出典URLがありません: {it['headline']}")
    env = dict(os.environ, **TELEMETRY_OFF)
    hf = ["node", HF_CLI] if os.path.exists(HF_CLI) else ["npx", "--yes", "hyperframes@0.9.72"]
    r = subprocess.run(hf + ["check", "--json"], cwd=PROJ, env=env, capture_output=True, text=True)
    errs = None
    try:
        j = json.loads(r.stdout[r.stdout.index("{"):])
        open(os.path.join(OUT, "check.json"), "w").write(json.dumps(j, ensure_ascii=False, indent=1))
        errs = sum(int(v.get("errorCount", 0)) for v in j.values() if isinstance(v, dict))
        if j.get("ok") is False and errs == 0: errs = 1
        wn = sum(int(v.get("warningCount", 0)) for v in j.values() if isinstance(v, dict))
        report.append(f"hyperframes check: ok={j.get('ok')} エラー {errs} / 注意 {wn}（中身は check.json）")
    except Exception:
        report.append("hyperframes check の結果が読めません:\n" + (r.stdout[-2000:] + r.stderr[-2000:]))
    times["check"] = time.time() - t0
    report += [f"注意: {w}" for w in warn] or ["注意: なし"]
    log("③ チェック\n  " + "\n  ".join(report))
    blocked = (errs is None or errs > 0 or r.returncode != 0)
    if blocked and "--force" not in flags:
        open(os.path.join(OUT, "チェック結果.txt"), "w").write("\n".join(report) + "\n")
        sys.exit("チェックでエラー。check.json を見て直すか、--force で書き出し。")

    # ---------------- ④ 書き出し
    mp4 = os.path.join(OUT, f"turtle_ai_{sc['date']}.mp4")
    if "--no-render" in flags:
        open(os.path.join(OUT, "チェック結果.txt"), "w").write("\n".join(report) + "\n（書き出しなし）\n")
        log(f"書き出しなしで終了（{time.time() - t_begin:.0f}秒）"); return
    t0 = time.time()
    q = "draft" if "--draft" in flags else "delivery"
    with open(os.path.join(OUT, "render.log"), "w") as lf:
        r = subprocess.run(hf + ["render", "--quality", q, "-o", mp4], cwd=PROJ, env=env, stdout=lf, stderr=subprocess.STDOUT)
    times["render"] = time.time() - t0
    if r.returncode != 0 or not os.path.exists(mp4): sys.exit(f"書き出し失敗。{OUT}/render.log を見てください")
    log(f"④ 書き出し {times['render']:.0f}秒 → {mp4}")

    # ---------------- ⑤ 確認（長さ・確認コマ）
    t0 = time.time()
    real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout.strip() or 0)
    report.append(f"MP4の長さ {real:.2f} 秒（予定 {TOTAL} 秒）" + ("" if abs(real - TOTAL) < 0.2 else " ← ずれあり"))
    ast = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name", "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout.strip()
    report.append("音声トラック: " + (ast or "なし ← 要確認"))
    shots = [0.1, 1.2] + [round((b["s"] + b["e"]) / 2, 2) for s in scenes[1:-1] for b in s["beats"]] + [round(cta["start"] + 1.8, 2), round(TOTAL - 0.15, 2)]
    fdir = os.path.join(OUT, "確認コマ"); shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    ims = []
    for k, ts in enumerate(shots):
        p = os.path.join(fdir, f"{k:02d}_{ts:05.2f}s.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ts), "-i", mp4, "-frames:v", "1", p])
        if os.path.exists(p): ims.append((ts, Image.open(p).convert("RGB")))
    cols = 4; tw, th = 270, 480; rows_n = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * tw, rows_n * (th + 30)), (20, 20, 20)); dd = ImageDraw.Draw(sheet)
    for k, (ts, im) in enumerate(ims):
        x, y = (k % cols) * tw, (k // cols) * (th + 30)
        sheet.paste(im.resize((tw, th)), (x, y + 30)); dd.text((x + 8, y + 4), f"{ts:.2f}s", fill=(255, 255, 255), font=font("B", 20))
    sheet.save(os.path.join(fdir, "contact_sheet.jpg"), quality=88)
    times["verify"] = time.time() - t0
    total_t = time.time() - t_begin
    report.append("所要時間: " + " / ".join(f"{k} {v:.0f}秒" for k, v in times.items()) + f" / 合計 {total_t:.0f}秒")
    open(os.path.join(OUT, "チェック結果.txt"), "w").write("\n".join(report) + "\n")
    log("⑤ 確認\n  " + "\n  ".join(report[-4:]))
    log(f"完成: {mp4}\n確認コマ: {fdir}/contact_sheet.jpg\n概要欄: {OUT}/概要欄.txt")

if __name__ == "__main__":
    main()
