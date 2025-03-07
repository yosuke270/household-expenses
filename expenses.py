#家計簿をつけるアプリ
#自然言語で入力されたデータを分析して家計簿をつける。「すき家に３００円」と入力すれば、LLMが食費と推定してデータベースに登録する
import os
from openai import OpenAI

api_key = os.environ["ChatGPT_API"]
client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system","content": "家計簿をつける係です。入力から出力を考えてください。出力は次の形式をとってください。{カテゴリ：金額}カテゴリは食費、娯楽費、交通費から適切なものを選択してください。"},
        {"role": "user","content": "すき家に３００円"},
   ]
)

print(response.choices[0].message.content)
