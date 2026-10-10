import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

r= client.chat.completions.create(
    model="deepseek-flash",
    messages=[{"role": "user", "content": "南京邮电大学在哪个城市？"}],
)

print(r.id)                              # 本次请求的唯一 id，排查问题时给平台报这个
print(r.model)                           # 实际服务的模型
print(r.choices[0].finish_reason)        # 为什么停下：stop=正常说完
print(r.choices[0].message.content)      # 回复正文
print(r.usage)                           # token 用量 → 决定这次花了多少钱