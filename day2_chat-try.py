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

KEEP_RECENT = 4
messages = [
    {"role": "system", "content": "你是一个用于解答用户的知识宝库，回答尽可能准确详细"}
]

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    print(" 没有找到 DEEPSEEK_API_KEY")
    print("   请检查 .env 文件是否存在，以及变量名有没有拼错")
    sys.exit(1)        

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
def summarize_history():
    global messages                                   
    system = messages[0]                              
    dialog = messages[1:]                                                        
    keep = KEEP_RECENT * 2
    if len(dialog) <= keep + 2:
        return
    old_dialog=dialog[:-keep]
    recent_dialog=dialog[-keep:]
    text = ""
    for m in old_dialog:
          role = "用户" if m["role"] == "user" else "助手"
          text += f"{role}: {m['content']}\n"
          
    summary_prompt = (
        "请用简洁的中文总结下面这段对话的关键信息，"
        "包括用户的需求、已经确认的事实、重要结论。"
        "控制在 200 字以内。\n\n" + text
    )
    try:
        resp = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": "你是一个善于总结对话的助手。"},
            {"role": "user", "content": summary_prompt},
        ],
    )
        summary = resp.choices[0].message.content
    except Exception:
        messages=[messages[0]] + recent_dialog
        return
    
    messages = [
        {"role": "system",
         "content": system["content"]+f"\n\n【之前对话的摘要】{summary}"},
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
        return None,f"{type(e).__name__}: {e}"
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    summarize_history() 
    return reply,None


if __name__ == "__main__":
    while True:
        user_input = input("你 > ").strip()

        if user_input == "/exit":
            print("再见！")
            break

        if not user_input:
            continue

        reply, error = chat(user_input)
        if error:
            print(f"\n️  请求失败：{error}\n")              
        else:
            print(f"\nAI > {reply}")
            print(f"\n    (历史 {len(messages)} 条)\n")
