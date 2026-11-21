# -*- coding: utf-8 -*-
"""AI社員（仲間5体）の声の聞き比べ動画を作る（HyperFrames）。

使い方: python3 資料/ai_video/声の聞き比べ/AI社員/make_staff_compare.py
前提: VOICEVOX ENGINE が 127.0.0.1:50021 で動いていること（daily/毎日の手順.md の 1-2・1-3）。
声の割り当て・調整値は make_daily.py の STAFF（説明は 資料/ai_video/AI社員の声.md）。ここを直すと毎日の動画も同じ声になる。
出力（このフォルダ）:
  聞き比べ_AI社員_全部.mp4 … 5体をつないだ1本
  各キャラ/NN_<key>.mp4  … 1体ずつの短い動画（名札・クレジット入り）
  声/NN_<key>.wav        … 声だけ
  確認コマ/contact_sheet.jpg ／ 秒数.json
公開・投稿はしない（作るだけ）。
"""
import json, os, shutil, subprocess, sys, math, hashlib
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DAILY = os.path.abspath(os.path.join(HERE, "..", "..", "daily"))
sys.path.insert(0, DAILY)
import make_daily as md  # noqa: E402

SR, FPS = md.SR, md.FPS
ORDER = ["design", "sales", "listing", "automation", "research"]

def synth(text, spk, speed, vc, cache):
    a, meta = md.synth(text, spk, speed, cache, vc["intonation"], vc["pitch"])
    return a, meta

def mouth_events(chunks):
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
    return clean

