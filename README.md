# ai-learning

> 大模型应用开发 · 从 API 调用到 Agent 工程化

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-App%20%2F%20Agent-4B8BBE)
![Status](https://img.shields.io/badge/Status-Learning-success)

这是一个持续更新的学习仓库，记录我从零开始学习**大模型应用开发**的全过程。

目标不是"会调 API"，而是理解背后的原理——Token 与上下文、异步与并发、检索增强、Agent 编排——并能把它们工程化落地。仓库里每个脚本对应一个具体知识点，`notes/` 里是我的理解笔记。

---

## 学习进度

| 阶段 | 日期 | 主题 | 产出 |
|:---:|:---:|:---|:---|
| Day 1 | 10/10 | 大模型 API 调用入门 | 用 curl 与 Python SDK 跑通调用；参数实验（`temperature` / `max_tokens` / `system`） |
| Day 2 | 10/11 | Token 与多轮对话 | Token 换算实验；多轮对话程序（历史维护 + 上下文压缩） |
| Day 3 | 10/12 | Python 异步基础 | 同步串行 vs `asyncio.gather` 并发耗时实测 |

> 每周更新。完整计划：API 调用 → Prompt 工程 → RAG → Agent → 工程化部署。

---

## 目录结构

```
ai-learning/
├── day1-1.py ~ day1-6.py      # Day1：最小调用、temperature / max_tokens / system 实验
├── day2-1.py ~ day2-5.py      # Day2：Token 统计与 temperature 对照实验
├── day2_chat.py               # Day2：多轮对话程序（含上下文滑动窗口裁剪）
├── day2_chat-try.py           # Day2：多轮对话（自写版，含摘要压缩）
├── day3_async_demo.py         # Day3：同步 / 逐个 await / gather 三种方式耗时对比
├── python补课/                 # 基础练习（填空式，自带判分）
│   ├── 练习1-消息列表.py
│   └── 练习2-异步改造.py
├── notes/                     # 学习笔记
│   └── day1-我理解的LLM-API.md
├── env.example                # 环境变量模板
├── requirements.txt
└── .gitignore
```

---

## 快速开始

### 1. 环境要求

- Python 3.10+
- 任意 **OpenAI 兼容**的大模型 API Key（本项目默认使用 DeepSeek）

### 2. 克隆与安装

```bash
git clone https://github.com/17366511351/ai-learning-.git
cd ai-learning-

python -m venv .venv
source .venv/Scripts/activate     # Windows (Git Bash)
# source .venv/bin/activate       # Linux / macOS

pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
cp env.example .env
```

编辑 `.env`，填入你自己的 Key：

```
DEEPSEEK_API_KEY=sk-你的key
```

> ⚠️ `.env` 已被 `.gitignore` 忽略，**永远不会被提交**。

### 4. 运行

```bash
# 最基础：一次 API 调用
python day1-1.py

# 多轮对话（输入 /exit 退出）
python day2_chat.py

# 异步耗时对比（Part 0–2 不需要 Key，可直接看效果）
python day3_async_demo.py
```

---

## 知识点速览

### Token 与上下文窗口

- **模型是无状态的**——它不记得上一句。多轮对话靠客户端维护 `messages` 数组，每轮把全部历史重新发一遍。
- 上下文塞得越满，**中间部分的信息越容易被忽略**（lost in the middle）。所以"把整份文档丢进去"几乎总是错的——这正是需要 RAG 的原因。
- 多轮对话的累计输入量随轮数增长（10 轮 × 200 token ≈ 11000，而单次问答 10 次仅 2000），因此必须做裁剪或摘要压缩。

### 采样参数

- `temperature` 改变分布的**形状**（拉尖 / 压扁）；`top_p` 改变**候选集合**（截断长尾）。两者一次只调一个，否则无法归因。

### 异步与并发

- `async / await` 只是**允许**并发，`asyncio.gather` 才真正并发。只加 `async` 而逐个 `await`，耗时与同步无异。
- 实测（3 个请求）：

  | 写法 | 耗时 |
  |:---|:---:|
  | 同步串行 | 3.00 s |
  | `async` + 逐个 `await` | 3.01 s |
  | `asyncio.gather` | **1.01 s** |

- 判据一句话：**凡是"会等"的操作，都要用异步版本**（`time.sleep` → `await asyncio.sleep`，`OpenAI` → `AsyncOpenAI`）。

### 上下文压缩

- 用 LLM 总结较早的对话，**替换**而非追加，保证 system 长度恒定。
- 注意摘要是有损压缩、**误差会逐轮累积**：摘要的摘要会失真。工业界倾向"摘要只做有限次 + 关键事实单独结构化存储"。

---

## 技术栈

`Python` · `OpenAI SDK` · `python-dotenv` · `asyncio`

---

## 说明

- 本仓库只收录代码与笔记；学习过程中的辅助文档、审阅记录等不纳入公开版本。
- 学习日志会持续更新，欢迎交流。
