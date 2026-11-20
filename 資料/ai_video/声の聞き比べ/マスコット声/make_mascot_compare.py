# -*- coding: utf-8 -*-
"""マスコット声の聞き比べ動画を作る（HyperFrames）。

使い方: python3 資料/ai_video/声の聞き比べ/マスコット声/make_mascot_compare.py
前提: VOICEVOX ENGINE が 127.0.0.1:50021 で動いていること（daily/毎日の手順.md の 1-2・1-3）。
出力（このフォルダ）:
  聞き比べ_全部.mp4 … 全候補をつないだ1本
  候補/NN_<名前>.mp4 … 候補ごとの短い動画（全部の動画から切り出し）
  声/NN_<名前>.wav … 声だけ
  確認コマ/contact_sheet.jpg
キャラクターの絵は使わない（声だけ）。画面のキャラクターは自社のタートル。
"""
import json, os, shutil, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
DAILY = os.path.abspath(os.path.join(HERE, "..", "..", "daily"))
sys.path.insert(0, DAILY)
import make_daily as md  # noqa: E402  （声の読み込み・HTML部品・効果音を再利用）

SR, FPS = md.SR, md.FPS
LINE = [  # (字幕, 読み, 速さの倍率) … タートルアドのところはゆっくり
    ("はじめまして。", "はじめまして。", 1.0),
    ("タートルアドのAI社員、/タートルです。", "タートルアドのエーアイ社員、タートルです。", 0.84),
    ("毎日AIの情報を/お届けします！", "毎日エーアイの情報をお届けします！", 1.0),
]
# 候補：名前・スタイルID・速さ・高さ・抑揚・特徴・規約（エンジンの /speaker_info の policy で確認）
CANDS = [
    dict(key="zundamon", name="ずんだもん", style="ノーマル", id=3, speed=1.15, pitch=0.0, into=1.3,
         feat="定番のマスコット声。有名なので気づかれやすい",
         credit="VOICEVOX:ずんだもん", law="可", law_note="クレジット記載で商用・非商用OK（エンジン記載）"),
    dict(key="hau", name="雨晴はう", style="ノーマル", id=10, speed=1.15, pitch=0.03, into=1.3,
         feat="やさしく明るい。聞き取りやすく、案内役に向く",
         credit="VOICEVOX:雨晴はう", law="可", law_note="クレジット記載で商用・非商用OK（エンジン記載）"),
    dict(key="bii", name="猫使ビィ", style="ノーマル", id=58, speed=1.15, pitch=0.0, into=1.35,
         feat="幼くてかわいい。マスコットらしさが強い",
         credit="VOICEVOX:猫使ビィ", law="可", law_note="クレジット記載で商用・非商用OK（エンジン記載）"),
    dict(key="sayo", name="小夜/SAYO", style="ノーマル", id=46, speed=1.15, pitch=0.0, into=1.3,
         feat="小さな子のような声。ふんわりかわいい",
         credit="VOICEVOX:小夜/SAYO", law="可", law_note="クレジット記載で商用・非商用OK（エンジン記載）"),
    dict(key="hanamaru", name="満別花丸", style="元気", id=70, speed=1.15, pitch=0.0, into=1.3,
         feat="男の子っぽい元気な声。ロボット・相棒キャラに合う",
         credit="VOICEVOX:満別花丸", law="可", law_note="クレジット記載で商用・非商用OK（エンジン記載）"),
    dict(key="tsumugi_hi", name="春日部つむぎ", style="高め（マスコット寄り）", id=8, speed=1.18, pitch=0.06, into=1.35,
         feat="今の声を高く・抑揚強めに。今までの動画とつながる",
         credit="VOICEVOX:春日部つむぎ", law="可", law_note="クレジット記載で商用・非商用OK（エンジン記載）"),
]
EXCLUDED = [
    ("もち子さん", "要確認", "「企業が携わる形で利用する場合は、もちぞら模型店に事前確認」（エンジン記載）→ 候補から外した"),
    ("Voidoll", "要確認", "「法人による利用の場合は、個別に問い合わせが必要」（エンジン記載）→ 候補から外した"),
]

