# -*- coding: utf-8 -*-
"""
练习2-异步改造.py  ·  亲手把同步代码改成异步
====================================================
运行：python 练习2-异步改造.py

规则（和练习1一样）：
    · 不要先看答案，自己填 TODO
    · 填对了打印 ✅，填错了抛 AssertionError 告诉你哪里不对
    · 不需要 API Key，纯本地，秒跑

今天的目标不是"填对"，是亲眼看到时间从 3 秒变成 1 秒。
"""
import asyncio
import inspect
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


CITIES = ["北京", "上海", "广州"]


# ==========================================================
# 先看懂这个"老师写的同步版"，它就是你要改造的对象
# ==========================================================

def get_weather_sync(city):
    """查一次天气，假装要 1 秒（真实场景里就是一次 API 请求）"""
    time.sleep(1)
    return city + "：晴，22°C"


# ==========================================================
# TODO 1
# 把这个函数改成"异步版"：
#   ① def 前面加 async        →  async def get_weather(city):
#   ② time.sleep(1) 换成      →  await asyncio.sleep(1)
# 改完之后，它就是"可以被并发调度"的函数了。
# ==========================================================

def get_weather(city):          # ← TODO 1-①：这里要加 async
    time.sleep(1)               # ← TODO 1-②：这里要改成 await asyncio.sleep(1)
    return city + "：晴，22°C"


# ==========================================================
# TODO 2
# 逐个请求（串行）。给 get_weather(c) 前面加上 await。
# 注意：加了 await 之后它依然要 3 秒——这正好证明
#       "光有 async，不给 gather，等于白写"。
# ==========================================================

async def get_all_serial(cities):
    results = []
    for c in cities:
        r = get_weather(c)      # ← TODO 2：少了个 await
        results.append(r)
    return results


# ==========================================================
# TODO 3
# 用 asyncio.gather 把三个请求"同时发出去"。
# 提示：results = await asyncio.gather(*[get_weather(c) for c in cities])
#       注意别写成 await asyncio.gather(get_weather(cities))，那是"一个任务"不是"三个"
# ==========================================================

async def get_all_parallel(cities):
    results = []                # ← TODO 3：整段替换成 gather 写法
    return list(results)


# ==========================================================
# 下面是自动判题，你不需要改
# ==========================================================

def report(name, ok, msg):
    print(("  ✅ " if ok else "  ❌ ") + name + "：" + msg)
    return ok


def main():
    print()
    print("=" * 60)
    print("  异步改造练习 · 自动判题")
    print("=" * 60)

    all_ok = True

    # ---- 判题 1 ----
    print("\n【TODO 1】get_weather 是否真的变成了异步")
    if not inspect.iscoroutinefunction(get_weather):
        all_ok = report("TODO 1", False, "还不是协程函数，def 前面要加 async") and False
    else:
        t0 = time.perf_counter()
        try:
            ans = asyncio.run(get_weather("测试"))
        except TypeError as e:
            all_ok = report("TODO 1", False, "调用方式不对：" + str(e)) and False
            ans = None
        cost = time.perf_counter() - t0
        if ans is not None:
            if cost > 1.4:
                all_ok = report(
                    "TODO 1", False,
                    "函数是 async 了，但里面还是阻塞的 time.sleep"
                    "（单次耗时 %.2f 秒）。换成 await asyncio.sleep(1)" % cost
                ) and False
            elif "22" not in ans:
                all_ok = report("TODO 1", False, "返回值不对：" + str(ans)) and False
            else:
                all_ok = report("TODO 1", True, "是协程函数，且等待不阻塞（耗时 %.2f 秒）" % cost) and all_ok

    # ---- 判题 2 ----
    print("\n【TODO 2】get_all_serial 是否正确串行")
    try:
        t0 = time.perf_counter()
        r2 = asyncio.run(get_all_serial(CITIES))
        c2 = time.perf_counter() - t0
    except Exception as e:
        r2, c2 = None, 0
        all_ok = report("TODO 2", False, type(e).__name__ + "：" + str(e)) and False
    if r2 is not None:
        if not inspect.iscoroutinefunction(get_weather):
            all_ok = report("TODO 2", False, "先完成 TODO 1：get_weather 得先是异步函数，这里才有意义") and False
        elif len(r2) != 3:
            all_ok = report("TODO 2", False, "结果应该是 3 条，实际 %d 条 —— 可能忘了 await" % len(r2)) and False
        elif not all(isinstance(x, str) for x in r2):
            all_ok = report("TODO 2", False, "结果里混进了协程对象，说明某个地方忘了 await") and False
        elif c2 < 2.5:
            all_ok = report("TODO 2", False, "耗时 %.2f 秒，不该这么快，检查一下是不是有地方没 await" % c2) and False
        else:
            all_ok = report("TODO 2", True, "3 条结果正确，耗时 %.2f 秒（串行，还是慢）" % c2) and all_ok

    # ---- 判题 3 ----
    print("\n【TODO 3】get_all_parallel 是否用上了 gather 并发")
    try:
        t0 = time.perf_counter()
        r3 = asyncio.run(get_all_parallel(CITIES))
        c3 = time.perf_counter() - t0
    except Exception as e:
        r3, c3 = None, 0
        all_ok = report("TODO 3", False, type(e).__name__ + "：" + str(e)) and False
    if r3 is not None:
        if len(r3) != 3:
            all_ok = report("TODO 3", False, "结果应该是 3 条，实际 %d 条" % len(r3)) and False
        elif not all(isinstance(x, str) for x in r3):
            all_ok = report("TODO 3", False, "结果里混进了协程对象，gather 写法有问题") and False
        elif c3 > 1.5:
            all_ok = report("TODO 3", False, "耗时 %.2f 秒，没有并发起来。要用 asyncio.gather" % c3) and False
        else:
            all_ok = report("TODO 3", True, "3 条结果正确，耗时 %.2f 秒 —— 提速 %.1f 倍" % (c3, c2 / c3 if c2 else 0)) and all_ok

    # ---- 总结 ----
    print()
    print("=" * 60)
    if all_ok:
        print("  三题全过。你现在能回答这个问题了吗：")
        print("  「为什么加了 async 还是 3 秒，加了 gather 才变 1 秒？」")
    else:
        print("  还有 TODO 没过。看上面对应的 ❌ 提示，改完再跑一次。")
    print("=" * 60)


if __name__ == "__main__":
    main()
