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

def callback():
    logger.info("A")
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    userinput = event.message.text
    LLManswer = ask_LLM(userinput)
    data = fetch_data()
    plot_graph(data)
    local_graph_path = os.path.abspath("output_graph.png")
    try:
        plt.savefig(local_graph_path)
        logger.info("グラフを保存しました。")
    except Exception as e:
        logger.error(f"グラフの保存中にエラーが発生しました: {e}")
        return
    if not os.path.exists(local_graph_path):
        logger.error(f"グラフファイルが見つかりません: {local_graph_path}")
        return
    logger.info("###################")
    logger.info("送信側")
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
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