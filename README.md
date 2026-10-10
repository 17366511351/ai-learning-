# ai-learning

AI 应用 / Agent 开发方向的学习代码库。
2026-10-10 开始，目标：2027 春招拿下 AI 应用开发岗 offer。

## 进度

### Day 1 · 10/10　跑通大模型 API 调用

| 文件 | 实验内容 | 结论 |
|---|---|---|
| `day1-1.py` | 最小可运行调用 | 一次调用 = 一次 HTTPS POST，核心是 `choices[0].message.content` |
| `day1-2.py` | 解剖响应对象 | `finish_reason` 判断是否被截断，`usage` 决定成本 |
| `day1-3.py` | `temperature=0.0` | 输出几乎每次一致，适合抽取 / 分类 |
| `day1-4.py` | `temperature=1.5` | 输出每次不同，适合创意发散 |
| `day1-5.py` | `max_tokens=20` | 长回答被截断，`finish_reason` 变为 `length` |
| `day1-6.py` | system 提示词约束 | 用 system 强制输出格式，模型被显著约束住 |
| `day1_api_demo.py` | 综合示例（4 个 Part） | 调用、响应解剖、参数实验、多轮对话 |

## 环境准备

```bash
# 1. 虚拟环境
python -m venv .venv
source .venv/Scripts/activate      # Git Bash
# .venv\Scripts\activate.bat       # CMD
# .venv\Scripts\Activate.ps1       # PowerShell

# 2. 装依赖
python -m pip install openai python-dotenv
```

## 配置密钥

```bash
cp env.example .env
# 然后编辑 .env，填入自己的 API Key
```

`.env` 已在 `.gitignore` 里，不会被提交。

## 运行

```bash
python day1-1.py
```

## 日常工作流

```bash
git add -A
git commit -m "day2: 多轮对话封装"
git push
```

完整的 Git 命令与常见报错见 `Git速查表.md`。
