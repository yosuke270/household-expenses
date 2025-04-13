from flask import Flask, request, send_from_directory
from routes import callback,handle_message
from utils.logger import logger

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# appにurl_ruleを追加。設定したurlにアクセスしたときに呼び出される関数を指定。
app.add_url_rule("/callback", methods=["POST"], view_func=callback)
app.add_url_rule("/<filename>", view_func=lambda filename: send_from_directory(".", filename))


if __name__ == "__main__":
    logger.info("Starting server...")  # サーバー起動時のログ
    app.run(port=5000, debug=True)  # Flaskアプリケーションを起動
    logger.info("Server finished.")  # サーバー起動後のログ