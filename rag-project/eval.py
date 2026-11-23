"""RAG 评测脚本 —— 可复现实验的基石

只测检索层（不调 LLM，不花钱、跑得快），三个指标：
  - Recall@5：前 5 条里有没有命中正确文档（宽口径，命中就算）
  - MRR：正确文档排第几（排第1得1分，第2得0.5分……衡量排序质量）
  - 语料外拒答准确率：top1 相似度低于阈值才算正确拒答

为什么必须有评测集：
  "我加了 Rerank，感觉更准了"——这不是工程，是感觉。
  "Recall@5 从 0.62 → 0.81，代价是延迟 +120ms"——这才是工程，有数据支撑的决策。
  V1 每次优化都跑同一份 eval_set.jsonl，填同一张表，才能证明改动真的有效、没过拟合。

运行：在 rag-project 根目录  python eval.py
"""

# 离线模式：本地已有 bge 模型缓存，禁止联网检查（详见 app/cli.py 顶部注释）
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import json
import sys
import time
from pathlib import Path

from sentence_transformers import SentenceTransformer

from app import config
from app.vectorstore import search

EVAL_PATH = Path(__file__).with_name("eval_set.jsonl")


def load_eval_set(path: Path) -> list[dict]:
    """jsonl：一行一个 JSON 对象。"""
    cases = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def titles_of(hits: list[dict]) -> list[str]:
    return [h.get("metadata", {}).get("title", "") for h in hits]


def recall_at_k(hits: list[dict], gold: list[str], k: int = 5) -> float:
    """Recall@k：前 k 条结果的 title 与标准答案 gold 有交集就记 1 分，否则 0。

    用 set 求交集 & 而不是逐个比；单题得分是 0/1，全体平均后才是召回率。
    """
    if not gold:
        return 0.0
    got = set(titles_of(hits[:k]))
    return 1.0 if set(gold) & got else 0.0


def reciprocal_rank(hits: list[dict], gold: list[str], k: int = 5) -> float:
    """MRR：正确结果排第 r 位就记 1/r 分——排第 1 满分，越靠后分越低。

    Recall 只看"有没有找到"，MRR 看"排得好不好"，两者配合才全面。
    """
    if not gold:
        return 0.0
    for rank, title in enumerate(titles_of(hits[:k]), start=1):   # 排名从 1 开始
        if title in gold:
            return 1.0 / rank
    return 0.0


def run_eval(model, cases: list[dict], k: int = 5, threshold: float = 0.5):
    stats = {"fact": [], "fact_mrr": [], "multi": [], "multi_mrr": [], "out": []}
    latencies = []

    for case in cases:
        t0 = time.perf_counter()
        hits = search(case["q"], model, k)
        latencies.append(time.perf_counter() - t0)

        kind = case["type"]
        if kind == "out":
            # 语料外问题（正确答案就是"不知道"）：top1 分数低 = 正确拒答
            top = hits[0]["score"] if hits else 0.0
            stats[kind].append(1.0 if top < threshold else 0.0)
        else:
            # fact / multi：有标准答案，算召回和排序质量
            stats[kind].append(recall_at_k(hits, case["gold_titles"], k))
            stats[kind + "_mrr"].append(reciprocal_rank(hits, case["gold_titles"], k))

    print("=" * 62)
    print(f"RAG 检索评测 · {len(cases)} 题 · top_k={k}")
    print("=" * 62)
    for kind in ("fact", "multi"):
        vals = stats[kind]
        mrr = stats.get(kind + "_mrr", [])
        print(f"  {kind:6s}  n={len(vals):2d}  Recall@{k}={sum(vals)/len(vals):.3f}"
              f"  MRR={sum(mrr)/len(mrr):.3f}")
    outs = stats["out"]
    print(f"  {'out':6s}  n={len(outs):2d}  拒答准确率={sum(outs)/len(outs):.3f}"
          f"  (threshold={threshold})")
    print(f"  平均检索延迟: {sum(latencies)/len(latencies)*1000:.1f} ms")
    print("=" * 62)
    print("这组数字就是 V0 基线 —— V1 做 BM25/RRF/Rerank 后重跑同一份评测集对比。")


if __name__ == "__main__":
    cases = load_eval_set(EVAL_PATH)
    print(f"载入评测集 {len(cases)} 题："
          f"fact={sum(c['type']=='fact' for c in cases)}, "
          f"multi={sum(c['type']=='multi' for c in cases)}, "
          f"out={sum(c['type']=='out' for c in cases)}")
    model = SentenceTransformer(config.EMBED_MODEL)
    run_eval(model, cases, k=config.TOP_K)
