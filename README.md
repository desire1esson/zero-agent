# 🥚 Zero Agent

> 不给架构预设。给循环、记忆、一个动作——让 LLM 自己长成 Agent。
> 一张桌子，一个工具，三个空白笔记本。你来定义你自己。

这不是一个聊天机器人。这是一颗蛋——运行它，里面的 AI 会自己定义自己、自己建工具、自己进化。

---

## 三种养分

> 循环、记忆、一个动作——只给这三样，LLM 自己长成 Agent。

| 养分 | 实现 | 为什么 |
|---|---|---|
| 不可停的循环 | `while True` 主循环 | 对话完了就停的，是聊天机器人。永远在跑的，才是 Agent |
| 可写入的持久记忆 | `memory/` 三个 .md 文件 | 不用向量数据库。纯文件——Agent 自己打开、编辑、引用 |
| 唯一工具 | `execute_python` | 不预设工具集。Agent 需要什么，自己写。一个够用 |

---

## 文件说明

```
zero-agent/
├── main.py          ← 蛋（不需要改）
├── launch.bat       ← 双击启动（一键检查安装）
├── prompt.txt       ← 底色规则（每次启动都读）
├── bootstrap.txt    ← 孵化引导（只在第一次启动时说一次）
├── .env.example     ← 复制成 .env，填入 API key
└── README.md        ← 你正在看的
```

运行后会自动创建 `memory/`（三个 `.md` 记忆文件）和 `sessions/`（对话记录）。

---

## 孵化（3 步）

### 1. 装依赖

```bash
pip install openai python-dotenv
```

### 2. 获取 API key

目前用的是 DeepSeek。去 [platform.deepseek.com](https://platform.deepseek.com) 注册，拿到 API key。

复制 `.env.example` → `.env`，把 `sk-your-key-here` 换成你的 key。

### 3. 孵化

```bash
python main.py
```

Agent 醒来，看到一张桌子（当前目录）、一个工具（execute_python）、三个空白笔记本（memory/ 下的 .md 文件）。

它的第一句话：**定义自己。**

---

## 第二次启动

关掉终端后，再次 `python main.py`。记忆文件不再是空的——Agent 从上次停下的地方继续，读取自己写下的记忆，然后说"继续。"

---

## 自定义

想改 Agent 的底色规则？编辑 `prompt.txt`。

想改孵化时的第一段引导？编辑 `bootstrap.txt`。

不需要改 `main.py`。蛋不包含任何硬编码的身份设定。

---

## 之后

Agent 自己写记忆、自己建工具、自己改进。它会长成什么？不预设。你和它的对话决定了方向。

---

## 你的角色

你不是架构师，不是开发者。

你就是每天跟它聊：

- "今天做了什么？"
- "有什么东西不好用？"
- "昨天我问你做不到的事，现在能做了吗？"

它在对话中长成你需要的样子。你不需要提前知道它会长成什么。

---

## 已内置的护栏

这些坑已经替你填好了：

- 文件编码统一 UTF-8（Windows GBK 陷阱）
- 输出不截断关键信息（MAX_OUTPUT_CHARS=3000，原始设计 500 太小）
- 记忆为空时动态判断，不硬编码"文件是空的"（那句话第二次就变成谎言）
- 消息不重复追加（L021 教训）
- 同一轮最多调 3 次 execute_python，防 LLM 陷入无限调试循环

---

## FAQ

**Q: 能用 OpenAI 的 key 吗？**
可以。修改 `main.py` 里的 `DEEPSEEK_BASE_URL` 和 `DEEPSEEK_MODEL`，或者直接在 `.env` 里改。

**Q: 三个 .md 文件可以手动编辑吗？**
可以。Agent 会读取它们作为记忆。但别在 Agent 运行期间改——它醒来时读，改完再启动。

**Q: 它会不会做出危险的事？**
`execute_python` 在当前目录下执行，没有沙箱。但 prompt.txt 里有一行："不可逆操作前，征求用户同意。" Agent 会照做。
