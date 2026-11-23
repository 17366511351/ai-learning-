"""命令行入口 —— python -m app.cli "你的问题"

这是 V0 的"总装车间"：把前面所有模块串成一条完整链路
    问题 → 加载模型 → 检索(search) → 判拒答(should_refuse) → 生成(answer) → 打印答案/引用/性能

三条计时（模型加载 / 检索 / 生成）不是随便记的：
  面试被问"你的系统延迟多少、瓶颈在哪"时，这组数字就是答案——
  加载是启动一次性成本，检索 ~20ms，生成 2s+，瓶颈明显在 LLM，优化方向就很清楚。

V2 时在这里加：多轮对话模式（维护 query 历史 + 指代改写）
"""

# 离线模式：本地已有 bge 模型缓存，禁止联网检查。
# 新版 transformers 会去 huggingface 请求一个可选配置文件，国内网络连不上会卡住并报 ValueError。
# 若将来要下载新模型（如换 embedding），把下面这行改成 "0" 或删掉即可。
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import sys
import time
from sentence_transformers import SentenceTransformer
from app import config
from app.vectorstore import search
from app.generate import answer, should_refuse


def _ms(seconds):
    """秒 → 毫秒字符串，统一格式，避免各处重复写 *1000。"""
    return f"{seconds * 1000:.1f} ms"


def _print_citations(citations, hits):
    """把答案里的 [n] 编号映射回真实来源：标题/章节/页码/相似度。

    这就是"答案可追溯"的实现——面试官问"怎么防幻觉"，这段是证据：
    每个结论都能点回原文，编号 n 对应 hits[n-1]（★ 编号从 1 开始，列表下标从 0 开始，要 -1）。
    """
    if not citations:
        print("(无引用)")
        return
    for n in citations:
        if not (1 <= n <= len(hits)):         # 防御：模型若编造了 [9] 这种越界编号，跳过
            continue
        hit = hits[n - 1]                      # ★ 编号 → 下标的关键偏移
        meta = hit.get("metadata", {})
        title = meta.get("title", "未知")
        section = meta.get("section", "")
        page = meta.get("page", 0)
        score = hit.get("score", 0.0)
        loc = f"{title}/{section}" if section else title
        if page:
            loc += f" 第{page}页"
        snippet = (hit.get("text") or "").replace("\n", " ")[:100]   # 换行替换成空格，截断 100 字
        print(f"[{n}] {loc}  (score={score:.3f})")
        print(f"    {snippet}...")


def main():
    # ---- 1. 读命令行参数：sys.argv[1:] 是问题词的列表，join 拼回一句 ----
    if len(sys.argv) < 2:
        print("用法: python -m app.cli \"你的问题\"")
        sys.exit(1)
    question = "".join(sys.argv[1:]).strip()
    if not question:
        print("问题不能为空")
        sys.exit(1)

    # ---- 2. 加载 embedding 模型：perf_counter 高精度计时，全局只加载一次（很贵） ----
    # ★ perf_counter 拼写是 perf（性能），不是 pref；且是函数要带 () —— 这里是之前踩的坑
    t0 = time.perf_counter()
    embed = SentenceTransformer(config.EMBED_MODEL)
    t_load = time.perf_counter() - t0

    # ---- 3. 检索：把问题变成向量，查 top_k 个最相关的 chunk ----
    t1 = time.perf_counter()
    hits = search(question, embed, config.TOP_K)
    t_search = time.perf_counter() - t1

    # ---- 4. 拒答分支：分数太低说明语料里没答案，直接拒，不浪费 API token ----
    if should_refuse(hits):
        top_score = hits[0]["score"] if hits else 0.0
        print("\n=== 答案 ===")
        print("抱歉，资料中没有相关内容，无法回答。")
        print("\n=== 引用 ===")
        print("(拒答，无引用)")
        print("\n=== 性能 ===")
        print(f"模型加载: {_ms(t_load)}")
        print(f"检索耗时: {_ms(t_search)}  (top_k={config.TOP_K}, hits={len(hits)}, top_score={top_score:.3f})")
        print("生成耗时: 0.0 ms  (拒答，未调用 LLM)")
        print("Token 用量: prompt=0, completion=0, total=0")
        return                                  # 提前返回，不调 LLM

    # ---- 5. 生成分支：把检索结果拼进 prompt 交给 LLM ----
    t2 = time.perf_counter()
    result = answer(question, hits)
    t_gen = time.perf_counter() - t2
    # 三处 .get 兜底：即使某个字段缺失也不崩（answer 失败时返回的是空结构）
    text = result.get("answer", "")
    citations = result.get("citations", []) or []
    usage = result.get("usage", {}) or {}
    p_tok = usage.get("prompt_tokens", 0)
    c_tok = usage.get("completion_tokens", 0)

    # ---------- 6. 输出：答案 + 引用 + 性能 ----------
    print("\n=== 答案 ===")
    print(text.strip() or "(空)")

    print("\n=== 引用 ===")
    _print_citations(citations, hits)

    # ---------- 7. 性能 + token：这组数字就是简历素材 ----------
    print("\n=== 性能 ===")
    print(f"模型加载: {_ms(t_load)}")
    print(f"检索耗时: {_ms(t_search)}  (top_k={config.TOP_K}, hits={len(hits)}, top_score={hits[0]['score']:.3f})")
    print(f"生成耗时: {_ms(t_gen)}")
    print(f"检索+生成: {_ms(t_search + t_gen)}  (不含加载，这才是服务端延迟)")
    print(f"Token 用量: prompt={p_tok}, completion={c_tok}, total={p_tok + c_tok}")


if __name__ == "__main__":
    main()
