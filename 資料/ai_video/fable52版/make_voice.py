# 音声づくり（VOICEVOX:春日部つむぎ）。セリフごとにWAVを作り、口の形と字幕の時刻を voice/timing.json に書く。
# 使い方: python3 make_voice.py [話す速さ(例 1.0)] [VOICEVOXのURL]
import json, os, sys, urllib.request, urllib.parse, wave, re

SPEED = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
URL = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:50021"
SPK = 8  # 春日部つむぎ（ノーマル）
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "voice"); os.makedirs(OUT, exist_ok=True)

# セリフは台本_ショート.md のとおり。1つのセリフ = [(字幕, 読み), ...]。字幕の「/」は改行。
# 読みは台本の指定（Anthropic＝アンソロピック など）に合わせたカタカナ。
LINES = [
    ("intro1", [("タートルアドのタートルです。", "タートルアドのタートルです。")]),
    ("intro2", [("今週のAIニュースを、/3つ紹介します。", "今週のエーアイニュースを、みっつ紹介します。")]),
    ("n1a", [("ひとつめ。", "ひとつめ。"),
             ("Anthropicが、新しいAI/「Claude Fable 5.2」を出しました。", "アンソロピックが、新しいエーアイ、クロード・フェイブルごーてんにーを出しました。")]),
    ("n1b", [("前の型より、答えが出るのが/最大3割ほど速くなったそうです。", "前の型より、答えが出るのが最大3割ほど速くなったそうです。")]),
    ("n1c", [("ふだんの仕事は、今のAIで十分。", "ふだんの仕事は、今のエーアイで十分。"),
             ("むずかしい作業のときに/試すのがおすすめです。", "むずかしい作業のときに試すのがおすすめです。")]),
    ("n2a", [("ふたつめ。", "ふたつめ。"),
             ("ChatGPTで、/会社やお店の情報を、", "チャットジーピーティーで、会社やお店の情報を、"),
             ("自分で管理できる仕組みが/始まりました。", "自分で管理できる仕組みが始まりました。")]),
    ("n2b", [("まだ試験中の機能です。", "まだ試験中の機能です。")]),
    ("n2c", [("Googleマップと同じように、", "グーグルマップと同じように、"),
             ("AIの中で、自分の会社が/どう紹介されているか、", "エーアイの中で、自分の会社がどう紹介されているか、"),
             ("確かめる時代です。", "確かめる時代です。")]),
    ("n3a", [("みっつめ。", "みっつめ。"),
             ("GoogleのGeminiの/「タスク」機能が、", "グーグルのジェミニのタスク機能が、"),
             ("日本でも無料になりました。", "日本でも無料になりました。")]),
    ("n3b", [("アメリカでは、/AIがお店に電話して、", "アメリカでは、エーアイがお店に電話して、"),
             ("値段を聞くこともできます。", "値段を聞くこともできます。")]),
    ("n3c", [("AIがお客さんの代わりに/調べる時代。", "エーアイがお客さんの代わりに調べる時代。"),
             ("営業時間や料金は、/いつも最新にしておきましょう。", "営業時間や料金は、いつも最新にしておきましょう。")]),
    ("out1", [("AIは、毎週のように/新しくなっています。", "エーアイは、毎週のように新しくなっています。")]),
    ("out2", [("タートルアドでは、AIの使い方の/ご相談を受け付けています。", "タートルアドでは、エーアイの使い方のご相談を受け付けています。"),
              ("また来週。", "また来週。")]),
]

def post(path, params, body=None):
    req = urllib.request.Request(URL + path + "?" + urllib.parse.urlencode(params), data=body or b"", method="POST",
                                 headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=120).read()

result = []
for key, chunks in LINES:
    reading = "".join(r for _, r in chunks)
    q = json.loads(post("/audio_query", {"text": reading, "speaker": SPK}))
    q["speedScale"] = SPEED; q["intonationScale"] = 1.15; q["prePhonemeLength"] = 0.08; q["postPhonemeLength"] = 0.08
    wav = post("/synthesis", {"speaker": SPK}, json.dumps(q).encode())
    path = os.path.join(OUT, key + ".wav"); open(path, "wb").write(wav)
    with wave.open(path) as f: dur = f.getnframes() / f.getframerate()
    # モーラごとの時刻（口の形用）と、読点・句点のポーズの時刻（字幕の切り替え用）
    t = q["prePhonemeLength"] / SPEED; vis = []; pauses = []
    for ap in q["accent_phrases"]:
        for m in ap["moras"]:
            c = (m.get("consonant_length") or 0) / SPEED; v = m["vowel_length"] / SPEED
            vis.append((round(t + c * 0.6, 3), round(t + c + v, 3), m["vowel"]))
            t += c + v
        if ap.get("pause_mora"):
            p = ap["pause_mora"]["vowel_length"] / SPEED
            pauses.append((round(t, 3), round(t + p, 3))); t += p
    est = t + q["postPhonemeLength"] / SPEED
    k = dur / est  # 計算と実際の長さのずれを合わせる
    vis = [(a * k, b * k, v) for a, b, v in vis]; pauses = [(a * k, b * k) for a, b in pauses]
    # 字幕の区切り：読みの中の「、。」の数で、何番目のポーズで切り替えるかを決める
    need = [len(re.findall("[、。]", r)) for _, r in chunks]
    total_p = sum(need) - 1
    subs = []; start = 0.0; acc = 0
    ok = (len(pauses) == total_p)
    for i, (disp, r) in enumerate(chunks):
        acc += need[i]
        if i == len(chunks) - 1: end = dur
        elif ok: end = pauses[acc - 1][1] - 0.03
        else: end = dur * sum(len(x[1]) for x in chunks[:i + 1]) / len(reading)
        subs.append({"text": disp, "s": round(start, 3), "e": round(end, 3)}); start = end
    result.append({"key": key, "file": path, "dur": round(dur, 3), "subs": subs, "vis": vis, "kana": q["kana"], "pause_ok": ok})
    print(key, f"{dur:.2f}s", "pause_ok" if ok else f"PAUSE MISMATCH {len(pauses)} vs {total_p}", q["kana"])
json.dump({"speed": SPEED, "lines": result}, open(os.path.join(OUT, "timing.json"), "w"), ensure_ascii=False, indent=1)
print("合計（セリフだけ）", round(sum(r["dur"] for r in result), 2), "秒")
