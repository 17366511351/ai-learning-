"""文档解析与清洗 —— RAG 的第一座大山，决定整个系统的上限。

TODO(你来做)：
1. 实现 parse_pdf / parse_md / parse_txt，统一输出 List[Document]
2. 清洗：去页眉页脚、合并断行（中文别在标点前断）、去连续空行
3. V0 只要求 PDF + Markdown 两种；PDF 用 pypdf 起步，
   如果发现表格/多栏还原很差，再换 pdfplumber 对比（这就是你的踩坑素材）

Document 就是个 dict，字段固定，后续模块都依赖它：
    {"doc_id": str, "title": str, "section": str, "text": str, "page": int}
"""

def parse_pdf(path) -> list[dict]:
    """TODO: 逐页提取文本。要点：
    - pypdf 的 extract_text() 对扫描件返回空串 —— 检查并跳过/告警
    - 每页一个 Document，page 记页码
    """
    ...

def parse_markdown(path) -> list[dict]:
    """TODO: 按标题(##)切 section，标题进 section 字段。
    Markdown 是最干净的语料，先把它做对，再啃 PDF。"""
    ...

def clean(text: str) -> str:
    """TODO: 清洗函数。
    - 去掉重复出现的页眉页脚（观察你的语料，它们长什么样）
    - 合并被硬换行打断的句子（中文行尾无标点 → 大概率是断行）
    - 连续 3 个以上空行压成 1 个
    """
    ...

def load_corpus(data_dir) -> list[dict]:
    """TODO: 遍历 data_dir，按扩展名分发到对应 parser，汇总返回。
    统计并打印：总数、各类型数量、空文本数量。"""
    ...
