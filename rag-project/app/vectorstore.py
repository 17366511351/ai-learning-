"""向量库 —— 把 chunk 变成向量存进 Chroma，并按语义相似度检索。

什么是向量检索：
  文本 → Embedding 模型 → 一串数字（向量）→ 存进数据库。
  查询时把问题也变成向量，找和它"方向最接近"的那些向量，就是把语义最相关的 chunk 找出来。
  这个"方向接近"用余弦相似度衡量，所以建库时用 cosine 距离。

Chroma 的核心概念（类比 SQL 更好懂）：
  collection（集合） ≈ 一张表
  id      ≈ 主键，全局唯一（就是 chunk_id）
  embedding ≈ 向量列
  document ≈ 原文
  metadata ≈ 附带的标签（title/section/page），用于回填引用来源

用户踩过的坑（下面逐处标注）：复数 s、方法用圆括号、局部变量不共享、归一化两边一致。
"""
import chromadb
from app import config


def build_index(chunks: list[dict], embed_model) -> None:
    """建索引：把 chunks 编码成向量，整体覆盖写入 Chroma 的 rag_v0 集合。

    幂等设计：先 delete 再 create，所以重复跑不会越积越多（这是数据库"幂等"思想的体现）。
    """
    client = chromadb.PersistentClient(path=str(config.INDEX_DIR))  # 方法用 ()，path 是关键字参数；Path 要 str() 转一下
    try:
        client.delete_collection("rag_v0")   # ★ 方法名是 delete_collection（下划线，不是点）
    except Exception:
        pass                                  # 第一次建库时集合不存在，删除会报错，忽略即可
    col = client.create_collection("rag_v0", metadata={"hnsw:space": "cosine"})
    # hnsw:space=cosine 指定用余弦距离；HNSW 是底层近似最近邻索引算法，空间换时间

    # 三个平行列表：ids / texts / metadatas 顺序一一对应，Chroma 按位置配对写入
    ids = [c["chunk_id"] for c in chunks]      # ★ 变量名是 chunks（复数），不是 chunk
    texts = [c["text"] for c in chunks]
    metadatas = [{"doc_id": c["doc_id"], "section": c["section"],
                  "page": c["page"], "title": c["title"]} for c in chunks]

    # 批量编码：一次传整批文本比一条条 encode 快得多；normalize_embeddings=True 把向量归一化成单位向量
    vectors = embed_model.encode(texts, normalize_embeddings=True, batch_size=64).tolist()
    # .tolist()：numpy 数组 → Python list，Chroma 才认
    col.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas)
    print(f"写入完成：{col.count()} 条向量 -> {config.INDEX_DIR}")


def search(query: str, embed_model, top_k: int) -> list[dict]:
    """检索：把 query 编码成向量，查出最相似的 top_k 个 chunk。

    返回 [{"text", "score", "metadata"}]，score 越大越相关。
    """
    # ★ 每个函数里的 client 是局部变量，build_index 里建的同名变量在这里用不了，必须重新建
    client = chromadb.PersistentClient(path=str(config.INDEX_DIR))
    col = client.get_collection("rag_v0")      # ★ 方法名 get_collection（下划线）

    # ★ 查询也要 normalize_embeddings=True，必须和入库时一致，否则余弦算出来是错的
    qv = embed_model.encode([query], normalize_embeddings=True).tolist()
    # ★ 参数是 query_embeddings（复数），传的是向量列表 [query] 不是字符串
    res = col.query(query_embeddings=qv, n_results=top_k)

    out = []                                   # ★ 先建空列表，下面 append 才不会 NameError
    # zip 把三列并排走：原文 / 距离 / 元信息
    for text, dist, meta in zip(res["documents"][0],
                                res["distances"][0],   # ★ 是 distances（复数），结果也是嵌套列表 [0] 取第一条查询
                                res["metadatas"][0]):
        # Chroma 返回的是"距离"（越小越近），转成"相似度"（越大越近）：score = 1 - dist
        out.append({"text": text, "score": 1 - dist, "metadata": meta})
    return out                                 # ★ 别忘了 return，否则调用方拿到 None
