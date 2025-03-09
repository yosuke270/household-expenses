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
    input = input()
    today = datetime.datetime.now()
    print(today)

    prompt = f"""\
    ## 指示
    - あなたは家計簿のデータベースを管理し解析するAIです。
    - INPUTを解析して、結果をOUTPUT_TEMPLATEに従って出力してください。
    - 出力はOUTPUT_exampleを参考にしてください。
    ## 注意事項
    - 出力は必ずOUTPUT_exampleに従ってください。
    - INPUTには、話し言葉で入力されたデータです。うまく解析してください。
    - カテゴリは、食費、交通費、日用品、居住費、医療費から選ばれます。
    - 日付は、{today}をOUTPUT_exampleに従って出力してください。
    - inputが不明な場合は、「エラー：入力が不明」と出力してください。
    - 内容は、入力された内容から抽出してください。
    - inputに複数のデータが入力された場合はOUTPUT_exampleを参考に複数の出力をしてください。

    ## INPUT
    {input}

    ## OUTPUT_example
    内容　　：ラーメン
    カテゴリ：食費
    金額　　：600円
    日付　　：○○○○年○○月○○日
    =====
    内容　　：洋服
    カテゴリ：日用品
    金額　　：1111円
    日付　　：○○○○年○○月○○日
    """



    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system","content": prompt},
    ]
    )

    print(response.choices[0].message.content)

def mysql_connect(item_id, amount, date, memo, week_id):

    print("データベースに接続します")
    #データベースに接続する
    conn = MySQLdb.connect(
        user="root",
        passwd="Funao270",
        host="localhost",
        db="household_expenses_db")
    
    print("カーソルを取得します")
    #カーソルを取得する
    cur = conn.cursor()

    print("SQL文を実行します")
    #SQL文を実行する
    sql = "INSERT INTO amount (item_id, amount, date, memo, week_id) VALUES (%s, %s, %s, %s, %s)"
    # item_id  1 食費  2 住居費  3 水道光熱費  4 消耗品  5 交際費 6 交通費  7 自己投資費  8 その他
    # week_id  1 Monday 2 Tuesday 3 Wednesday 4 Thursday 5 Friday 6 Saturday 7 Sunday
    cur.execute(sql, (item_id, amount, date, memo, week_id))
    # コミットして変更を確定する
    conn.commit()
    print("データベースに登録しました")

    # データを取得するためのSQL文を実行する
    cur.execute("SELECT * FROM amount")
    rows = cur.fetchall()
    for row in rows:
        print("取得したデータを表示します")
        print(row)

    print("データベースを切断します")
     #切断する
    cur.close()
    conn.close()

if __name__ == "__main__":
    #ask_LLM()
    print("item_id, amount, date, memo, week_idを入力してください")
    item_id = input()
    amount = input()
    date = input()
    memo = input()
    week_id = input()
    mysql_connect(item_id, amount, date, memo, week_id)