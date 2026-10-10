# Git 速查表

写给「刚学会写 Python、第一次用 Git」的自己。忘记命令时翻这一页。

---

## 一、一次性配置（只做一次）

```bash
git config --global user.name  "你的名字"
git config --global user.email "你的邮箱"

# 让中文文件名正常显示，不然会变成 \344\275\240 这种鬼东西
git config --global core.quotepath false
```

查是否配好了：

```bash
git config --global --list
```

---

## 二、把本地代码推上 GitHub（首次建仓）

### 第 1 步：本地建仓库

```bash
cd /d/ai-learning        # 进到项目文件夹
git init -b main         # 初始化，主分支叫 main
git add -A               # 把所有改动放进暂存区
git status --short       # 检查：确认 .env 不在列表里！
git commit -m "day1: 跑通大模型 API 调用"
```

### 第 2 步：GitHub 网页上新建空仓库

1. 打开 https://github.com/new
2. **Repository name** 填 `ai-learning`
3. 选 **Public**（公开，面试官才看得到你的代码）
4. ⚠️ **不要勾选** Add a README / Add .gitignore / Choose a license
   （本地已经有了，勾了会导致第一次推送冲突）
5. 点 Create repository

### 第 3 步：关联并推送

```bash
git remote add origin https://github.com/你的用户名/ai-learning.git
git push -u origin main
```

第一次推送会**弹出浏览器窗口**要求登录 GitHub（Git Credential Manager 自动处理），点授权就行。之后再也不用重复。

### 第 4 步：验证

```bash
git remote -v            # 看远程地址对不对
git log --oneline        # 看提交记录
```

然后刷新 GitHub 页面，代码应该出现了。

---

## 三、日常三步（以后每天都用）

```bash
cd /d/ai-learning
git add -A
git commit -m "day2: 封装多轮对话函数"
git push
```

**提交信息怎么写**：`dayN: 做了什么`。比如 `day3: 实现流式输出`。
写清楚的好处是——12 月回头看这个提交历史，就是你简历上「持续学习能力」的证据。

---

## 四、密钥安全红线

- `.env` 绝不提交。`.gitignore` 里已经有 `.env` 了，**不要删掉那一行**。
- 每次 `git commit` 前扫一眼 `git status --short`，确认没有 `.env`。
- 如果手滑已经推上去了：**立刻去平台控制台作废这把 Key 重新申请**，然后把仓库改回私有或删掉历史。Key 被人扫到，几小时内就可能被刷爆。

---

## 五、常见报错

| 报错 | 原因 | 解决 |
|---|---|---|
| `not a git repository` | 不在项目文件夹里 | `cd /d/ai-learning` 再执行 |
| `remote origin already exists` | 之前加过远程地址了 | `git remote set-url origin <新地址>` |
| `failed to push some refs` / `rejected` | 远程有本地没有的内容 | `git pull --rebase origin main` 再 `git push` |
| `Please tell me who you are` | 没配用户名邮箱 | 回到第一节配置 `user.name` / `user.email` |
| `Authentication failed` | 登录凭证过期 | 命令行执行 `git config --global --unset credential.helper`，重新 push 触发登录 |
| 要求输入密码但输不对 | GitHub 早已不支持密码登录 | 用弹出的浏览器窗口授权；或去 GitHub 生成 Personal Access Token 当密码用 |
| `LF will be replaced by CRLF` | Windows 换行符提示 | **只是警告，不用管** |

---

## 六、查看状态常用命令

```bash
git status               # 现在有哪些改动
git status --short       # 精简版（更常用）
git diff                 # 具体改了什么内容
git log --oneline -10    # 最近 10 条提交
git branch               # 当前在哪个分支
```

---

## 七、后悔药

```bash
git restore 文件名.py     # 撤销某个文件的未提交修改
git restore --staged .   # 把文件从暂存区拿出来（改动还在）
git reset --soft HEAD~1  # 撤销上一次 commit，改动保留
```

⚠️ 别随便用 `git reset --hard`，会**永久丢失**未提交的改动。
