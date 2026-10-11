import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
texts = [
    "你好",
    "你好，请用一句话解释什么是机器学习。",
    "你好，请用一句话解释什么是机器学习。" * 5,
    "Hello, explain machine learning in one sentence.",
]
for t in texts:
    r = client.chat.completions.create(
        model="deepseek-flash",
        messages=[{"role": "user", "content": t}],
    )
    print(f"字符数 {len(t):<5} → 输入 token {r.usage.prompt_tokens}")

