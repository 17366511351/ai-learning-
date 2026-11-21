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
from app import config

def build_index(chunks: list[dict], embed_model) -> None:
    """TODO: 全量入库。
    - chromadb.PersistentClient(path=config.INDEX_DIR)
    - 先清掉旧 collection（幂等），再批量 add
      —— 注意 Chroma 的 add 要求 id 唯一，用 chunk_id
    - metadata 里存 doc_id / section / page（后面做过滤要用）
    - 打印总耗时和向量数
    """
    client = chromadb.PersistentClient(path=str(config.INDEX_DIR))
    try:
        client.delete_collection("rag_v0")
    except Exception:
        pass
    col = client.create_collection("rag_v0", metadata={"hnsw:space": "cosine"})
    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [{"doc_id": c["doc_id"], "section": c["section"],
                  "page": c["page"], "title": c["title"]} for c in chunks]
    vectors = embed_model.encode(texts, normalize_embeddings=True, batch_size=64).tolist()
    col.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas)
    print(f"写入完成：{col.count()} 条向量 -> {config.INDEX_DIR}")

def search(query: str, embed_model, top_k: int) -> list[dict]:
    """TODO: 查询。
    - encode query（同样要 normalize）
    - collection.query(query_embeddings=..., n_results=top_k)
    - 返回 [{"text":..., "score": 距离转相似度, "metadata":...}, ...]
    - 距离转相似度：Chroma 默认 L2 或 cosine 距离，确认你用的哪种，换算成 0~1
    """
    client = chromadb.PersistentClient(path=str(config.INDEX_DIR))
    col = client.get_collection("rag_v0")
    qv = embed_model.encode([query], normalize_embeddings=True).tolist()
    res = col.query(query_embeddings=qv, n_results=top_k)
    out = []
    for text, dist, meta in zip(res["documents"][0],
                                res["distances"][0],
                                res["metadatas"][0]):
        out.append({"text": text, "score": 1 - dist, "metadata": meta})
    return out
        
