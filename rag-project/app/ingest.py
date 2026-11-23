"""文档解析与清洗 —— RAG 的第一座大山，决定整个系统的上限。

职责：把 data/ 目录里的原始文件（md/pdf/txt）统一解析成 Document 列表。
下游 chunking / vectorstore 全都依赖这个统一的 Document 格式，所以它是数据契约的源头。

Document 就是个 dict，字段固定：
    {"doc_id": str, "title": str, "section": str, "text": str, "page": int}

解析策略：
  - Markdown：按二级标题 ## 切成一节一个 Document（最干净的语料）
  - PDF：pypdf 逐页提取，一页一个 Document；扫描件提取为空 → 告警跳过
  - TXT：整篇一个 Document

清洗的难点（clean 函数三段）：中文没有空格，PDF 复制出来常被硬换行切断，
  判断依据"行尾没有标点 → 大概率是被截断的句子 → 和下一行拼接"。
"""
from pathlib import Path
from pypdf import PdfReader


def clean(text: str) -> str:
    """清洗文本：去短行噪音 → 合并中文断行 → 压缩连续空行。"""
    # ---- 第一段：逐行 strip，丢掉太短的行（页眉页脚/孤立字符），保留空行占位 ----
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        s = line.strip()
        if not s:
            cleaned.append("")            # 空行先留着，第三段统一压缩
            continue
        if len(s) <= 2:                    # 1-2 个字符多是页码、页眉残留，丢掉
            continue
        cleaned.append(s)

    # ---- 第二段：合并被硬换行打断的句子 ----
    # 判定：上一行结尾不是句号等结束标点，且当前行不是新段落标记（#、-、>、·）→ 认为是断行，拼上去
    merged = []
    END_MARKS = "。！？；：，、）】》.'"
    for line in cleaned:
        if not merged:
            merged.append(line)
            continue
        prev = merged[-1]
        if (prev and prev[-1] not in END_MARKS
                and not line.startswith(("#", "-", ">", "·"))):
            merged[-1] = prev + line       # 直接拼接，中文断行不需要补空格
        else:
            merged.append(line)

    # ---- 第三段：连续多个空行压成一个，避免浪费上下文窗口 ----
    result = []
    blank_count = 0
    for line in merged:
        if line == "":
            blank_count += 1
            if blank_count == 1:           # 只在第一个空行时保留
                result.append("")
        else:
            blank_count = 0                # 遇到非空行，计数归零
            result.append(line)

    return "\n".join(result).strip()


def parse_markdown(path) -> list[dict]:
    """按 ## 二级标题切分，每个 section 一个 Document；### 及以下不切（避免切太碎）。"""
    path = Path(path)
    title = path.stem                      # 文件名（不含扩展名）作为 title
    sections = []

    lines = path.read_text(encoding="utf-8").split("\n")
    current_name = "概述"                  # 第一个 ## 之前的引言归到"概述"
    current_lines = []

    for line in lines:
        # 只认 "## " 开头且不认 "### "（否则 ### 也会命中 ## —— 这是个经典坑）
        if line.startswith("## ") and not line.startswith("### "):
            sections.append((current_name, current_lines))   # 上一节收尾
            current_name = line[3:].strip()                  # 标题文字（去掉 "## "）
            current_lines = []
        else:
            current_lines.append(line)
    sections.append((current_name, current_lines))           # 最后一节收尾

    docs = []
    for i, (name, body_lines) in enumerate(sections, start=1):
        text = clean("\n".join(body_lines))
        if not text.strip():               # 空的 section 跳过，不产生空 Document
            continue
        docs.append({
            "doc_id": f"{title}_S{i}",     # 文档内唯一：文件名 + 节号
            "title": title,
            "section": name,
            "text": text,
            "page": 0,                     # Markdown 没有页码概念，统一填 0
        })
    return docs


def parse_txt(path) -> list[dict]:
    """纯文本：整篇一个 Document，不做 section 切分。"""
    path = Path(path)
    text = clean(path.read_text(encoding="utf-8"))
    if not text:
        return []
    return [{
        "doc_id": path.stem,
        "title": path.stem,
        "section": "正文",
        "text": text,
        "page": 0,
    }]


def parse_pdf(path) -> list[dict]:
    """PDF：pypdf 逐页提取，一页一个 Document；扫描件无文本时跳过。"""
    path = Path(path)
    title = path.stem
    reader = PdfReader(str(path))
    docs = []
    print(f"  正在解析 {title}，共 {len(reader.pages)} 页")

    for i, page in enumerate(reader.pages, start=1):         # 页码从 1 开始
        raw = page.extract_text() or ""       # 扫描件/图片页返回 None → 用 "" 兜底
        if not raw.strip():
            print(f"    [告警] 第 {i} 页无文本（可能是扫描件），跳过")
            continue                          # 空页不产生 Document，否则后面全是空向量
        docs.append({
            "doc_id": f"{title}_P{i}",        # 文档内唯一：文件名 + 页码
            "title": title,
            "section": f"第{i}页",
            "text": clean(raw),
            "page": i,
        })
    return docs


def load_corpus(data_dir) -> list[dict]:
    """遍历 data_dir 根目录，按扩展名分发到对应 parser，汇总返回。

    注意：只遍历根目录（iterdir 不递归），data/ 下的 pptx-* 子目录不会被读；
    也只认 .md/.pdf/.txt，其他格式（如 pptx）会被忽略。这正是"换数据"时要牢记的两点。
    """
    data_dir = Path(data_dir)
    docs = []
    stats = {}

    for p in sorted(data_dir.iterdir()):      # sorted 保证顺序稳定，结果可复现
        if p.is_dir():                         # 子目录直接跳过，不递归
            continue
        ext = p.suffix.lower()                 # 统一转小写，.MD 也能识别
        if ext == ".md":
            part = parse_markdown(p)
        elif ext == ".pdf":
            part = parse_pdf(p)
        elif ext == ".txt":
            part = parse_txt(p)
        else:
            continue                           # 其他格式忽略（如 .pptx 读不了）

        docs.extend(part)                      # ★ extend 把列表摊开加入；append 会变成嵌套列表
        stats[ext] = stats.get(ext, 0) + len(part)

    empty = sum(1 for d in docs if not d["text"].strip())
    print("\n========== 语料统计 ==========")
    print(f"总 Document 数: {len(docs)}")
    for ext, n in stats.items():
        print(f"  {ext}: {n} 个 Document")
    print(f"  空文本 Document: {empty}")
    return docs


if __name__ == "__main__":
    DATA = Path("D:/ai-learning/rag-project/data")
    all_docs = load_corpus(DATA)

    print("\n========== 抽样看前 3 个 Document ==========")
    for d in all_docs[:3]:
        print(f"\n[{d['doc_id']}] section={d['section']} page={d['page']}")
        print(f"  正文前 80 字: {d['text'][:80]}")
