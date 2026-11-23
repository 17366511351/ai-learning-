"""生成模块 —— 拼 Prompt、调模型、拒答。

设计要点：
- build_prompt：把检索结果组装成带编号引用的上下文
- answer：调 DeepSeek（OpenAI 兼容接口），返回答案 + 引用编号 + token
- should_refuse：最高相似度低于阈值 → 直接拒答，不浪费 token
"""

import re

from openai import OpenAI

from app import config


SYSTEM_PROMPT = """你是一个严谨的知识库问答助手。回答规则：
1. 只依据下面提供的【资料】回答，禁止使用资料之外的任何知识。
2. 每个关键结论后标注来源编号，如 [1]、[2]。
3. 如果资料中没有足够信息回答问题，直接回答：
   "抱歉，资料中没有相关内容，无法回答。" —— 这不是失败，是正确行为。
4. 用简洁中文回答，先给结论再给解释。"""


def build_prompt(question: str, hits: list[dict]) -> str:
    """把 hits 组装成带编号的上下文，编号从 1 开始，与 citations 对应。

    ★ start=1 是关键：编号 1..n 给模型看，它回答时引用 [1]，
      后面 _print_citations 用 hits[n-1] 换回原文。若从 0 开始，模型引用 [0] 会和人类直觉冲突。
    """
    blocks = []
    for i, hit in enumerate(hits, start=1):
        meta = hit.get("metadata", {}) or {}   # or {} 兜底：metadata 是 None 时也不崩
        title = meta.get("title", "未知来源")
        section = meta.get("section", "")
        page = meta.get("page", 0)

        loc = f"{title}/{section}" if section else title
        if page:
            loc += f" 第{page}页"

        # [:500] 保险丝：单个 chunk 最多取 500 字，防止一条超长结果撑爆上下文窗口
        text = (hit.get("text") or "")[:500]
        blocks.append(f"[{i}] 来源：{loc}\n{text}")

    contexts = "\n\n".join(blocks)
    return (
        f"【资料】\n{contexts}\n\n"
        f"【问题】\n{question}\n\n"
        f"请严格按照规则回答，并在关键结论后标注来源编号。"
    )


def should_refuse(hits: list[dict], threshold: float = 0.5) -> bool:
    """无召回 或 最高相似度低于阈值 → 拒答，不调 LLM。

    ★ 阈值 0.5 是 V0 的拍脑袋起点，实测语料外问题只拒对 33%（bge 对任何中文都给 0.4-0.7 分）。
      这就是今天的"阈值标定实验"要解决的问题：打印语料内/外问题的分数分布，找最佳分界点。
      面试题 30/64 问的就是"怎么防止 RAG 一本正经地胡说八道"。
    """
    if not hits:                               # 一条都没召回 → 必然拒答
        return True
    return hits[0].get("score", 0.0) < threshold   # hits 按 score 降序，hits[0] 是最高分


def answer(question: str, hits: list[dict]) -> dict:
    """调模型生成答案。返回 {"answer", "citations", "usage"}，失败不抛异常。"""
    prompt = build_prompt(question, hits)

    try:
        client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)
        resp = client.chat.completions.create(
            model=config.CHAT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0,               # 问答要确定性：同一问题每次答得一样，便于复现和评测
        )
    except Exception as e:
        return {
            "answer": f"生成失败：{type(e).__name__}: {e}",
            "citations": [],
            "usage": {},
        }

    text = resp.choices[0].message.content or ""

    # 抽取答案里出现的 [n]：re.findall 找所有 "[数字]"，捕获组 (\d+) 只要数字部分
    # 用 set 去重（模型可能重复引用 [1] [1]），再过滤越界编号（模型可能编造 [9]）
    raw = {int(n) for n in re.findall(r"\[(\d+)\]", text)}
    citations = sorted(n for n in raw if 1 <= n <= len(hits))

    usage = {}
    if resp.usage:
        usage = {
            "prompt_tokens": resp.usage.prompt_tokens,
            "completion_tokens": resp.usage.completion_tokens,
            "total_tokens": resp.usage.total_tokens,
        }

    return {"answer": text, "citations": citations, "usage": usage}
