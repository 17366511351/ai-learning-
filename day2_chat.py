# -*- coding: utf-8 -*-
"""
day2_chat.py —— D1 第二天的产出：多轮对话命令行程序
========================================================

这是今天的"参考答案"。正确用法：
    1) 先把它跑起来，感受一下多轮对话是什么效果
    2) 然后关掉它，凭理解从零写一遍（放到 day2-1.py）
    3) 最后回来对照，看有没有漏掉的处理

它能做什么：
    - 连续多轮对话（模型"记得"前面说过的话）
    - 实时统计 token 花费
    - 上下文自动裁剪（防止越聊越贵、超出窗口）
    - 调试命令：/history /tokens /clear /trim /exit
"""

import os
import sys
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI


# ============================================================
# 配置
# ============================================================
BASE_URL = "https://api.deepseek.com"
API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL = "deepseek-flash"

SYSTEM_PROMPT = "你是一个简洁的助手，回答控制在三句话以内。"

# 保留最近几轮对话（1 轮 = 1 条 user + 1 条 assistant）
MAX_TURNS = 8


def make_client():
    key = os.getenv(API_KEY_ENV)
    if not key:
        print(f"没读到环境变量 {API_KEY_ENV}，请检查 .env 文件。")
        sys.exit(1)
    return OpenAI(api_key=key, base_url=BASE_URL)


# ============================================================
# 核心：一个 ChatSession 类，把"对话历史"封装起来
#
# 这是今天要真正理解的东西——模型本身没有记忆，
# messages 列表就是它全部的"记忆"。你维护这个列表，
# 就等于在维护对话的上下文。
# ============================================================
class ChatSession:
    def __init__(self, client, model=MODEL, system_prompt=SYSTEM_PROMPT,
                 max_turns=MAX_TURNS):
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        # 初始化时就把 system 放进列表，之后永远保持在第 0 位
        self.messages = [{"role": "system", "content": system_prompt}]
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.call_count = 0

    # ---------- 发一轮对话 ----------
    def ask(self, user_input: str) -> str:
        # 第 1 步：把用户这句话追加进历史
        self.messages.append({"role": "user", "content": user_input})

        # 第 2 步：把「整个历史」发出去（不是只发这一句！）
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )

        reply = response.choices[0].message.content

        # 第 3 步：把模型的回复也追加进历史，下一轮它才"记得"
        self.messages.append({"role": "assistant", "content": reply})

        # 第 4 步：累计用量
        usage = response.usage
        self.total_prompt_tokens += usage.prompt_tokens
        self.total_completion_tokens += usage.completion_tokens
        self.call_count += 1

        return reply

    # ---------- 上下文裁剪：只保留 system + 最近 N 轮 ----------
    def trim(self):
        """把老对话丢掉，只留 system 和最近 max_turns 轮。

        这是「上下文管理」的最小雏形。真实项目里还会用
        摘要压缩、向量检索等方式，但原理都是：不能让 messages 无限长。
        """
        system = self.messages[0]
        dialog = self.messages[1:]                    # 去掉 system
        keep = self.max_turns * 2                     # 每轮 user + assistant 两条
        if len(dialog) <= keep:
            return 0
        dropped = len(dialog) - keep
        self.messages = [system] + dialog[-keep:]
        return dropped

    # ---------- 调试用 ----------
    def history(self):
        return json.dumps(self.messages, ensure_ascii=False, indent=2)

    def stats(self):
        total = self.total_prompt_tokens + self.total_completion_tokens
        return (f"本次会话共 {self.call_count} 次调用｜"
                f"输入 {self.total_prompt_tokens} token｜"
                f"输出 {self.total_completion_tokens} token｜"
                f"合计 {total} token")


# ============================================================
# 命令行界面
# ============================================================
HELP = """
可用命令：
  /history   查看当前 messages 数组（这就是发给模型的全部内容）
  /tokens    查看本次会话的 token 累计
  /trim      手动裁剪上下文（保留最近 8 轮）
  /clear     清空对话，回到初始状态
  /exit      退出
"""


def main():
    client = make_client()
    session = ChatSession(client)

    print("=" * 62)
    print("  多轮对话 Demo　模型：" + MODEL)
    print("  直接输入问题开始聊天，/exit 退出，/help 看命令")
    print("=" * 62)

    while True:
        try:
            user_input = input("\n你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break

        if not user_input:
            continue

        if user_input == "/exit":
            print(session.stats())
            break
        if user_input == "/help":
            print(HELP)
            continue
        if user_input == "/history":
            print(session.history())
            continue
        if user_input == "/tokens":
            print(session.stats())
            continue
        if user_input == "/clear":
            session = ChatSession(client)
            print("对话已清空。")
            continue
        if user_input == "/trim":
            n = session.trim()
            print(f"裁掉了 {n} 条老消息，当前 messages 有 {len(session.messages)} 条。")
            continue

        try:
            t0 = time.time()
            reply = session.ask(user_input)
            cost = time.time() - t0
            print(f"\nAI > {reply}")
            print(f"     （{cost:.1f}s｜messages 共 {len(session.messages)} 条"
                  f"｜本轮合计 {session.total_prompt_tokens + session.total_completion_tokens} token 累计）")
        except Exception as e:
            print(f"\n[出错] {type(e).__name__}: {e}")
            # 出错时把刚才追加的 user 消息撤掉，避免污染历史
            if session.messages and session.messages[-1]["role"] == "user":
                session.messages.pop()
            print("    （已撤销这条消息，可以重新输入）")


if __name__ == "__main__":
    main()
