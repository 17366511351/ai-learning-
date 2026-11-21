"""切分模块 —— RAG 里性价比最高的优化点。

TODO(你来做)：
1. 实现 split_fixed：固定长度 + overlap（V0 用它先跑通）
2. 实现 split_recursive：按 段落(\\n\\n) → 句子(。！？) → 字符 三级递归
   （V1 做对比实验时用）
3. 每个 chunk 保留来源信息：doc_id / section / parent 索引
   —— V1 做 Parent-Child 时会感谢现在的你

两个函数都返回 List[dict]：
    {"chunk_id": str, "doc_id": str, "text": str, "page": int, ...}
"""

def split_fixed(doc: dict, size: int, overlap: int) -> list[dict]:
    """TODO: 滑动窗口切分。
    - 用字符为单位（中文场景比 token 简单直观）
    - 相邻窗口重叠 overlap 个字符，保证边界句子不丢
    - 注意：别把一个 chunk 切得只剩标点 —— 过滤长度 < 20 的碎片
    """
    text = doc["text"]
    step = size - overlap
    chunk,start,idx = [],0,0
    while start < len(text):
        piece = text[start:start +size].strip()
        if len(piece) >=20:
            idx += 1
            chunk.append({
                "chunk_id":f"{doc['doc_id']}_C{idx}",
                "doc_id":doc["doc_id"],
                "title":doc.get("title",""),
                "section":doc["section"],
                "text":piece,
                "page":doc.get("page",0),
            })
        if start + size>= len(text):
            break
        start += step
    return chunk
def split_recursive(doc: dict, size: int) -> list[dict]:
    """TODO(V1)：优先按段落切；段落超长再按句子切；句子超长才硬切。
    这是 LangChain RecursiveCharacterTextSplitter 的思路，
    但你要自己写一遍 —— 面试说「我手写过递归切分」比「我调过 LangChain」值钱。"""
    ...
