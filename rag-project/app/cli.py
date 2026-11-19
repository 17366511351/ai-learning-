"""命令行入口 —— python -m app.cli "你的问题"

TODO(你来做)：
1. 接收命令行参数作为问题
2. 加载 embedding 模型 → 检索 → 生成 → 打印答案和引用
3. 打印性能数据：检索耗时、生成耗时、token 用量
   —— 这些数字从第一天就要记录，它们是你的简历素材

V2 时在这里加：多轮对话模式（维护 query 历史 + 指代改写）
"""

import sys

def main():
    if len(sys.argv) < 2:
        print("用法: python -m app.cli \"你的问题\"")
        sys.exit(1)
    question = sys.argv[1]

    # TODO 1: 加载 embedding 模型（全局只加载一次）
    # TODO 2: vectorstore.search(question, model, config.TOP_K) 计时
    # TODO 3: generate.answer(question, hits) 计时
    # TODO 4: 打印答案 + 引用列表 + 用时/token

if __name__ == "__main__":
    main()
