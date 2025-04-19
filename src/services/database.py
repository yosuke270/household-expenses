import MySQLdb
import pandas as pd
from utils.logger import logger

def mysql_connect(item_id, amount, date, memo, week_id):
    conn = MySQLdb.connect(
        user="root",
        passwd="Funao270",
        host="localhost",
        db="household_expenses_db"
    )
    cur = conn.cursor()
    sql = "INSERT INTO amount (item_id, amount, date, memo, week_id) VALUES (%s, %s, %s, %s, %s)"
    cur.execute(sql, (item_id, amount, date, memo, week_id))
    conn.commit()
    cur.execute("SELECT * FROM amount")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()

def fetch_data():
    conn = MySQLdb.connect(
        user="root",
        passwd="Funao270",
        host="localhost",
        db="household_expenses_db"
    )
    cur = conn.cursor()
    sql = "SELECT item_id, SUM(amount) AS total_amount FROM amount GROUP BY item_id"
    cur.execute(sql)
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["item_id", "total_amount"])
    cur.close()
    conn.close()
    return df