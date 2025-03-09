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
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    print(today)

    prompt = f"""\ 
    ## 指示
    - あなたは家計簿のデータベースを管理し解析するAIです。
    - INPUTを解析して、結果をOUTPUT_TEMPLATEに従って出力してください。
    - INPUTは、話し言葉で入力されたデータです。うまく解析して出力してください。
    - item_idの項目は、1 食費  2 住居費  3 水道光熱費  4 消耗品  5 交際費 6 交通費  7 自己投資費  8 その他 です。必ずこの中から選択してください。
    - amountの項目は、入力された金額です。
    - dateの項目は、{today}です。
    - memoの項目は、入力された内容です。
    - week_idの項目は、1 Monday 2 Tuesday 3 Wednesday 4 Thursday 5 Friday 6 Saturday 7 Sunday です。
    ## 注意事項
    - 結果は必ずINPUTのみから導き出し、INPUT_exampleとOUTPUT_exampleは参考としてのみ使用してください。

    ## INPUT
    {user_input}

    ## OUTPUT_TEMPLATE
    item_id, amount, date, memo, week_id

    ## INPUT_example1
    牛丼に300円
    ## OUTPUT_example1
    1,300,{today},牛丼,1

    ## INPUT_example2
    会社のの飲み会5000円
    ## OUTPUT_example2
    5,5000,{today},会社のの飲み会,1

    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system","content": prompt},
        ]
    )

    print(response.choices[0].message.content)

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
