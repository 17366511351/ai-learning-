# -*- coding: utf-8 -*-
"""
day3_async_demo.py  ·  W1 第一课：异步到底快在哪
====================================================
运行方式：python day3_async_demo.py

Part 0 / 1 / 2  不需要 API Key，秒跑，专门用来看时间差
Part 3          需要 .env 里的 DEEPSEEK_API_KEY，是真实 API 调用对比

今天你只需要看懂一件事：
    慢的不是"计算"，是"等"。异步就是让"等"这件事重叠起来。
"""
import asyncio
import os
import sys
import time

# Windows 控制台默认不是 UTF-8，这句能避免中文乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def title(text):
    print()
    print("=" * 64)
    print("  " + text)
    print("=" * 64)


def line():
    print("-" * 64)


# ==========================================================
# Part 0 · 同步串行：一个做完才做下一个
# ==========================================================

def fake_call_sync(name, seconds=1.0):
    """假装这是一次耗时的网络请求（比如调用大模型 API）"""
    print(f"    [{name}] 发出请求…")
    time.sleep(seconds)          # ← 关键：time.sleep 会卡住整个程序
    print(f"    [{name}] 拿到结果")
    return name + " 的结果"


def part0():
    title("Part 0 · 同步串行 —— 一个做完才做下一个")
    print("  场景：依次问模型 3 个问题，每个问题耗时 1 秒（用 sleep 模拟）\n")

    t0 = time.perf_counter()
    results = []
    for name in ["问题A", "问题B", "问题C"]:
        results.append(fake_call_sync(name, 1.0))
    cost = time.perf_counter() - t0

    print(f"\n  结果：{results}")
    print(f"  总耗时：{cost:.2f} 秒")
    print("  ── 3 个请求 × 1 秒 = 3 秒。因为第 2 个要等第 1 个彻底做完才开始。")
    return cost


# ==========================================================
# Part 1 · 换成了 async/await，但老实的一个等一个
# ==========================================================

async def fake_call_async(name, seconds=1.0):
    """和上面做同一件事，但这次是「异步」版本"""
    print(f"    [{name}] 发出请求…")
    await asyncio.sleep(seconds)   # ← 关键：asyncio.sleep 会把"等待"交出去，不霸占程序
    print(f"    [{name}] 拿到结果")
    return name + " 的结果"


async def part1():
    title("Part 1 · 明明是 async/await，为什么还是 3 秒？")
    print("  场景：和上面完全一样，依次问 3 个问题\n")

    t0 = time.perf_counter()
    results = []
    for name in ["问题A", "问题B", "问题C"]:
        r = await fake_call_async(name, 1.0)   # ← await = "我等它做完，再走下一行"
        results.append(r)
    cost = time.perf_counter() - t0

    print(f"\n  结果：{results}")
    print(f"  总耗时：{cost:.2f} 秒")
    print("  ── 还是 3 秒！")
    print("  ── 【今天最重要的认知】async 只是「允许」你并发，不等于「自动」并发。")
    print("     你在循环里逐个 await，等于还是排队，一个等一个。")
    return cost


# ==========================================================
# Part 2 · asyncio.gather —— 真正的并发
# ==========================================================

async def part2():
    title("Part 2 · asyncio.gather —— 三个一起发出去")
    print("  场景：还是同样 3 个问题，但这次同时发出去\n")

    t0 = time.perf_counter()
    results = await asyncio.gather(
        fake_call_async("问题A", 1.0),
        fake_call_async("问题B", 1.0),
        fake_call_async("问题C", 1.0),
    )
    cost = time.perf_counter() - t0

    print(f"\n  结果：{list(results)}")
    print(f"  总耗时：{cost:.2f} 秒")
    print("  ── 只要 1 秒！三条请求同时在路上，等待时间重叠了。")
    print("  ── 注意上面 3 行的打印顺序是乱的，正说明它们真的在同时跑。")
    return cost


async def run_parts_0_to_2():
    t0 = part0()
    t1 = await part1()
    t2 = await part2()

    title("三条路对比")
    print(f"  同步串行            {t0:.2f} 秒   ████████████████  基准")
    print(f"  async 但逐个 await  {t1:.2f} 秒   ████████████████  白写了")
    print(f"  asyncio.gather      {t2:.2f} 秒   █████              提速 {t0 / t2:.1f} 倍")
    print()
    print("  一句话记住：")
    print("    async/await 是「语法」，asyncio.gather 才是「并发」。")
    print("    光写 async 不给 gather，等于买了车不踩油门。")


# ==========================================================
# Part 3 · 换成真实的大模型 API 调用（需要 Key）
# ==========================================================

QUESTIONS = [
    "用一句话解释什么是机器学习",
    "用一句话解释什么是神经网络",
    "用一句话解释什么是梯度下降",
]


def part3_sync():
    """同步版：真实调用 3 次"""
    from openai import OpenAI

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    title("Part 3-A · 真实 API 调用（同步串行）")
    t0 = time.perf_counter()
    try:
        for q in QUESTIONS:
            resp = client.chat.completions.create(
                model="deepseek-flash",
                messages=[{"role": "user", "content": q}],
            )
            answer = resp.choices[0].message.content.strip().replace("\n", " ")
            print(f"    Q: {q}")
            print(f"    A: {answer[:60]}…")
    except Exception as e:
        print(f"\n  调用失败：{type(e).__name__}: {e}")
        print("  自查：① 网络能否访问 api.deepseek.com  ② Key 是否正确  ③ 余额是否充足")
        return None
    cost = time.perf_counter() - t0
    print(f"\n  总耗时：{cost:.2f} 秒")
    return cost


async def part3_async():
    """异步并发版：真实调用 3 次，同时发出去"""
    from openai import AsyncOpenAI

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None

    client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    async def one(q):
        resp = await client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": q}],
        )
        return q, resp.choices[0].message.content.strip().replace("\n", " ")

    title("Part 3-B · 真实 API 调用（asyncio.gather 并发）")
    t0 = time.perf_counter()
    try:
        pairs = await asyncio.gather(*(one(q) for q in QUESTIONS))
    except Exception as e:
        print(f"\n  调用失败：{type(e).__name__}: {e}")
        print("  自查：① 网络能否访问 api.deepseek.com  ② Key 是否正确  ③ 余额是否充足")
        return None
    for q, a in pairs:
        print(f"    Q: {q}")
        print(f"    A: {a[:60]}…")
    cost = time.perf_counter() - t0
    print(f"\n  总耗时：{cost:.2f} 秒")
    return cost


def main():
    # 先把不要 Key 的三个实验跑掉
    asyncio.run(run_parts_0_to_2())

    # 再跑真实 API（没配 Key 就跳过）
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print()
        print("  [跳过 Part 3] 没有找到 DEEPSEEK_API_KEY，Part 3 需要真实 Key。")
        print("  Part 0-2 已经说明了全部原理，这个跳过不影响。")
        return

    ts = part3_sync()
    ta = asyncio.run(part3_async())

    if ts and ta:
        title("真实 API 对比")
        print(f"  同步串行        {ts:.2f} 秒")
        print(f"  gather 并发     {ta:.2f} 秒")
        print(f"  ── 提速 {ts / ta:.1f} 倍")
        print()
        print("  【记录下来】这两个数字就是你以后简历上")
        print("   「将 N 个请求的响应时间从 X 秒降到 Y 秒」的来源。")


if __name__ == "__main__":
    main()
