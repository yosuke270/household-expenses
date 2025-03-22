#家計簿をつけるアプリ
#自然言語で入力されたデータを分析して家計簿をつける。「すき家に３００円」と入力すれば、LLMが食費と推定してデータベースに登録する
import os
from openai import OpenAI
import datetime
import MySQLdb


def ask_LLM():
    api_key = os.environ["ChatGPT_API"]
    client = OpenAI(api_key=api_key)

    print("出費を入力してください")
    user_input = input()
    day_info = datetime.datetime.now()
    today = day_info.strftime("%Y-%m-%d")
    weekday = day_info.weekday()
    weekday += 1
     # 曜日を日本語で取得
    weekdays_jp = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    weekday_jp = weekdays_jp[weekday]
    print(today)
    print(weekday + 1)

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
            {"role": "system","content": prompt},
        ]
    )

    print("Output:", response.choices[0].message.content)

    # response.choices[0].message.contentをパースして、mysql_connect関数に渡す
    output = response.choices[0].message.content.strip().split(',')
    item_id, amount, date, memo, week_id = output[0], output[1], output[2], output[3], output[4]

    mysql_connect(item_id, amount, date, memo, week_id)

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

if __name__ == "__main__":
    ask_LLM()
