###使用方法
1.ngrokを起動
~~~
ngrok http 5000
~~~

2.Forwarding に記載されているURLをLINE DevelopersのWebhookに登録する
写真

3.app.pyのngrok_urlをForwarding に記載されているURLに変更する


4.アプリケーションを実行する
~~~
python app.py
~~~


＝＝＝＝＝＝＝＝＝
勉強メモ
＝＝＝＝＝＝＝＝＝

①Flaskを実行すると引数で指定されたportやモードでwebサーバを起動する
②実行された後は、リクエストの待機を行う

①Lineのプラットフォームから、app.pyにリクエストが飛んでくる
②Flaskのデコレータがつけれたcallback関数が受け取る
③callback関数内のhandler.handle(body, signature)で内容を受け取り、@handler.add(MessageEvent, message=TextMessageContent)が実行される

＝＝＝＝＝＝＝＝＝
雑多な知識
＝＝＝＝＝＝＝＝＝
lambda関数
引数として使いたいような単純な関数はlambda関数として実行する

folder構成参考
https://tarovlog.com/2024/10/21/react-summary-folder-structure/

＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

python仮想環境

PS C:\Users\funak\funao\家計簿\household-expenses> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
PS C:\Users\funak\funao\家計簿\household-expenses> .\expenses\Scripts\activate     
(expenses) PS C:\Users\funak\funao\家計簿\household-expenses> 


(expenses) PS C:\Users\funak\funao\家計簿\household-expenses> deactivate 
＝＝＝＝＝＝＝＝＝＝＝＝
学び
オンプレ環境で作ったものを、クラウドネイティブなものに変更するには手間とコストがかかる
クラウドでやることが決まっているなら最初からクラウドを使う設計をしたほうがいい

ただ、クラウドの設計ができる様になるためには自分でサービスを作ったことがないと難しい