def main():
    os.environ.update(md.TELEMETRY_OFF)
    PROJ = os.path.join(HERE, "project"); cache = os.path.join(HERE, "cache"); vdir = os.path.join(HERE, "声")
    if os.path.isdir(os.path.join(PROJ, "compositions")): shutil.rmtree(os.path.join(PROJ, "compositions"))
    for d_ in (cache, vdir, os.path.join(PROJ, "compositions"), os.path.join(PROJ, "assets", "audio"), os.path.join(PROJ, "assets", "fonts")):
        os.makedirs(d_, exist_ok=True)
    for sub in ("img", "vendor"):
        shutil.copytree(os.path.join(md.TEMPLATE, "assets", sub), os.path.join(PROJ, "assets", sub), dirs_exist_ok=True)
    for f in ("NotoSansJP-Bold.ttf", "RoundedMplus1c-ExtraBold.ttf", "README.txt"):
        shutil.copy(os.path.join(md.FONT_DIR, f), os.path.join(PROJ, "assets", "fonts", f))
    shutil.copy(os.path.join(md.TEMPLATE, "hyperframes.json"), PROJ)
    if not os.path.exists(os.path.join(PROJ, "meta.json")):
        json.dump({"id": "staff-voice-compare", "name": "staff-voice-compare"}, open(os.path.join(PROJ, "meta.json"), "w"))
    IMG = os.path.join(PROJ, "assets", "img")

    INTRO = 2.6
    t = INTRO; scenes = []; chunks = []
    for n, key in enumerate(ORDER):
        st = md.STAFF[key]; vc = dict(md.DEFAULT_VOICE, **st["voice"])
        spk = md.speaker_id(vc["name"], vc["style"])
        md.staff_faces(os.path.join(md.ROOT, st["img"]), IMG, f"staff_{key}")
        lines = [(md.wrap_sub(f"こんにちは、タートルアドの{st['name']}です。"), f"こんにちは、タートルアドの、{st['read']}です。", st.get("name_speed", st["speed"])),
                 (md.wrap_sub(f"わたしは、{st['job']}"), f"わたしは、{st['job_read']}", st["speed"])]
        s0 = t; t += 0.9; parts = []
        for k, (sub, read, sp) in enumerate(lines):
            if k: t += 0.16
            a, meta = synth(read, spk, float(sp), vc, cache)
            parts.append(a)
            chunks.append(dict(sub=sub, s=round(t, 3), e=round(t + meta["dur"], 3), audio=a, vis=meta["vis"], n=n, kana=meta["kana"], speed=sp))
            t += meta["dur"]
        md.write_wav(os.path.join(vdir, f"{n + 1:02d}_{key}.wav"), np.concatenate([np.concatenate([p, np.zeros(int(0.16 * SR), np.float32)]) for p in parts]))
        t += 0.9
        scenes.append(dict(n=n, key=key, start=round(s0, 3), end=round(t, 3), credit=f"VOICEVOX:{vc['name']}", style=vc["style"]))
    TOTAL = round(t + 0.2, 2)
    N = int(TOTAL * SR) + SR
    voice = np.zeros(N, np.float32); sfx = np.zeros(N, np.float32)
    for c in chunks:
        i = int(c["s"] * SR); voice[i:i + len(c["audio"])] += c["audio"]
    for s in scenes:
        i = int((s["start"] + 0.05) * SR); ch = md.chime(); sfx[i:i + len(ch)] += ch * 0.10
        i = int((s["start"] + 0.35) * SR); pp = md.tone(880, 0.18, 30, 0.2); sfx[i:i + len(pp)] += pp * 0.12
    AUD = os.path.join(PROJ, "assets", "audio")
    md.write_wav(os.path.join(AUD, "voice.wav"), voice[:int(TOTAL * SR)])
    md.write_wav(os.path.join(AUD, "sfx.wav"), sfx[:int(TOTAL * SR)])

    # タイトル
    md.comp_file(PROJ, "intro", f"""    <div id="in-card" class="clip" data-start="0" data-duration="{INTRO:.3f}" data-track-index="0" style="position:absolute;left:0;top:385px;width:1080px;height:340px;">
      <div id="in-in" class="card center" style="top:0;height:340px;">
        <div class="c" style="font-family:RoundM;font-size:36px;margin-bottom:6px;">AI動画編集部</div>
        <div class="big" style="font-size:84px;">AI社員の声<br/><span class="hl">聞き比べ</span></div>
        <div style="font-size:30px;color:var(--dim);">仲間 {len(ORDER)} 人・VOICEVOX</div>
      </div>
    </div>""", f'    tl.fromTo("#in-in", {{opacity:0, scale:0.9}}, {{opacity:1, scale:1, duration:0.4, ease:"back.out(1.8)"}}, 0);\n    tl.to("#in-in", {{opacity:0, duration:0.2}}, {INTRO - 0.25:.3f});')

    # キャラごとの場面：上の札（名前・声・規約）＋まん中のキャラ（口パク）＋名札＋クレジット
    for s in scenes:
        st = md.STAFF[s["key"]]; dur = round(s["end"] - s["start"], 3); sid = f"c{s['n']}"
        my = [c for c in chunks if c["n"] == s["n"]]
        for c in my: c["ls"], c["le"] = c["s"] - s["start"], c["e"] - s["start"]
        clean = mouth_events([dict(c, s=c["ls"]) for c in my])
        blinks = [round(x, 2) for x in np.arange(1.6, dur - 0.4, 2.7)]
        ev = sorted([(t_, "m", v) for t_, v in clean] + [(b, "b", 1) for b in blinks] + [(round(b + 0.13, 3), "b", 0) for b in blinks])
        cm = cb = 0; js_m = []
        for t_, kind, v in ev:
            if kind == "m": cm = v
            else: cb = v
            js_m.append(f'[{t_:.3f},"#{sid}-f{cm}{cb}"]')
        faces = [f"#{sid}-f{m}{b}" for m in (0, 1, 2) for b in (0, 1)]
        imgs = "\n".join(f'          <img id="{sid}-f{m}{b}" src="assets/img/staff_{s["key"]}_m{m}_b{b}.png" class="face" style="opacity:{1 if (m, b) == (0, 0) else 0};" />' for m in (0, 1, 2) for b in (0, 1))
        nsz = md.fit([st["name"]], 96, 56, 820, "R")
        tsz = md.fit([st["name"]], 44, 26, 250, "R")
        md.comp_file(PROJ, sid, f"""    <div id="{sid}-card" class="clip" data-start="0" data-duration="{dur:.3f}" data-track-index="0" style="position:absolute;left:0;top:385px;width:1080px;height:330px;">
      <div id="{sid}-in" class="card center" style="top:0;height:330px;padding:0 30px;">
        <div style="display:flex;gap:16px;align-items:center;"><div class="num" style="position:static;width:72px;height:72px;line-height:72px;font-size:44px;">{s['n'] + 1}</div>
          <div class="tag" style="font-size:28px;background:#5ee38f;">法人の商用利用：可（クレジット表記）</div></div>
        <div id="{sid}-name" style="font-family:RoundM;font-size:{nsz}px;line-height:1.2;margin-top:8px;color:{st['color']};white-space:nowrap;">{md.esc(st['name'])}</div>
        <div style="font-size:36px;">声：{md.esc(st['voice']['name'])}（{md.esc(s['style'])}）</div>
      </div>
    </div>
    <div id="{sid}-chr" class="clip" data-start="0" data-duration="{dur:.3f}" data-track-index="1" style="position:absolute;left:0;top:0;width:1080px;height:1920px;">
      <div id="{sid}-mv" style="position:absolute;left:345px;top:735px;width:390px;height:390px;"><div id="{sid}-rig" style="position:absolute;inset:0;">
{imgs}
      </div></div>
      <div id="{sid}-tag" style="position:absolute;left:745px;top:860px;width:260px;">
        <div style="display:inline-block;font-family:RoundM;font-size:{tsz}px;color:#08101f;background:{st['color']};border:3px solid #08101f;border-radius:22px;padding:6px 18px;line-height:1.3;white-space:nowrap;">{md.esc(st['name'])}</div>
      </div>
    </div>
    <div id="{sid}-cr" class="clip" data-start="0" data-duration="{dur:.3f}" data-track-index="2" style="position:absolute;left:0;top:1262px;width:1080px;height:60px;">
      <div id="{sid}-crin" style="text-align:center;font-size:34px;color:#fff;">音声：{md.esc(s['credit'])}</div>
    </div>""", f"""    tl.fromTo("#{sid}-in", {{x:900, opacity:0}}, {{x:0, opacity:1, duration:0.45, ease:"expo.out"}}, 0.05);
    tl.fromTo("#{sid}-name", {{scale:0.7}}, {{scale:1, duration:0.4, ease:"back.out(2.2)"}}, 0.3);
    tl.fromTo("#{sid}-mv", {{opacity:0, y:120, scale:0.4}}, {{opacity:1, y:0, scale:1, duration:0.5, ease:"back.out(2)", transformOrigin:"50% 100%"}}, 0.3);
    tl.fromTo("#{sid}-tag", {{opacity:0, x:60}}, {{opacity:1, x:0, duration:0.35, ease:"power3.out"}}, 0.6);
    tl.fromTo("#{sid}-rig", {{rotation:0, y:0}}, {{rotation:-7, y:-14, duration:0.22, ease:"sine.inOut", yoyo:true, repeat:3, transformOrigin:"50% 90%"}}, 0.75);
    tl.to("#{sid}-in, #{sid}-mv, #{sid}-tag", {{opacity:0, duration:0.2}}, {dur - 0.25:.3f});
    const {sid}faces = {json.dumps(faces)};
    const {sid}mouth = [{",".join(js_m)}];
    for (const [t, id] of {sid}mouth) {{ tl.set({sid}faces.filter(f => f !== id), {{opacity:0}}, t); tl.set(id, {{opacity:1}}, t); }}""",
                     "    .face { position:absolute; left:0; top:0; width:390px; height:390px; image-rendering:pixelated; }")

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
    md.comp_file(PROJ, "chrome", """    <div id="band">AI社員の声の聞き比べ（確認用）</div>""", '    tl.fromTo("#band", {y:-12}, {y:0, duration:0.4}, 0);',
                 "    #band { position:absolute; left:90px; right:90px; top:292px; height:68px; border-radius:34px; background:var(--yellow); color:var(--ink); font-size:36px; line-height:68px; text-align:center; }")
    def host(n, s_, e_, z, kind="graphics"):
        return f'      <div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" data-start="{s_:.3f}" data-duration="{e_ - s_:.3f}" data-track-index="1" data-track-kind="{kind}" data-width="1080" data-height="1920" style="z-index:{z};"></div>'
    hosts = [host("chrome", 0, TOTAL, 5), host("intro", 0, INTRO, 10)] + \
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
    hf = md.hf_cmd(); env = dict(os.environ, **md.TELEMETRY_OFF)
    r = subprocess.run(hf + ["check", "--json"], cwd=PROJ, capture_output=True, text=True, env=env)
    j = json.loads(r.stdout[r.stdout.index("{"):])
    json.dump(j, open(os.path.join(HERE, "check.json"), "w"), ensure_ascii=False, indent=1)
    errs = sum(int(v.get("errorCount", 0)) for v in j.values() if isinstance(v, dict))
    print("check: ok", j.get("ok"), "errors", errs, flush=True)
    if errs and "--force" not in sys.argv: sys.exit("check エラー（check.json を見る）")
    if "--no-render" in sys.argv: return
    allmp4 = os.path.join(HERE, "聞き比べ_AI社員_全部.mp4")
    with open(os.path.join(HERE, "render.log"), "w") as lf:
        subprocess.run(hf + ["render", "--quality", "delivery", "-o", allmp4], cwd=PROJ, stdout=lf, stderr=subprocess.STDOUT, check=True, env=env)
    cdir = os.path.join(HERE, "各キャラ"); os.makedirs(cdir, exist_ok=True)
    for s in scenes:
        out = os.path.join(cdir, f"{s['n'] + 1:02d}_{s['key']}.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['start']:.3f}", "-to", f"{s['end']:.3f}", "-i", allmp4,
                        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
    fdir = os.path.join(HERE, "確認コマ"); os.makedirs(fdir, exist_ok=True)
    shots = [1.0] + [s["start"] + 2.2 for s in scenes]
    ims = []
    for k, ts in enumerate(shots):
        p = os.path.join(fdir, f"{k:02d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ts:.2f}", "-i", allmp4, "-frames:v", "1", p]); ims.append(Image.open(p).convert("RGB"))
    tw, th = 270, 480; cols = 3; rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * tw, rows * th), (20, 20, 20))
    for k, im in enumerate(ims): sheet.paste(im.resize((tw, th)), ((k % cols) * tw, (k // cols) * th))
    sheet.save(os.path.join(fdir, "contact_sheet.jpg"), quality=88)
    json.dump({"total": TOTAL, "scenes": [dict(s, name=md.STAFF[s["key"]]["name"]) for s in scenes],
               "lines": [dict(sub=c["sub"], s=c["s"], e=c["e"], kana=c["kana"], speed=c["speed"]) for c in chunks]},
              open(os.path.join(HERE, "秒数.json"), "w"), ensure_ascii=False, indent=1)
    print("done", TOTAL, allmp4)

if __name__ == "__main__":
    main()