def synth(text, spk, speed, pitch, into, cache):
    import hashlib
    key = hashlib.sha1(f"{spk}|{speed}|{pitch}|{into}|{text}".encode()).hexdigest()[:16]
    wp, jp = os.path.join(cache, key + ".wav"), os.path.join(cache, key + ".json")
    if os.path.exists(wp) and os.path.exists(jp): return md.read_wav(wp), json.load(open(jp))
    q = json.loads(md.vv("/audio_query", {"text": text, "speaker": spk}))
    q.update(speedScale=speed, pitchScale=pitch, intonationScale=into, prePhonemeLength=0.06, postPhonemeLength=0.06, pauseLengthScale=0.85)
    open(wp, "wb").write(md.vv("/synthesis", {"speaker": spk}, json.dumps(q).encode()))
    a = md.read_wav(wp); dur = len(a) / SR
    t = q["prePhonemeLength"] / speed; vis = []
    for ap in q["accent_phrases"]:
        for m in ap["moras"]:
            c = (m.get("consonant_length") or 0) / speed; v = m["vowel_length"] / speed
            vis.append([t + c * 0.6, t + c + v, m["vowel"]]); t += c + v
        if ap.get("pause_mora"): t += ap["pause_mora"]["vowel_length"] * 0.85 / speed
    k = dur / (t + q["postPhonemeLength"] / speed)
    meta = {"dur": dur, "vis": [[a_ * k, b_ * k, v] for a_, b_, v in vis]}
    json.dump(meta, open(jp, "w")); return a, meta

