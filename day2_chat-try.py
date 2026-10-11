"""
day2_chat-try.py D1多轮对话命令行程序
=====================================
"""
import os
import sys
import json
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

messages = [
    {"role": "system", "content": "你是一个用于解答用户的知识宝库，回答尽可能准确详细"}
]

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)


def chat(question):
    messages.append({"role": "user", "content": question})
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
    )
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply


if __name__ == "__main__":
    while True:
        user_input = input("你 > ").strip()

        if user_input == "/exit":
            print("再见！")
            break

        if not user_input:
            continue

        answer = chat(user_input)
        print(f"AI > {answer}")
        print(f"     (历史 {len(messages)} 条)\n")