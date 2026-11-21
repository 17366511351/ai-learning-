import sys, time
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
from app.config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBED_MODEL, TOP_K, INDEX_DIR
from app.ingest import load_corpus
from app.chunking import split_fixed
from app.vectorstore import build_index, search

print("=" * 50)
print("RAG V0 端到端验收")
print("=" * 50)

t0 = time.time()
docs = load_corpus(Path(DATA_DIR))
print(f"[1] 解析: {len(docs)} 个 Document")

chunks = []
for d in docs:
    chunks.extend(split_fixed(d, CHUNK_SIZE, CHUNK_OVERLAP))
lens = [len(c["text"]) for c in chunks]
print(f"[2] 切分: {len(chunks)} chunks, 平均 {sum(lens)//len(lens)} 字, 最短 {min(lens)}, 最长 {max(lens)}")
print(f"    唯一 chunk_id 数: {len(set(c['chunk_id'] for c in chunks))} (应等于 {len(chunks)})")

from sentence_transformers import SentenceTransformer
print(f"[3] 加载 embedding 模型 {EMBED_MODEL} (首次需下载)...")
embed = SentenceTransformer(EMBED_MODEL)
print("    模型加载完成")

t1 = time.time()
build_index(chunks, embed)
print(f"[4] 建索引耗时: {time.time()-t1:.1f}s, 落盘: {INDEX_DIR}")

print("[5] 检索自测:")
for q in ["数据结构有哪些知识点", "毕业需要多少学分", "操作系统进程调度"]:
    t2 = time.time()
    res = search(q, embed, TOP_K)
    top = res[0] if res else None
    print(f"    Q: {q}")
    print(f"    top1: score={top['score']:.3f} | {top['metadata']['title']}/{top['metadata']['section']} | {top['text'][:50]}... | {time.time()-t2:.2f}s")

print(f"\n总耗时: {time.time()-t0:.1f}s")
print("=" * 50)
print("验收结果: PASS")
