import json,urllib.request,urllib.parse
L=[("タートルアドのタートルです。","タートルアドのタートルです。"),
("今週のAIニュースを、3つ紹介します。","今週のAIニュースを、3つ紹介します。"),
("ひとつめ。アンソロピックが、新しいAI「クロード・フェイブル5.2」を出しました。","ひとつめ。Anthropicが、新しいAI「Claude Fable 5.2」を出しました。"),
("前の型より、答えが出るのが最大3割ほど速くなったそうです。","前の型より、答えが出るのが最大3割ほど速くなったそうです。"),
("ふだんの仕事は、今のAIで十分。むずかしい作業のときに試すのがおすすめです。","ふだんの仕事は、今のAIで十分。むずかしい作業のときに試すのがおすすめです。"),
("ふたつめ。チャットジーピーティーで、会社やお店の情報を、自分で管理できる仕組みが始まりました。","ふたつめ。ChatGPTで、会社やお店の情報を、自分で管理できる仕組みが始まりました。"),
("まだ試験中の機能です。","まだ試験中の機能です。"),
("グーグルマップと同じように、AIの中で、自分の会社がどう紹介されているか、確かめる時代です。","Googleマップと同じように、AIの中で、自分の会社がどう紹介されているか、確かめる時代です。"),
("みっつめ。グーグルのジェミニの「タスク」機能が、日本でも無料になりました。","みっつめ。GoogleのGeminiの「タスク」機能が、日本でも無料になりました。"),
("アメリカでは、AIがお店に電話して、値段を聞くこともできます。","アメリカでは、AIがお店に電話して、値段を聞くこともできます。"),
("AIがお客さんの代わりに調べる時代。営業時間や料金は、いつも最新にしておきましょう。","AIがお客さんの代わりに調べる時代。営業時間や料金は、いつも最新にしておきましょう。"),
("タートルアドでは、AIの使い方のご相談を受け付けています。また来週。","タートルアドでは、AIの使い方のご相談を受け付けています。また来週。")]
op=urllib.request.build_opener(urllib.request.ProxyHandler({})); meta=[]
for i,(say,txt) in enumerate(L):
    q=json.loads(op.open(urllib.request.Request("http://localhost:50021/audio_query?speaker=52&text="+urllib.parse.quote(say),method="POST")).read())
    q["outputSamplingRate"]=48000; q["speedScale"]=1.2
    w=op.open(urllib.request.Request("http://localhost:50021/synthesis?speaker=52",data=json.dumps(q).encode(),headers={"Content-Type":"application/json"},method="POST")).read()
    fn=f"l{i:02d}.wav"; open(fn,"wb").write(w); meta.append({"text":txt,"file":fn})
json.dump(meta,open("narr.json","w"),ensure_ascii=False)
