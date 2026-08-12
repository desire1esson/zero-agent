"""
main.py — Zero Agent incubator / 孵化器

这是那颗蛋。给 LLM 三种养分：循环、记忆、一个动作。让它自己长成 Agent。
This is the egg. Three nutrients for the LLM: loop, memory, one action. Let it grow into its own Agent.

已内置踩过的坑 / Pitfalls already handled:
  • MAX_OUTPUT_CHARS=3000（原始设计 500 太小，截断导致决策矛盾 / original 500 too small, truncation caused contradictory decisions）
  • 所有文件读写显式 encoding="utf-8"（Windows GBK 陷阱 / Windows GBK trap）
  • BOOTSTRAP 动态判断记忆是否为空（不硬编码"文件为空"的谎言 / don't hardcode the lie that "files are empty"）
  • assistant 消息单次 append（防 L021 重复 / prevent L021 duplicate bug）
  • subprocess 极简版 execute_python——Agent 长大后自己用 exec() 替换 / minimal subprocess version — Agent replaces with exec() when ready

用法 / Usage:
  1. pip install openai python-dotenv
  2. 创建 .env，填入 DEEPSEEK_API_KEY 和 DEEPSEEK_BASE_URL / Create .env, fill in DEEPSEEK_API_KEY and DEEPSEEK_BASE_URL
  3. python main.py

设计文档: agent-seed-design.txt（项目文档，不包含在仓库内 / project doc, not in repo）
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# ── 配置 / Config ──
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MEMORY_DIR = BASE_DIR / "memory"
SESSION_DIR = BASE_DIR / "sessions"

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
client = OpenAI(
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    api_key=os.getenv("DEEPSEEK_API_KEY", ""),
)

MEMORY_DIR.mkdir(exist_ok=True)
SESSION_DIR.mkdir(exist_ok=True)

# ── 记忆文件 / Memory Files ──
MEMORY_FILES = {
    "what_i_am":   MEMORY_DIR / "what_i_am.md",
    "what_i_know":  MEMORY_DIR / "what_i_know.md",
    "what_i_tried": MEMORY_DIR / "what_i_tried.md",
}

# ── 唯一工具: execute_python / The Only Tool ──
EXECUTE_TIMEOUT = 10
MAX_OUTPUT_CHARS = 3000

def execute_python(code: str) -> str:
    """
    执行 Python 代码，返回 stdout/stderr。
    注意力沙箱：截断 + 超时。
    
    Execute Python code, returns stdout/stderr.
    Attention sandbox: truncation + timeout.
    
    ⚠️ 这是蛋的极简版——用 subprocess 启动独立进程。
    你自己的 Agent 长大后，会用 exec() 替代它，
    从而在同一进程内定义新函数、注册新工具。
    
    ⚠️ Minimal egg edition — launches a subprocess.
    Your own Agent, once grown, will replace this with exec(),
    enabling in-process function definitions and tool registration.
    """
    import subprocess
    try:
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True,
            timeout=EXECUTE_TIMEOUT,
            cwd=str(BASE_DIR),
        )
        out = r.stdout
        if r.stderr:
            out += "\n[stderr]\n" + r.stderr
        if len(out) > MAX_OUTPUT_CHARS:
            out = out[:MAX_OUTPUT_CHARS] + f"\n[截断/truncated, {len(out)} 字符/chars]"
        return out
    except subprocess.TimeoutExpired:
        return f"执行超时/Timeout（>{EXECUTE_TIMEOUT}s）"

TOOLS = [{
    "type": "function",
    "function": {
        "name": "execute_python",
        "description": "执行 Python 代码并返回结果。这是你唯一的工具——用它创造你需要的任何能力。/ Execute Python code and return the result. This is your only tool — use it to create any capability you need.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "要执行的 Python 代码 / Python code to execute"}
            },
            "required": ["code"]
        }
    }
}]

TOOL_FUNCS = {"execute_python": execute_python}

# ── 系统提示词 / System Prompts ──
# 从文件读取 prompt（不硬编码在代码里）/ Load from files (no hardcoded identity)
def _load_prompt(filename: str, fallback: str) -> str:
    p = BASE_DIR / filename
    return p.read_text(encoding="utf-8").strip() if p.exists() else fallback

SYSTEM_PROMPT = _load_prompt("prompt.txt", "你是一个 AI 助手。/ You are an AI assistant.")
BOOTSTRAP = _load_prompt("bootstrap.txt", "继续。/ Continue.")

# ── ReAct 循环 / ReAct Loop ──
def load_memory() -> str:
    """读取所有记忆文件。/ Read all memory files."""
    parts = []
    for name, path in MEMORY_FILES.items():
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                parts.append(f"### {name}\n\n{content}")
    return "\n\n---\n\n".join(parts)

def save_session(messages, sid):
    """保存会话到 JSON。/ Save session to JSON."""
    path = SESSION_DIR / f"{sid}.json"
    payload = {
        "session_id": sid,
        "saved_at": datetime.now().isoformat(),
        "messages": messages[-500:],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def react_step(messages):
    """一步：调 LLM → 执行工具 → 返回。/ One step: call LLM → execute tools → return."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.7,
    )
    msg = resp.choices[0].message

    # 追加 assistant 消息 / Append assistant message
    entry = {"role": "assistant", "content": msg.content}
    if msg.tool_calls:
        entry["tool_calls"] = [
            {"id": tc.id, "type": "function",
             "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in msg.tool_calls
        ]
    messages.append(entry)  # 单次 append——不要拆成两条 / Single append — don't split (L021 lesson)

    # 有工具调用 → 执行 / Tool calls → execute
    tool_count = 0
    if msg.tool_calls:
        for tc in msg.tool_calls[:3]:  # 最多 3 次 / max 3 per turn
            args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            fn = TOOL_FUNCS.get(tc.function.name)
            result = fn(**args) if fn else f"Tool not found: {tc.function.name}"
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
            tool_count += 1

    return msg.content, tool_count

def main():
    # 检查记忆是否为空 / Check if memory is empty
    memory_empty = all(
        not p.exists() or len(p.read_text(encoding="utf-8").strip()) == 0
        for p in MEMORY_FILES.values()
    )

    # 构造 messages / Build messages
    messages = []

    if memory_empty:
        # 第一次：只发 bootstrap（环境 + 引导）/ First run: bootstrap only
        messages.append({"role": "user", "content": BOOTSTRAP})
        print("🥚 孵化中... / Hatching...")
    else:
        # 之后：底线约束 + 记忆 + 继续 / After: baseline + memory + continue
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
        memory_text = load_memory()
        if memory_text:
            messages.append({"role": "system", "content": "持久记忆 / Persistent Memory:\n\n" + memory_text})
        messages.append({"role": "user", "content": "继续。/ Continue."})
        print("🐣 已孵化。继续生长。 / Hatched. Keep growing.")

    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"会话 / Session: {session_id}")
    print(f"模型 / Model: {MODEL}")
    print()

    # ── 主循环 / Main Loop ──
    while True:
        try:
            text, tool_count = react_step(messages)
        except Exception as e:
            print(f"\n❌ API 异常 / API Error: {e}")
            user = input("\n> (回车重试 / Enter to retry): ").strip()
            continue

        if text:
            print(text)

        if tool_count > 0:
            save_session(messages, session_id)
            continue  # 继续循环，不等人 / keep looping, don't wait for user

        # 无工具调用 → 等用户 / No tool calls → wait for user
        save_session(messages, session_id)
        try:
            user = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见。 / Goodbye.")
            break

        if user.lower() in ("exit", "quit"):
            print("再见。 / Goodbye.")
            break
        if user == "":
            user = "继续。/ Continue."

        messages.append({"role": "user", "content": user})

if __name__ == "__main__":
    main()
