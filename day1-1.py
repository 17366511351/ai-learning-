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
        {"role": "system", "content": "你是一个说话简洁的助手。"},
        {"role": "user",   "content": "用一句话解释什么是 API。"},
    ],
)

print(response.choices[0].message.content)