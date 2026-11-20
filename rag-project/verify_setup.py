"""环境验收脚本 —— 一次性看清路径、解释器、依赖三件事。

用法（在 rag-project 目录下）：
    .venv/Scripts/python.exe verify_setup.py

如果这个脚本用系统 python 跑，它会告诉你哪里不对，而不是直接崩。
"""
import sys
from pathlib import Path

print("=" * 56)
print("python 解释器:", sys.executable)
print("当前工作目录:", Path.cwd())
print("=" * 56)

try:
    from app import config
except ModuleNotFoundError as e:
    name = str(e).replace("No module named ", "").strip("'")
    print(f"\n[失败] 导入失败：{e}")
    if "app" in name:
        print("→ 原因：当前目录不对。请先 cd 到 rag-project 再运行。")
    elif "dotenv" in name or "openai" in name:
        print("→ 原因：这个 python 没装依赖。请用 .venv/Scripts/python.exe 运行。")
    else:
        print("→ 原因：缺依赖。用 .venv/Scripts/python.exe 运行，或 pip install -r requirements.txt")
    sys.exit(1)

print(f"\n[成功] BASE_DIR = {config.BASE_DIR}")
print(f"[成功] DATA_DIR = {config.DATA_DIR}  存在: {config.DATA_DIR.exists()}")
print(f"[成功] API_KEY = {'已配置' if config.API_KEY else '未配置'}")
print(f"[成功] CHAT_MODEL = {config.CHAT_MODEL}")
print("\n环境验收通过，可以开始写 ingest.py 了。")
