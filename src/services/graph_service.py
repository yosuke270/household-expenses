import matplotlib.pyplot as plt
import matplotlib
from utils.logger import logger

matplotlib.rc('font', family='Meiryo')
matplotlib.use('Agg')

def plot_graph(df):
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
    df["item_name"] = df["item_id"].map(item_labels)
    plt.figure(figsize=(10, 6))
    plt.bar(df["item_name"], df["total_amount"], color="skyblue")
    plt.title("カテゴリ別支出合計", fontsize=16)
    plt.xlabel("カテゴリ", fontsize=12)
    plt.ylabel("支出額 (円)", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()