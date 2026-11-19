"""向量化与检索 —— Embedding + Chroma。

TODO(你来做)：
1. 选一个本地能跑的中文 embedding 模型（推荐 BAAI/bge-small-zh-v1.5，
   CPU 几分钟就能跑完几百个 chunk；bge-large 效果更好但慢）
2. 用 sentence-transformers 编码，注意 normalize_embeddings=True（配余弦相似度）
3. 写入 Chroma persistent client，落盘到 config.INDEX_DIR
4. 实现 query()：编码 query → top_k 检索 → 返回 chunk + 距离

面试点（做的时候记进笔记）：
- 批量编码 vs 逐条编码的速度差异
- Chroma collection 的 metadata 过滤怎么用
"""

import chromadb

def build_index(chunks: list[dict], embed_model) -> None:
    """TODO: 全量入库。
    - chromadb.PersistentClient(path=config.INDEX_DIR)
    - 先清掉旧 collection（幂等），再批量 add
      —— 注意 Chroma 的 add 要求 id 唯一，用 chunk_id
    - metadata 里存 doc_id / section / page（后面做过滤要用）
    - 打印总耗时和向量数
    """
    ...

def search(query: str, embed_model, top_k: int) -> list[dict]:
    """TODO: 查询。
    - encode query（同样要 normalize）
    - collection.query(query_embeddings=..., n_results=top_k)
    - 返回 [{"text":..., "score": 距离转相似度, "metadata":...}, ...]
    - 距离转相似度：Chroma 默认 L2 或 cosine 距离，确认你用的哪种，换算成 0~1
    """
    ...
