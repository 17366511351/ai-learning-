"""
day2_chat-try.py D1多轮对话命令行程序
=====================================
"""
import os
import sys
import json
import time
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from openai import OpenAI
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MAX_TURNS = 8
KEEP_RECENT = 4
messages = [
    {"role": "system", "content": "你是一个用于解答用户的知识宝库，回答尽可能准确详细"}
]

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    print(" 没有找到 DEEPSEEK_API_KEY")
    print("   请检查 .env 文件是否存在，以及变量名有没有拼错")
    sys.exit(1)        # sys 你已经 import 了，正好用上

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
def summarize_history():
    global messages                                   
    system = messages[0]                              
    dialog = messages[1:]                                                        
    keep = MAX_TURNS * 2
    if len(dialog) <= keep:
        return
    recent_content =KEEP_RECENT * 2
    old_dialog=dialog[:-recent_content]
    recent_dialog=dialog[-recent_content:]
    text = ""
    for m in old_dialog:
          role = "用户" if m["role"] == "user" else "助手"
          text += f"{role}: {m['content']}\n"
          summary_prompt = (
        "请用简洁的中文总结下面这段对话的关键信息，"
        "包括用户的需求、已经确认的事实、重要结论。"
        "控制在 200 字以内。\n\n" + text
    )

    resp = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": "你是一个善于总结对话的助手。"},
            {"role": "user", "content": summary_prompt},
        ],
    )
    summary = resp.choices[0].message.content

    messages = [
        {"role": "system", "content": f"【之前对话的摘要】{summary}"},
    ] + recent_dialog

def chat(question):
    messages.append({"role": "user", "content": question})
    try:
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
    )
    except Exception as e:
        messages.pop()
        return f"[出错了] {type(e).__name__}: {e}"

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    summarize_history() 
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