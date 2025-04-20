from flask import request, abort, send_from_directory
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
from urllib.parse import quote
from services.llm_service import ask_LLM
from services.database import fetch_data
from services.graph_service import plot_graph
from utils.logger import logger
import matplotlib.pyplot as plt

configuration = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
ngrok_url = "https://549d-240b-10-bf66-df00-a079-30ee-1cd3-8f49.ngrok-free.app/"
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder_path = "images"
filename = "graph.png"
#ライン公式に基づきcallcack関数を定義。Lineのプラットフォームから送信されるリクエストヘッダに含まれる署名を取得
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    logger.info("Request body: " + body)
    try:
        #署名を検証し、正当なリクエストかどうかを確認
        #署名が正当な場合、handleメソッドを呼び出す。
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    userinput = event.message.text
    ask_LLM(userinput)
    data = fetch_data()
    plot_graph(data)
    local_graph_path = os.path.join(project_root, folder_path, filename)
    try:
        plt.savefig(local_graph_path)
        logger.info("グラフを保存しました。")
    except Exception as e:
        logger.error(f"グラフの保存中にエラーが発生しました: {e}")
        return
   
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        encoded_graph_path = os.path.join(ngrok_url, filename)
        try:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token, #どのユーザのトークに返信するか識別
                    messages=[TextMessage(text=encoded_graph_path)]
                )
            )
        except Exception as e:
            logger.error(f"LINEメッセージの送信中にエラーが発生しました: {e}")