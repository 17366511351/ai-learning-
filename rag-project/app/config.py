"""配置模块 —— 所有可变的东西集中在这里，不硬编码。

设计思想：整个项目只有这一个地方放"会变的值"（密钥、模型名、路径、参数）。
  好处：换模型/调参数只改这一处；项目和具体机器解耦，拷到别处也能跑。
  __file__ 是当前文件路径，resolve() 转成绝对路径，parent.parent 上两级 = 项目根 —— 这样无论从哪个目录启动都能找到 data/ 和 index/。
"""
import os
from pathlib import Path
from dotenv import load_dotenv
# 项目根目录 = app/ 的上一级
BASE_DIR = Path(__file__).resolve().parent.parent

# ---- TODO 1: 模型配置 ----
load_dotenv(BASE_DIR / ".env")
API_KEY = os.environ.get("DEEPSEEK_API_KEY") # 从环境变量读 DEEPSEEK_API_KEY
if not API_KEY:
    raise ValueError("请在 rag-project/.env 中配置 DEEPSEEK_API_KEY，模板见 env.example")
BASE_URL = "https://api.deepseek.com"
CHAT_MODEL = "deepseek-flash"

# ---- TODO 2: embedding 模型（V0 先用 bge-small-zh-v1.5，CPU 能跑）----
EMBED_MODEL = "BAAI/bge-small-zh-v1.5"  # 形如 "BAAI/bge-small-zh-v1.5"

# ---- TODO 3: 路径 ----
DATA_DIR = BASE_DIR / "data"          # 原始文档放这里
INDEX_DIR = BASE_DIR / "index"        # Chroma 持久化目录

# ---- TODO 4: 切分参数（V1 时你会做对比实验，先给默认值）----
# size=400 字约等于 250-300 个中文 token，留足空间给 prompt 和答案；
# overlap=60（15%）防止句子被窗口边界截断。step = size-overlap = 340。
# V1 的量化实验就是拿 256/512/1024 和不同 overlap 跑同一份评测集对比命中率。
CHUNK_SIZE = 400
CHUNK_OVERLAP = 60

# ---- TODO 5: 检索参数 ----
# top_k=5：召回 5 个 chunk 拼进上下文。太小会漏，太大引入噪音且烧 token（"lost in the middle"）。
# V1 会做 top_k=3/5/10 的对比实验。
TOP_K = 5
