"""生成模块 —— 拼 Prompt、调模型、流式输出、拒答。

TODO(你来做)：
1. build_prompt：把检索结果组装成带编号引用的上下文
2. answer：调模型（V0 同步即可；V2 接 AsyncOpenAI 流式）
3. 拒答逻辑（V2 加）：最高相似度低于阈值 → 直接返回"资料中没有"

这里是你系统里「幻觉防线」的主战场，prompt 写不好全白搭。
"""

SYSTEM_PROMPT = """你是一个严谨的知识库问答助手。回答规则：
1. 只依据下面提供的【资料】回答，禁止使用资料之外的任何知识。
2. 每个关键结论后标注来源编号，如 [1]、[2]。
3. 如果资料中没有足够信息回答问题，直接回答：
   "抱歉，资料中没有相关内容，无法回答。" —— 这不是失败，是正确行为。
4. 用简洁中文回答，先给结论再给解释。"""

def build_prompt(question: str, hits: list[dict]) -> str:
    """TODO: 把检索结果编号组装。
    格式：
        【资料】
        [1] (来源: xxx, 页码 p)  内容...
        [2] ...

    要点：资料太长时截断 —— 每段最多 500 字，别把窗口塞爆。
    """
    ...

def answer(question: str, hits: list[dict]) -> dict:
    """TODO: 生成答案。
    - OpenAI(api_key=..., base_url=...) 客户端
    - messages = [system] + [user: build_prompt(...)]
    - 返回 {"answer": str, "citations": [1,2], "usage": {...}}
    - 从 answer 文本里用正则抽出引用编号 [n]，方便前端展示
    - try/except 包住 API 调用，失败返回明确错误（参考你 day1 的经验）
    """
    ...

def should_refuse(hits: list[dict], threshold: float = 0.5) -> bool:
    """TODO(V2)：最高相似度低于阈值时拒答。
    阈值不是拍脑袋定的 —— 用 10 个语料外的问题标定，
    记录「阈值取多少时误拒率可接受」。这个实验过程是面试素材。"""
    ...
