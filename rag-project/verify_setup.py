"""环境验收脚本 —— 从任意目录运行都能用。

原理：脚本把自己的所在目录加入 sys.path，所以无论你在 D:\ 还是哪里敲命令，
from app import config 都能找到 app 包。

用法（任选其一）：
    D:/ai-learning/rag-project/.venv/Scripts/python.exe D:/ai-learning/rag-project/verify_setup.py
    或 cd 进 rag-project 后：.venv/Scripts/python.exe verify_setup.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 60)
print("python 解释器:", sys.executable)
print("当前工作目录:", Path.cwd())
print("项目根目录  :", PROJECT_ROOT)
print("=" * 60)

try:
    from app import config
except ModuleNotFoundError as e:
    name = str(e).replace("No module named ", "").strip("'")
    print(f"\n[失败] 导入失败：{e}")
    if "app" in name:
        print("→ 原因：脚本目录没进 sys.path（不该发生，请贴报错给我）")
    elif "dotenv" in name or "openai" in name:
        print("→ 原因：这个 python 没装依赖。请用 rag-project/.venv/Scripts/python.exe 运行。")
    else:
        print("→ 原因：缺依赖。用 .venv/Scripts/python.exe，或 pip install -r requirements.txt")
    sys.exit(1)

print(f"\n[成功] BASE_DIR  = {config.BASE_DIR}")
print(f"[成功] DATA_DIR  = {config.DATA_DIR}  存在: {config.DATA_DIR.exists()}")
print(f"[成功] API_KEY   = {'已配置' if config.API_KEY else '未配置'}")
print(f"[成功] CHAT_MODEL= {config.CHAT_MODEL}")
print("\n环境验收通过，可以开始写 ingest.py 了。")
