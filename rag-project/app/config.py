"""配置模块 —— 所有可变的东西集中在这里，不硬编码。

TODO(你来做)：
1. 用 pydantic-settings（或纯 os.environ）读取以下配置
2. 缺 DEEPSEEK_API_KEY 时抛出带人话指引的报错，不要让 KeyError 裸奔
3. 注意：路径都基于本文件位置推导（pathlib），保证换目录也能跑
"""
from pathlib import Path

# 项目根目录 = app/ 的上一级
BASE_DIR = Path(__file__).resolve().parent.parent

# ---- TODO 1: 模型配置 ----
API_KEY = ...        # 从环境变量读 DEEPSEEK_API_KEY
BASE_URL = "https://api.deepseek.com"
CHAT_MODEL = "deepseek-flash"

# ---- TODO 2: embedding 模型（V0 先用 bge-small-zh-v1.5，CPU 能跑）----
EMBED_MODEL = ...    # 形如 "BAAI/bge-small-zh-v1.5"

# ---- TODO 3: 路径 ----
DATA_DIR = BASE_DIR / "data"          # 原始文档放这里
INDEX_DIR = BASE_DIR / "index"        # Chroma 持久化目录

# ---- TODO 4: 切分参数（V1 时你会做对比实验，先给默认值）----
CHUNK_SIZE = 400
CHUNK_OVERLAP = 60

# ---- TODO 5: 检索参数 ----
TOP_K = 5
