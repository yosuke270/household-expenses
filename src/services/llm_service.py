import os
import datetime
from openai import OpenAI
from services.database import mysql_connect
from utils.logger import logger

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