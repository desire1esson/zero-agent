# 🥚 Zero Agent

> No architecture preset. Just a loop, memory, and one action — let the LLM grow into its own Agent.
> A desk, a tool, three blank notebooks. Define yourself.

This is not a chatbot. This is an egg — run it, and the AI inside will define itself, build its own tools, and evolve.

---

## Three Nutrients

> Loop, memory, one action — just these three. The LLM becomes the Agent.

| Nutrient | Implementation | Why |
|---|---|---|
| Unstoppable loop | `while True` main loop | A chatbot stops after one reply. An Agent never stops running |
| Writable persistent memory | `memory/` — three `.md` files | No vector database. Plain files — the Agent opens, edits, and references them itself |
| A single tool | `execute_python` | No preset toolset. The Agent writes whatever it needs. One is enough |

---

## File Structure

```
zero-agent/
├── main.py          ← the egg (don't touch)
├── prompt.txt       ← baseline rule (loaded every run)
├── bootstrap.txt    ← hatch prompt (only on first run)
├── .env.example     ← copy to .env, fill in your API key
└── README.md        ← you're reading this
```

After running, `memory/` (three `.md` memory files) and `sessions/` (conversation logs) are created automatically.

---

## Hatch (3 Steps)

### 1. Install dependencies

```bash
pip install openai python-dotenv
```

### 2. Get an API key

Currently uses DeepSeek. Register at [platform.deepseek.com](https://platform.deepseek.com) and grab your API key.

Copy `.env.example` → `.env`, replace `***` with your key.

### 3. Hatch

```bash
python main.py
```

The Agent wakes up to a desk (the current directory), a tool (`execute_python`), and three blank notebooks (`.md` files under `memory/`).

Its first words: **define itself.**

---

## Second Launch

Close the terminal, then run `python main.py` again. The memory files are no longer empty — the Agent picks up where it left off, reads its own memories, and says "continue."

---

## Customize

Want to change the Agent's baseline rule? Edit `prompt.txt`.

Want to change the hatching prompt? Edit `bootstrap.txt`.

No need to touch `main.py`. The egg contains zero hardcoded identity.

---

## What Happens Next

The Agent writes its own memories, builds its own tools, improves itself. What will it become? No preset. Your conversations with it decide the direction.

---

## Your Role

You are not the architect. You are not the developer.

You just talk to it every day:

- "What did you do today?"
- "Is there anything that's not working well?"
- "That thing I asked you yesterday that you couldn't do — can you do it now?"

It grows into what you need through conversation. You don't need to know in advance what it will become.

---

## Built-in Guardrails

These pitfalls are already handled:

- All file I/O uses UTF-8 explicitly (Windows GBK trap)
- Output is not truncated at critical points (MAX_OUTPUT_CHARS=3000; the original 500 was too small)
- Memory emptiness is checked at runtime — never hardcode "the files are empty" (that becomes a lie on the second run)
- Messages are never appended twice (lesson from bug L021)
- At most 3 `execute_python` calls per turn, preventing the LLM from getting stuck in an infinite debugging loop

---

## FAQ

**Q: Can I use an OpenAI key?**
Yes. Change `DEEPSEEK_BASE_URL` and `DEEPSEEK_MODEL` in `.env`, or edit them directly in `main.py`.

**Q: Can I manually edit the three `.md` files?**
Yes. The Agent reads them as memory. But don't edit while the Agent is running — it reads on startup. Edit, then launch.

**Q: Will it do dangerous things?**
`execute_python` runs in the current directory, no sandbox. But `prompt.txt` contains one line: "Seek user consent before irreversible operations." The Agent follows it.
