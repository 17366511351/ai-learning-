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
        {"role": "user",   "content": "给一家开在大学旁边的咖啡店起个名字，只输出名字。"},
    ],
temperature=1.5,
)

print(response.choices[0].message.content)