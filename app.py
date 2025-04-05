from flask import Flask, request, abort, send_from_directory
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import os
import datetime
import MySQLdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from openai import OpenAI
import logging  # logging モジュールをインポート
from urllib.parse import quote
from PIL import Image  # Pillowライブラリをインポート

# 日本語フォントを設定
matplotlib.rc('font', family='Meiryo')
matplotlib.use('Agg')
app = Flask(__name__)

# ロガーを設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LINE APIの設定
configuration = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

ngrok_url = "https://5fe9-240b-10-bf66-df00-4deb-56ac-1ef8-1461.ngrok-free.app/"

# デフォルトのルートを追加
@app.route("/", methods=["GET"])
def index():
    return "This is the default route. Use /callback for LINE Webhook.", 200

# LINEからのWebhookを受け取るエンドポイント
@app.route("/callback", methods=['POST'])
def callback():
    logger.info("A")
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    logger.info("Request body: " + body)  # デバッグ用
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# メッセージイベントの処理
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    userinput = event.message.text  # ユーザーからの入力を取得
    LLManswer = ask_LLM(userinput)  # LLMに問い合わせ
    data = fetch_data()
    # グラフを作成
    plot_graph(data)

    # グラフを一時ファイルに保存
    local_graph_path = os.path.abspath("output_graph.png")
    try:
        plt.savefig(local_graph_path)
        logger.info("グラフを保存しました。")

    except Exception as e:
        logger.error(f"グラフの保存中にエラーが発生しました: {e}")
        return  # エラーが発生した場合はここで処理を終了する

    if not os.path.exists(local_graph_path):
        logger.error(f"グラフファイルが見つかりません: {local_graph_path}")
        return
    logger.info("###################")
    logger.info("送信側")
    # グラフ画像をLINEで送信
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        # パーセントエンコードを適用
        encoded_graph_path = quote(os.path.join(ngrok_url, "output_graph.png"), safe=":/")
        try:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=encoded_graph_path)]
                    
                )
            )
        except Exception as e:
            logger.error(f"LINEメッセージの送信中にエラーが発生しました: {e}")
def ask_LLM(user_input):
    logger.info(user_input)
    api_key = os.environ["ChatGPT_API"]
    client = OpenAI(api_key=api_key)

    day_info = datetime.datetime.now()
    today = day_info.strftime("%Y-%m-%d")
    weekday = day_info.weekday() + 1

    prompt = f"""\\ 
    ## 指示
    - あなたは家計簿のデータベースを管理し解析するAIです。
    - INPUTを解析して、結果を**必ず**OUTPUT_TEMPLATEに従って出力してください。
    - 出力は**カンマ区切り**で、以下の形式を厳密に守ってください。
    - 出力形式: item_id, amount, date, memo, week_id
    - 各項目の説明:
      - item_id: 1 食費  2 住居費  3 水道光熱費  4 消耗品  5 交際費 6 交通費  7 自己投資費  8 その他
      - amount: 入力された金額
      - date: {today}（この日付を使用してください）
      - memo: 入力された内容
      - week_id: {weekday}（このidを使用してください）
    ## INPUT
    {user_input}

    ## OUTPUT_TEMPLATE
    item_id, amount, date, memo, week_id

    ## 注意事項
    - 出力は**1行のみ**で、カンマ区切り形式で出力してください。
    - 余計な説明や追加の情報を含めないでください。
    - 例: 6, 9000, 2025-03-22, 新幹線のチケット代, 6
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
        ]
    )

    output = response.choices[0].message.content.strip().split(',')
    item_id, amount, date, memo, week_id = output[0], output[1], output[2], output[3], output[4]
    mysql_connect(item_id, amount, date, memo, week_id)

    return output

def mysql_connect(item_id, amount, date, memo, week_id):

    #データベースに接続する
    conn = MySQLdb.connect(
        user="root",
        passwd="Funao270",
        host="localhost",
        db="household_expenses_db")
    
    #カーソルを取得する
    cur = conn.cursor()

    #SQL文を実行する
    sql = "INSERT INTO amount (item_id, amount, date, memo, week_id) VALUES (%s, %s, %s, %s, %s)"
    # item_id  1 食費  2 住居費  3 水道光熱費  4 消耗品  5 交際費 6 交通費  7 自己投資費  8 その他
    # week_id  1 Monday 2 Tuesday 3 Wednesday 4 Thursday 5 Friday 6 Saturday 7 Sunday
    cur.execute(sql, (item_id, amount, date, memo, week_id))
    # コミットして変更を確定する
    conn.commit()

    # データを取得するためのSQL文を実行する
    cur.execute("SELECT * FROM amount")
    rows = cur.fetchall()
    for row in rows:
        print(row)

     #切断する
    cur.close()
    conn.close()

def fetch_data():
    # データベースに接続
    conn = MySQLdb.connect(
        user="root",
        passwd="Funao270",
        host="localhost",
        db="household_expenses_db"
    )
    cur = conn.cursor()

    # データを取得
    sql = "SELECT item_id, SUM(amount) AS total_amount FROM amount GROUP BY item_id"
    cur.execute(sql)
    rows = cur.fetchall()

    # データをDataFrameに変換
    df = pd.DataFrame(rows, columns=["item_id", "total_amount"])

    # データベース接続を閉じる
    cur.close()
    conn.close()

    return df

def plot_graph(df):
    # 項目名を設定
    item_labels = {
        1: "食費",
        2: "住居費",
        3: "水道光熱費",
        4: "消耗品",
        5: "交際費",
        6: "交通費",
        7: "自己投資費",
        8: "その他"
    }

    # item_idを日本語ラベルに変換
    df["item_name"] = df["item_id"].map(item_labels)

    # グラフを作成
    plt.figure(figsize=(10, 6))
    plt.bar(df["item_name"], df["total_amount"], color="skyblue")
    plt.title("カテゴリ別支出合計", fontsize=16)
    plt.xlabel("カテゴリ", fontsize=12)
    plt.ylabel("支出額 (円)", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # グラフを表示
    plt.show()

@app.route("/<filename>")
def serve_image(filename):
    return send_from_directory(".", filename)

if __name__ == "__main__":
    logger.info("Starting server...")  # サーバー起動時のログ
    app.run(port=5000, debug=True)  # Flaskアプリケーションを起動
    logger.info("Server finished.")  # サーバー起動後のログ