# ============================================================
# 练习 1 · 消息列表操作（不需要调用 API，纯 Python 练习）
# ============================================================
#
# 目的：把"追加、取值、长度、遍历"练成肌肉记忆。
# 因为多轮对话的 90% 就是在操作这个列表。
#
# 用法：每个 TODO 下面写你的代码，然后运行 python 练习1-消息列表.py
#       看到所有"✅"就算过关。

messages = []


# ---------- TODO 1：往列表里加一条 user 消息 ----------
# 要求：往 messages 末尾加 {"role": "user", "content": "你好"}
# 提示：messages.append(...)
# 你的代码 ↓




# 检查 1（不要改）
assert len(messages) == 1, "❌ messages 应该有 1 条"
assert messages[0]["role"] == "user", "❌ 角色应该是 user"
print("✅ 检查 1 通过：列表里有 1 条 user 消息")


# ---------- TODO 2：再加一条 assistant 消息 ----------
# 要求：加 {"role": "assistant", "content": "你好，有什么可以帮你？"}
# 你的代码 ↓




# 检查 2
assert len(messages) == 2, "❌ messages 应该有 2 条"
print("✅ 检查 2 通过：现在有 2 条消息")


# ---------- TODO 3：取最后一条消息的内容 ----------
# 要求：把最后一条消息的 content 存进 last_content 变量
# 提示：messages[-1] 是最后一条，它是个字典，再用 ["content"] 取值
# 你的代码 ↓




# 检查 3
assert last_content == "你好，有什么可以帮你？", f"❌ 取到的是：{last_content}"
print("✅ 检查 3 通过：成功取到最后一条内容")


# ---------- TODO 4：用一个循环打印所有消息 ----------
# 要求：格式是   [0] user: 你好
# 提示：for i, m in enumerate(messages):  然后 f-string
# 你的代码 ↓




# 检查 4（人工看，没有 assert）
print("✅ 检查 4：上面应该有两行，编号 0 和 1，角色分别是 user 和 assistant")


# ---------- TODO 5（进阶）：删掉最后一条，再打印长度 ----------
# 要求：用 pop() 删掉最后一条，然后打印剩下的条数
# 你的代码 ↓




# 检查 5
assert len(messages) == 1, "❌ 删除后应该剩 1 条"
print("✅ 检查 5 通过：pop 成功")


print()
print("=" * 50)
print("🎉 全部通过！你已经掌握了多轮对话需要的列表操作。")
print("   下一步：打开 02-从单次到多轮对话.py 跑一遍。")
print("=" * 50)
