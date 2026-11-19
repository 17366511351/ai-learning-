"""建索引脚本 —— 一次性跑：python scripts/build_index.py

TODO(你来做)：串联 ingest → chunking → vectorstore 三个模块。
跑通后 index/ 目录会出现 Chroma 数据，之后 cli 就不需要重建。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config, ingest, chunking, vectorstore  # noqa: E402

def main():
    print("① 解析文档...")
    docs = ingest.load_corpus(config.DATA_DIR)          # TODO: 确认 data/ 里放了语料
    print(f"   共 {len(docs)} 个文档段")

    print("② 切分...")
    chunks = []
    for d in docs:                                       # TODO: V0 用 split_fixed
        chunks.extend(chunking.split_fixed(d, config.CHUNK_SIZE, config.CHUNK_OVERLAP))
    print(f"   共 {len(chunks)} 个 chunk")

    print("③ 向量化入库...")
    # TODO: 加载 embedding 模型，调 vectorstore.build_index(chunks, model)
    # 记录：总耗时、平均每 chunk 耗时

if __name__ == "__main__":
    main()
