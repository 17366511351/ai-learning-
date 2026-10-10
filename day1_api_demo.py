# -*- coding: utf-8 -*-
"""
day1_api_demo.py —— D0 第一天：跑通第一次大模型 API 调用
==========================================================

用法：
    1) pip install openai python-dotenv
    2) 把 env.example 复制成 .env，填入你的 Key（或直接设环境变量）
    3) python day1_api_demo.py

今天只需要跑通 Part 1 和 Part 2。
Part 3 / Part 4 是明天和后天的内容，先跑一遍看效果，代码看不懂没关系。
"""

import os
import sys
import json
import time

# Windows 终端默认编码不是 UTF-8，不加重定向的话中文会变乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 自动读取同目录下的 .env 文件；没装 python-dotenv 也不影响运行
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI


# ============================================================
# 平台配置表：换供应商只需要改这里，代码一行都不用动
# ============================================================
PROVIDERS = {
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "key_env":  "DEEPSEEK_API_KEY",
        "model":    "deepseek-flash",
    },
    "dashscope": {   # 通义千问（阿里云百炼）
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key_env":  "DASHSCOPE_API_KEY",
        "model":    "qwen3.7-plus",
    },
    "zhipu": {       # 智谱 GLM，注意路径是 /api/paas/v4 不是 /v1
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "key_env":  "ZHIPUAI_API_KEY",
        "model":    "glm-4-flash",
    },
    "siliconflow": {  # 硅基流动，模型名带斜杠
        "base_url": "https://api.siliconflow.cn/v1",
        "key_env":  "SILICONFLOW_API_KEY",
        "model":    "deepseek-ai/DeepSeek-V3",
    },
    "moonshot": {     # Kimi
        "base_url": "https://api.moonshot.cn/v1",
        "key_env":  "MOONSHOT_API_KEY",
        "model":    "moonshot-v1-8k",
    },
}


def pick_provider():
    """挑一个可用的平台：优先用环境变量 PROVIDER 指定的，否则用第一个配了 Key 的。"""
    wanted = os.getenv("PROVIDER", "").strip().lower()
    if wanted in PROVIDERS and os.getenv(PROVIDERS[wanted]["key_env"]):
        return wanted

    for name, cfg in PROVIDERS.items():
        if os.getenv(cfg["key_env"]):
            return name

    print("没有找到任何 API Key。请检查：")
    for name, cfg in PROVIDERS.items():
        print(f"  {name:<12} 需要设置环境变量 {cfg['key_env']}")
    print("\n在 Git Bash 里可以这样临时设置：")
    print('  export DEEPSEEK_API_KEY="sk-你的key"')
    sys.exit(1)


def banner(text):
    print("\n" + "=" * 62)
    print(f"  {text}")
    print("=" * 62)


# ============================================================
# Part 1 · 最小可运行调用（今天必须跑通）
# ============================================================
def part1_minimal(client, model):
    banner("Part 1 · 最小可运行调用")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个说话简洁的助手。"},
            {"role": "user",   "content": "用一句话解释什么是 API。"},
        ],
    )

    answer = response.choices[0].message.content
    print("模型回复：", answer)
    print("\n>>> 核心就一行：response.choices[0].message.content")


# ============================================================
# Part 2 · 解剖响应对象（今天必须跑通）
# ============================================================
def part2_anatomy(client, model):
    banner("Part 2 · 解剖响应对象：模型还告诉了你什么")

    t0 = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "南京邮电大学在哪个城市？一句话回答。"}],
    )
    cost_time = time.time() - t0

    print("请求 id      :", response.id)
    print("实际模型     :", response.model)
    print("choices 数量 :", len(response.choices))
    print("finish_reason:", response.choices[0].finish_reason)
    print("回复正文     :", response.choices[0].message.content)

    usage = response.usage
    print("\n--- token 用量（决定这次花了多少钱）---")
    print("输入 tokens  :", usage.prompt_tokens)
    print("输出 tokens  :", usage.completion_tokens)
    print("合计 tokens  :", usage.total_tokens)

    # 部分平台会额外返回缓存命中信息，用 getattr 兜底避免报错
    cached = getattr(usage, "prompt_cache_hit_tokens", None)
    if cached is not None:
        print("缓存命中     :", cached, "（命中部分单价极低，是省钱关键）")

    print(f"本次耗时     : {cost_time:.2f} 秒")


# ============================================================
# Part 3 · 改参数看差异（明天的内容，先体验）
# ============================================================
def part3_params(client, model):
    banner("Part 3 · temperature 实验：0.0 vs 1.5")

    question = "给一家咖啡店起一个名字，只输出名字本身。"
    for temp in (0.0, 1.5):
        print(f"\ntemperature = {temp}")
        for i in range(3):
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": question}],
                temperature=temp,
            )
            print(f"  第{i + 1}次：", r.choices[0].message.content.strip())

    print("\n>>> 观察：temperature=0 时几乎每次一样，1.5 时每次不同。")
    print(">>> 需要稳定输出（抽取/分类）调低；需要创意发散调高。")

    print("\n--- 顺便看看 max_tokens 被截断时会发生什么 ---")
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "写一篇 300 字的作文介绍南京。"}],
        max_tokens=20,
    )
    print("回复内容     :", r.choices[0].message.content)
    print("finish_reason:", r.choices[0].finish_reason, "（length 表示被截断了）")


# ============================================================
# Part 4 · 多轮对话（明天/后天的内容，先体验）
# ============================================================
def part4_multi_turn(client, model):
    banner("Part 4 · 多轮对话：自己维护 messages 数组")

    history = [{"role": "system", "content": "你是一个简洁的 Python 助教，回答不超过两句话。"}]

    def ask(question):
        history.append({"role": "user", "content": question})
        r = client.chat.completions.create(model=model, messages=history)
        answer = r.choices[0].message.content
        # 关键：把模型的回复也塞回历史，下一轮它才"记得"
        history.append({"role": "assistant", "content": answer})
        return answer

    for q in ["什么是装饰器？", "举个例子", "那它和闭包什么关系？"]:
        print(f"\n我：{q}")
        print(f"AI：{ask(q)}")
        print(f"   (此刻 messages 里已有 {len(history)} 条消息)")

    print("\n--- 第二轮请求时真正发出去的 JSON 长这样（这就是'上下文'）---")
    print(json.dumps(history, ensure_ascii=False, indent=2))

    print("\n>>> 注意：数组越滚越长，token 越花越多。")
    print(">>> 模型本身没有记忆，是你在每轮把历史全量重发。")


def main():
    name = pick_provider()
    cfg = PROVIDERS[name]

    client = OpenAI(api_key=os.getenv(cfg["key_env"]), base_url=cfg["base_url"])
    model = os.getenv("MODEL", cfg["model"])

    print(f"平台：{name}　base_url：{cfg['base_url']}　模型：{model}")
    print("（改平台只需设置环境变量 PROVIDER=zhipu 之类，代码不用动）")

    # 想只跑其中一部分，把不需要的行加上 # 注释掉即可
    part1_minimal(client, model)
    part2_anatomy(client, model)
    part3_params(client, model)
    part4_multi_turn(client, model)

    banner("全部跑通。别忘了：写笔记 + 推 GitHub + 填「卡点清单」")


if __name__ == "__main__":
    main()