def main():
    os.environ.update(md.TELEMETRY_OFF)
    PROJ = os.path.join(HERE, "project"); cache = os.path.join(HERE, "cache"); vdir = os.path.join(HERE, "声")
    for d_ in (cache, vdir, os.path.join(PROJ, "compositions"), os.path.join(PROJ, "assets", "audio"), os.path.join(PROJ, "assets", "fonts")):
        os.makedirs(d_, exist_ok=True)
    for sub in ("img", "vendor"):
        shutil.copytree(os.path.join(md.TEMPLATE, "assets", sub), os.path.join(PROJ, "assets", sub), dirs_exist_ok=True)
    for f in ("NotoSansJP-Bold.ttf", "RoundedMplus1c-ExtraBold.ttf", "README.txt"):
        shutil.copy(os.path.join(md.FONT_DIR, f), os.path.join(PROJ, "assets", "fonts", f))
    shutil.copy(os.path.join(md.TEMPLATE, "hyperframes.json"), PROJ)

    # 声：候補ごとに3つのセリフを作って並べる
    t = 0.0; scenes = []; chunks = []
    INTRO = 2.6
    t = INTRO
    for n, c in enumerate(CANDS):
        s0 = t; t += 0.9  # 名前カードが出てから話し始める
        parts = []
        for k, (sub, read, mul) in enumerate(LINE):
            if k: t += 0.14
            a, meta = synth(read, c["id"], round(c["speed"] * mul, 3), c["pitch"], c["into"], cache)
            parts.append(a)
            chunks.append(dict(sub=sub, s=t, e=t + meta["dur"], audio=a, vis=meta["vis"], cand=n)); t += meta["dur"]
        md.write_wav(os.path.join(vdir, f"{n + 1:02d}_{c['key']}.wav"), np.concatenate([np.concatenate([p, np.zeros(int(0.14 * SR), np.float32)]) for p in parts]))
        t += 0.9
        scenes.append(dict(n=n, start=round(s0, 3), end=round(t, 3)))
    TOTAL = round(t + 0.2, 2)
    N = int(TOTAL * SR) + SR
    voice = np.zeros(N, np.float32); sfx = np.zeros(N, np.float32)
    for c in chunks:
        i = int(c["s"] * SR); voice[i:i + len(c["audio"])] += c["audio"]
    for s in scenes:
        i = int((s["start"] + 0.05) * SR); ch = md.chime(); sfx[i:i + len(ch)] += ch * 0.10
    AUD = os.path.join(PROJ, "assets", "audio")
    md.write_wav(os.path.join(AUD, "voice.wav"), voice[:int(TOTAL * SR)])
    md.write_wav(os.path.join(AUD, "sfx.wav"), sfx[:int(TOTAL * SR)])

    # 場面：タイトル → 候補ごとの名前カード
    md.comp_file(PROJ, "intro", f"""    <div id="in-card" class="clip" data-start="0" data-duration="{INTRO:.3f}" data-track-index="0" style="position:absolute;left:0;top:385px;width:1080px;height:340px;">
      <div id="in-in" class="card center" style="top:0;height:340px;">
        <div class="c" style="font-family:RoundM;font-size:36px;margin-bottom:6px;">タートルの声えらび</div>
        <div class="big" style="font-size:84px;">マスコット声<br/><span class="hl">聞き比べ</span></div>
        <div style="font-size:30px;color:var(--dim);">候補 {len(CANDS)} 人・VOICEVOX</div>
      </div>
    </div>""", f'    tl.fromTo("#in-in", {{opacity:0, scale:0.9}}, {{opacity:1, scale:1, duration:0.4, ease:"back.out(1.8)"}}, 0);\n    tl.to("#in-in", {{opacity:0, duration:0.2}}, {INTRO - 0.25:.3f});')
    for s in scenes:
        c = CANDS[s["n"]]; dur = s["end"] - s["start"]; sid = f"c{s['n']}"
        nsz = md.fit([c["name"]], 104, 60, 820)
        md.comp_file(PROJ, sid, f"""    <div id="{sid}-card" class="clip" data-start="0" data-duration="{dur:.3f}" data-track-index="0" style="position:absolute;left:0;top:385px;width:1080px;height:340px;">
      <div id="{sid}-in" class="card center" style="top:0;height:340px;padding:0 30px;">
        <div style="display:flex;gap:16px;align-items:center;"><div class="num" style="position:static;width:76px;height:76px;line-height:76px;font-size:46px;">{s['n'] + 1}</div>
          <div class="tag" style="font-size:30px;background:#5ee38f;">法人の商用利用：{c['law']}</div></div>
        <div id="{sid}-name" class="big hl" style="font-size:{nsz}px;line-height:1.2;margin-top:8px;">{md.esc(c['name'])}</div>
        <div style="font-size:36px;">{md.esc(c['style'])}</div>
        <div style="font-size:28px;color:var(--dim);margin-top:8px;white-space:normal;line-height:1.4;">{md.esc(c['feat'])}</div>
      </div>
    </div>
    <div id="{sid}-cr" class="clip" data-start="0" data-duration="{dur:.3f}" data-track-index="1" style="position:absolute;left:0;top:1262px;width:1080px;height:60px;">
      <div id="{sid}-crin" style="text-align:center;font-size:34px;color:#fff;">音声：{md.esc(c['credit'])}</div>
    </div>""", f"""    tl.fromTo("#{sid}-in", {{x:900, opacity:0}}, {{x:0, opacity:1, duration:0.45, ease:"expo.out"}}, 0.05);
    tl.fromTo("#{sid}-name", {{scale:0.7}}, {{scale:1, duration:0.4, ease:"back.out(2.2)"}}, 0.3);
    tl.to("#{sid}-in", {{opacity:0, duration:0.2}}, {dur - 0.25:.3f});""")
    # 字幕
    cap_html, cap_js = [], []
    for i, c in enumerate(chunks):
        s_, e_ = round(c["s"] - 0.04, 3), round(c["e"] + 0.12, 3)
        lines = c["sub"].split("/"); fs = md.fit(lines, 54, 40, 790)
        cap_html.append(f'    <div id="cap{i}" class="clip cap" data-start="{s_:.3f}" data-duration="{e_ - s_:.3f}" data-track-index="0"><span class="capbox" id="capb{i}" style="font-size:{fs}px;">{md.mark(c["sub"])}</span></div>')
        cap_js.append(f'    tl.fromTo("#capb{i}", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.18, ease:"back.out(2)"}}, {s_:.3f});')
    md.comp_file(PROJ, "captions", "\n".join(cap_html), "\n".join(cap_js), """    .cap { position:absolute; left:0; right:0; bottom:690px; text-align:center; }
    .capbox { display:inline-block; padding:20px 40px; border-radius:28px; background:rgba(4,7,15,0.82); border:3px solid rgba(60,214,240,0.55);
      color:#fff; line-height:1.42; white-space:nowrap; }""")
    # タートル（口パク）
    segs = []
    for c in chunks:
        for a_, b_, v in c["vis"]:
            st = 2 if v in ("a", "o", "e") else 1 if v in ("i", "u") else 0
            if st: segs.append((c["s"] + a_, c["s"] + b_, st))
    ev = [(0.0, 0)]
    for a_, b_, st in segs:
        a_ = round(a_ * FPS) / FPS; b_ = max(round(b_ * FPS) / FPS, a_ + 1 / FPS)
        if ev[-1][0] > a_: a_ = ev[-1][0]
        if ev[-1][1] != st: ev.append((a_, st))
        ev.append((b_, 0))
    clean = [ev[0]]
    for i in range(1, len(ev)):
        tc, st = ev[i]
        if i + 1 < len(ev) and st == 0 and ev[i + 1][0] - tc < 1.5 / FPS: continue
        if clean[-1][1] != st: clean.append((tc, st))
    mouth = ",".join(f'[{t_:.3f},"#tm{st}0"]' for t_, st in clean)
    imgs = "\n".join(f'        <img id="tm{m}0" src="assets/img/turtle_m{m}_b0.png" class="tface" style="opacity:{1 if m == 0 else 0};" />' for m in (0, 1, 2))
    waves = "\n".join(f'    tl.fromTo("#rig", {{rotation:0}}, {{rotation:7, duration:0.2, yoyo:true, repeat:3, ease:"sine.inOut", transformOrigin:"50% 90%", immediateRender:false}}, {s["start"] + 0.2:.3f});' for s in scenes)
    md.comp_file(PROJ, "turtle", f'    <div id="mover"><div id="rig">\n{imgs}\n    </div></div>', f"""{waves}
    const faces = ["#tm00","#tm10","#tm20"];
    const mouth = [{mouth}];
    for (const [t, id] of mouth) {{ tl.set(faces.filter(f => f !== id), {{opacity:0}}, t); tl.set(id, {{opacity:1}}, t); }}""",
    """    #mover { position:absolute; left:375px; top:745px; width:330px; height:330px; }
    #rig { position:absolute; left:0; top:0; width:330px; height:330px; }
    .tface { position:absolute; left:0; top:0; width:330px; height:330px; image-rendering:pixelated; }""")
    md.comp_file(PROJ, "chrome", """    <div id="band">マスコット声の聞き比べ（候補）</div>""", '    tl.fromTo("#band", {y:-12}, {y:0, duration:0.4}, 0);',
                 "    #band { position:absolute; left:90px; right:90px; top:292px; height:68px; border-radius:34px; background:var(--yellow); color:var(--ink); font-size:36px; line-height:68px; text-align:center; }")
    def host(n, s_, e_, z, kind="graphics"):
        return f'      <div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{s_:.3f}" data-duration="{e_ - s_:.3f}" data-track-index="1" data-track-kind="{kind}" data-width="1080" data-height="1920" style="z-index:{z};"></div>'
    hosts = [host("chrome", 0, TOTAL, 5), host("turtle", 0, TOTAL, 20), host("intro", 0, INTRO, 10)] + \
            [host(f"c{s['n']}", s["start"], s["end"], 10) for s in scenes] + [host("captions", 0, TOTAL, 30, "captions")]
    open(os.path.join(PROJ, "index.html"), "w").write(f"""<!doctype html>
<html lang="ja"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
<script src="assets/vendor/gsap.min.js"></script>
<style>:root {{ {md.COLORS} }} * {{ margin:0; padding:0; box-sizing:border-box; }} html, body {{ width:1080px; height:1920px; overflow:hidden; background:var(--navy); }} #root {{ position:relative; width:100%; height:100%; }} #bg img {{ position:absolute; }}</style>
</head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
  <div id="bg" data-layout-ignore><img id="bgimg" src="assets/img/bg.png" style="left:0;top:0;width:1080px;height:1920px;" /><img id="glow" src="assets/img/glow.png" style="left:90px;top:620px;width:900px;height:900px;" /></div>
{chr(10).join(hosts)}
  <audio id="voice" class="clip" src="assets/audio/voice.wav" data-start="0" data-duration="{TOTAL}" data-track-index="6" data-volume="1"></audio>
  <audio id="sfx" class="clip" src="assets/audio/sfx.wav" data-start="0" data-duration="{TOTAL}" data-track-index="8" data-volume="1"></audio>
</div>
<script>const tl = gsap.timeline({{ paused: true }}); tl.fromTo("#glow", {{x:-60}}, {{x:60, duration:{TOTAL:.2f}, ease:"sine.inOut"}}, 0); window.__timelines["main"] = tl;</script>
</body></html>
""")
    hf = ["node", md.HF_CLI] if os.path.exists(md.HF_CLI) else ["npx", "--yes", "hyperframes@0.9.72"]
    r = subprocess.run(hf + ["check", "--json"], cwd=PROJ, capture_output=True, text=True)
    j = json.loads(r.stdout[r.stdout.index("{"):])
    errs = sum(int(v.get("errorCount", 0)) for v in j.values() if isinstance(v, dict))
    print("check: ok", j.get("ok"), "errors", errs, flush=True)
    if errs and "--force" not in sys.argv: sys.exit("check エラー")
    allmp4 = os.path.join(HERE, "聞き比べ_全部.mp4")
    with open(os.path.join(HERE, "render.log"), "w") as lf:
        subprocess.run(hf + ["render", "--quality", "delivery", "-o", allmp4], cwd=PROJ, stdout=lf, stderr=subprocess.STDOUT, check=True)
    cdir = os.path.join(HERE, "候補"); os.makedirs(cdir, exist_ok=True)
    for s in scenes:
        c = CANDS[s["n"]]; out = os.path.join(cdir, f"{s['n'] + 1:02d}_{c['key']}.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['start']:.3f}", "-to", f"{s['end']:.3f}", "-i", allmp4,
                        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", out], check=True)
    fdir = os.path.join(HERE, "確認コマ"); os.makedirs(fdir, exist_ok=True)
    shots = [1.0] + [s["start"] + 1.6 for s in scenes]
    ims = []
    for k, ts in enumerate(shots):
        p = os.path.join(fdir, f"{k:02d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ts:.2f}", "-i", allmp4, "-frames:v", "1", p]); ims.append(Image.open(p).convert("RGB"))
    tw, th = 270, 480; cols = 4; rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * tw, rows * th), (20, 20, 20))
    for k, im in enumerate(ims): sheet.paste(im.resize((tw, th)), ((k % cols) * tw, (k // cols) * th))
    sheet.save(os.path.join(fdir, "contact_sheet.jpg"), quality=88)
    json.dump({"total": TOTAL, "scenes": [dict(s, name=CANDS[s["n"]]["name"]) for s in scenes]}, open(os.path.join(HERE, "秒数.json"), "w"), ensure_ascii=False, indent=1)
    print("done", TOTAL, allmp4)

if __name__ == "__main__":
    main()
