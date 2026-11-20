import json,urllib.request,urllib.parse
T="タートルアドのタートルです。今週のAIニュースを、3つ紹介します。AIは、毎週のように新しくなっています。また来週。"
V=[(47,"1"),(52,"2"),(42,"3"),(14,"4")]
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
for sid,n in V:
    q=op.open(urllib.request.Request(f"http://localhost:50021/audio_query?speaker={sid}&text="+urllib.parse.quote(T),method="POST")).read()
    qq=json.loads(q); qq["speedScale"]=1.0; qq["outputSamplingRate"]=48000
    w=op.open(urllib.request.Request(f"http://localhost:50021/synthesis?speaker={sid}",data=json.dumps(qq).encode(),headers={"Content-Type":"application/json"},method="POST")).read()
    open(f"v{n}.wav","wb").write(w)
