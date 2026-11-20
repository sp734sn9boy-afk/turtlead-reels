import json,urllib.request,urllib.parse
T="タートルアドのタートルです。今週のAIニュースを、3つ紹介します。AIは、毎週のように新しくなっています。また来週。"
V=[("A",52,dict(pitchScale=0.03,intonationScale=1.35,speedScale=1.05)),
   ("B",52,dict(pitchScale=-0.03,intonationScale=1.1,speedScale=0.9)),
   ("C",21,{}),("D",11,{}),("E",12,{}),("F",53,{})]
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
for n,sid,adj in V:
    q=json.loads(op.open(urllib.request.Request(f"http://localhost:50021/audio_query?speaker={sid}&text="+urllib.parse.quote(T),method="POST")).read())
    q.update(adj); q["outputSamplingRate"]=48000
    open(f"w{n}.wav","wb").write(op.open(urllib.request.Request(f"http://localhost:50021/synthesis?speaker={sid}",data=json.dumps(q).encode(),headers={"Content-Type":"application/json"},method="POST")).read())
