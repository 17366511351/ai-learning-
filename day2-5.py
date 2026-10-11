import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {"role": "user",   "content": "用一句话形容秋天，不要用'金黄'这个词。"},
    ],
temperature=1.5,
)

print(response.choices[0].message.content)