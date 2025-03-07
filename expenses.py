#家計簿をつけるアプリ
#自然言語で入力されたデータを分析して家計簿をつける。「すき家に３００円」と入力すれば、LLMが食費と推定してデータベースに登録する
import os
from openai import OpenAI

api_key = os.environ["ChatGPT_API"]
client = OpenAI(api_key=api_key)

print("出費を入力してください")
input = input()

prompt = f"""\
## 指示
- あなたは家計簿のデータベースを管理し解析するAIです。
- INPUTを解析して、結果をOUTPUT_TEMPLATEに従って出力してください。
- 出力はOUTPUT_exampleを参考にしてください。
## 注意事項
- 出力は必ずOUTPUT_exampleに従ってください。
- INPUTには、話し言葉で入力されたデータです。うまく解析してください。
- カテゴリは、食費、交通費、日用品、居住費、医療費から選ばれます。
- 日付がわからない場合は、今日の日付を入力してください。
- inputが不明な場合は、「エラー：入力が不明」と出力してください。
- 内容は、入力された内容から抽出してください。
- inputに複数のデータが入力された場合はOUTPUT_exampleを参考に複数の出力をしてください。

## INPUT
{input}

## OUTPUT_example
内容　　：ラーメン
カテゴリ：食費
金額　　：600円
日付　　：2023年1月1日
=====
内容　　：洋服
カテゴリ：日用品
金額　　：1111円
日付　　：2023年1月1日
"""



response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system","content": prompt},
   ]
)

print(response.choices[0].message.content)
