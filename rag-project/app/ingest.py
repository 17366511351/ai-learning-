"""文档解析与清洗 —— RAG 的第一座大山，决定整个系统的上限。

把各种格式的原始文档，统一切成 List[Document]：
    {"doc_id": str, "title": str, "section": str, "text": str, "page": int}

V0 只支持 Markdown / PDF / TXT；V1 再加 PPTX。
"""
from pathlib import Path
from pypdf import PdfReader


def clean(text: str) -> str:
    """清洗文本：去噪 → 合并断行 → 压缩空行。顺序不能反。"""
    lines = text.split("\n")

    # 第 1 步：去掉首尾空格；空行先保留（第 3 步统一压缩）
    cleaned = []
    for line in lines:
        s = line.strip()
        if not s:
            cleaned.append("")
            continue
        if len(s) <= 2:          # 1-2 字符的行，大概率是页码 "- 3 -"
            continue
        cleaned.append(s)

    # 第 2 步：合并被硬换行打断的中文句子
    # 判据：上一行结尾不是标点 → 句子没说完，和下一行接上
    merged = []
    END_MARKS = "。！？；：，、）】》.'"
    for line in cleaned:
        if not merged:
            merged.append(line)
            continue
        prev = merged[-1]
        if (prev and prev[-1] not in END_MARKS
                and not line.startswith(("#", "-", ">", "·"))):
            merged[-1] = prev + line
        else:
            merged.append(line)

    # 第 3 步：连续多个空行压成 1 个
    result = []
    blank_count = 0
    for line in merged:
        if line == "":
            blank_count += 1
            if blank_count == 1:
                result.append("")
        else:
            blank_count = 0
            result.append(line)

    return "\n".join(result).strip()


def parse_markdown(path) -> list[dict]:
    """Markdown 按 ## 切分：一个二级标题 = 一个 Document。"""
    path = Path(path)
    title = path.stem
    sections = []

    lines = path.read_text(encoding="utf-8").split("\n")
    current_name = "概述"        # 第一个 ## 之前的内容归入"概述"
    current_lines = []

    for line in lines:
        # 带空格判断，"### 三级标题"不会被误当成 ## 切分
        if line.startswith("## ") and not line.startswith("### "):
            sections.append((current_name, current_lines))
            current_name = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    sections.append((current_name, current_lines))   # 最后一个小节收尾

    docs = []
    for i, (name, body_lines) in enumerate(sections, start=1):
        text = clean("\n".join(body_lines))
        if not text.strip():
            continue
        docs.append({
            "doc_id": f"{title}_S{i}",
            "title": title,
            "section": name,
            "text": text,
            "page": 0,
        })
    return docs


def parse_txt(path) -> list[dict]:
    """纯文本最简单：整个文件当一个 Document。"""
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
    """PDF 按页切分：一页一个 Document。"""
    path = Path(path)
    title = path.stem
    reader = PdfReader(str(path))
    docs = []
    print(f"  正在解析 {title}，共 {len(reader.pages)} 页")

    for i, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""      # or "" 保证返回的是字符串
        if not raw.strip():
            print(f"    [告警] 第 {i} 页无文本（可能是扫描件），跳过")
            continue
        docs.append({
            "doc_id": f"{title}_P{i}",
            "title": title,
            "section": f"第{i}页",
            "text": clean(raw),
            "page": i,
        })
    return docs


def load_corpus(data_dir) -> list[dict]:
    """遍历目录，按扩展名分发给对应 parser，汇总返回。"""
    data_dir = Path(data_dir)
    docs = []
    stats = {}

    # iterdir() 只看这一层，不进子目录 —— pptx-* 子目录暂时不会被读
    for p in sorted(data_dir.iterdir()):
        if p.is_dir():
            continue
        ext = p.suffix.lower()
        if ext == ".md":
            part = parse_markdown(p)
        elif ext == ".pdf":
            part = parse_pdf(p)
        elif ext == ".txt":
            part = parse_txt(p)
        else:
            continue

        docs.extend(part)
        stats[ext] = stats.get(ext, 0) + len(part)

    # 统计必须放在循环外面 —— 这才是对的
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
