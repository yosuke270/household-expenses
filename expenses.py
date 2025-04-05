import os
from openai import OpenAI
import datetime
import MySQLdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rc('font', family='Meiryo')  # Windowsの場合

# 定数の定義
ITEM_LABELS = {
    1: "食費",
    2: "住居費",
    3: "水道光熱費",
    4: "消耗品",
    5: "交際費",
    6: "交通費",
    7: "自己投資費",
    8: "その他",
}
WEEKDAYS_JP = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]

def get_database_connection():
    """データベースへの接続を確立する関数"""
    try:
        conn = MySQLdb.connect(
            user="root",
            passwd="Funao270",
            host="localhost",
            db="household_expenses_db",
        )
        return conn
    except MySQLdb.Error as e:
        print(f"データベース接続エラー: {e}")
        return None

def ask_LLM():
    """LLMに問い合わせて家計簿データを取得し、データベースに登録する関数"""
    api_key = os.environ["ChatGPT_API"]
    client = OpenAI(api_key=api_key)

    print("出費を入力してください")
    user_input = input()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.datetime.now().weekday() + 1

    prompt = f"""
    ## 指示
    - あなたは家計簿のデータベースを管理し解析するAIです。
    - INPUTを解析して、結果を**必ず**OUTPUT_TEMPLATEに従って出力してください。
    - 出力は**カンマ区切り**で、以下の形式を厳密に守ってください。
    - 出力形式: item_id, amount, date, memo, week_id
    - 各項目の説明:
        - item_id: 1 食費 2 住居費 3 水道光熱費 4 消耗品 5 交際費 6 交通費 7 自己投資費 8 その他
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

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "system", "content": prompt}]
        )
        output = response.choices[0].message.content.strip().split(",")
        item_id, amount, date, memo, week_id = output
        mysql_connect(item_id, amount, date, memo, week_id)
    except Exception as e:
        print(f"LLMエラー: {e}")

def mysql_connect(item_id, amount, date, memo, week_id):
    """データベースに家計簿データを登録する関数"""
    conn = get_database_connection()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        sql = "INSERT INTO amount (item_id, amount, date, memo, week_id) VALUES (%s, %s, %s, %s, %s)"
        cur.execute(sql, (item_id, amount, date, memo, week_id))
        conn.commit()

        cur.execute("SELECT * FROM amount")
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except MySQLdb.Error as e:
        print(f"データベースエラー: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def fetch_data():
    """データベースから家計簿データを取得する関数"""
    conn = get_database_connection()
    if conn is None:
        return None

    try:
        cur = conn.cursor()
        sql = "SELECT item_id, SUM(amount) AS total_amount FROM amount GROUP BY item_id"
        cur.execute(sql)
        rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=["item_id", "total_amount"])
        return df
    except MySQLdb.Error as e:
        print(f"データベースエラー: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def plot_graph(df):
    """家計簿データをグラフで表示する関数"""
    if df is None:
        return

    df["item_name"] = df["item_id"].map(ITEM_LABELS)

    plt.figure(figsize=(10, 6))
    plt.bar(df["item_name"], df["total_amount"], color="skyblue")
    plt.title("カテゴリ別支出合計", fontsize=16)
    plt.xlabel("カテゴリ", fontsize=12)
    plt.ylabel("支出額 (円)", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    ask_LLM()
    data = fetch_data()
    plot_graph(data)