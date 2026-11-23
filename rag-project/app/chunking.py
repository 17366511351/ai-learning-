"""文本切分 —— 把 Document 切成适合向量化的小块（chunk）。

为什么必须切：
  1. Embedding 模型有长度上限（bge 约 512 token），整篇塞进去会被截断；
  2. 一整篇只出一个向量，语义被稀释，检索时"大海捞针"不准；
  3. 切小块后，一次命中只需回传一小段，成本低、引用也精确。

滑动窗口三参数：
  size    窗口大小（每个 chunk 最多多少字）—— config.CHUNK_SIZE = 400
  overlap 相邻窗口重叠多少字——防止一句话被窗口边界拦腰斩断
  step    步长 = size - overlap，即每次窗口往右挪多少字

  例：size=400, overlap=60 → step=340
     窗口1 = text[0:400]，窗口2 = text[340:740]，重叠的那 60 字保证边界句子完整。

数据契约：输入 Document（ingest 产出），输出 chunk 字典，多带一个 chunk_id。
  Document = {"doc_id", "title", "section", "text", "page"}
  chunk    = {"chunk_id", "doc_id", "title", "section", "text", "page"}
"""


def split_fixed(doc: dict, size: int, overlap: int) -> list[dict]:
    """固定长度滑动窗口切分。你这两天改对的 6 个坑都在下面注释里标出来了。"""
    text = doc["text"]
    step = size - overlap            # 步长 = 窗口 − 重叠；overlap 必须 < size，否则 step<=0 死循环
    chunk, start, idx = [], 0, 0     # chunk=结果列表, start=窗口左端, idx=chunk 序号

    # while 而非 for：因为 start 的增量是 step 不是 1，for 不好表达
    while start < len(text):         # ★坑1：条件是 < 不是 <=（<= 会在末尾多切一个空窗口）
        piece = text[start:start + size].strip()   # 切片"含头不含尾"：[start, start+size)
        if len(piece) >= 20:         # ★坑2：用 len(piece) 比长度；直接 piece>=20 是"字符串比整数"报错
            idx += 1                 # ★坑3：先自增再编号，从 _C1 开始（漏这句所有 id 都是 _C0 → Chroma 冲突）
            chunk.append({
                "chunk_id": f"{doc['doc_id']}_C{idx}",  # ★坑4：全局唯一 = 文档id + 序号
                "doc_id": doc["doc_id"],                # ★坑5：doc 是字典用 [] 取值，不是 doc("doc_id")
                "title": doc.get("title", ""),          # get 是方法用 ()；且给默认值防 KeyError
                "section": doc["section"],              # 字段名是 section，不是 session
                "text": piece,
                "page": doc.get("page", 0),             # 有些 Document 没有 page，默认 0
            })
        # ★坑6：break 条件用 start + size >= len(text)——窗口右端越过文本末尾就停。
        # 千万别写成 start + len(chunk) >= ...，len(chunk) 是"攒了几个块"，跟文本长度无关。
        if start + size >= len(text):
            break                    # ★坑7：break 必须真的跳出，漏了会死循环；start += step 必须在 while 内部
        start += step
    return chunk                     # return 与 while 同级（缩进对齐 while），在循环外


def split_recursive(doc: dict, size: int) -> list[dict]:
    """（V1 用）按段落/句子边界递归切分，比硬切更尊重语义，目前尚未实现。

    思路：优先在 \n\n（段落）切，段落还太长就在 。！？（句子）切，
    最后才用 split_fixed 硬切。对比实验时用它和固定切分比命中率。
    V1 做切分策略对比时再来填这个函数的实现。
    """
    pass
