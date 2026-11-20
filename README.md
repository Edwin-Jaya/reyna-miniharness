# Reyna Miniharness

Reyna is a tool-calling agent loop I wrote from scratch, small enough to read in one sitting.

I built it because I wanted to see exactly what happens between "the model asked for a tool" and "the model gave an answer". It turns out the loop is small: send messages, run whatever tools the model asks for, send the results back, and repeat until it answers or runs out of steps. The whole `loop.py` file is 44 lines. Everything else in this repo exists to make that loop safe to run and easy to test.

**Phase 1 (the harness) is done.** Phase 2 (evaluation) comes next.

Write-up: [Why My First Agent Fell Apart in One File](https://medium.com/@edwinjaya/why-my-first-agent-fell-apart-in-one-file-d27f33f83a2a)

## What happens when you ask it something

```
you: "What is 12 x 7 + 3?"
 │
 ├─ step 1  model → calls calculator("12 * 7 + 3")
 │          harness runs it → "87" → sent back as a tool_result
 │
 └─ step 2  model → "12 x 7 + 3 = 87"   ← no tool call, so that's the answer
```

The loop stops in one of two ways: the model replies with text and no tool call, or it hits `MAX_STEPS` (5 by default). In the second case you get `"Stopped: reached the maximum number of steps."` instead of a loop that never ends.

## Layout

```
src/
├── miniharness/
│   ├── cli.py            # entry point: reads the task from argv or stdin
│   ├── config.py         # loads .env from the project root
│   ├── llm.py            # the only file that knows about the Anthropic SDK
│   ├── schemas.py        # Message / ToolCall / ToolResult dataclasses
│   ├── agent/
│   │   ├── loop.py       # the Agent class, i.e. the whole point
│   │   └── prompts.py    # system prompt
│   └── tools/
│       ├── base.py       # Tool ABC: name, description, JSON schema, run()
│       ├── registry.py   # register + dispatch, turns exceptions into errors
│       ├── calculator.py
│       └── read_file.py
└── tests/
    ├── fakes.py          # FakeLLM, which replays scripted replies
    ├── test_loop.py
    └── test_tools.py
```

## Decisions worth explaining

**The loop never sees the API format.** `llm.py` converts my own `Message` dataclasses to Anthropic's content blocks and back. `Agent` takes any `chat(messages, tools, system) -> Message` callable. That makes swapping providers a one-file change, and it's what makes the tests possible without a network.

**Tool failures go back to the model.** `ToolRegistry.dispatch` catches every exception and returns it as a `ToolResult` with `is_error=True`. An unknown tool name, a bad expression or a blocked path all become something the model can read and react to. Before this, one bad call crashed the whole run.

**The calculator doesn't use `eval`.** It walks the Python AST and only allows numbers and `+ - * / % **` plus unary minus. `__import__('os')` raises `ValueError`. Exponents above 100 are rejected too, because `9 ** 9999` is a cheap way to make the process hang.

**`read_file` stays inside its folder.** Paths are resolved and checked with `is_relative_to(workspace)`, so `../../etc/passwd` raises `PermissionError`. Output is cut off at 10k characters so a big file can't eat the context window.

**Empty replies get retried.** Smaller and local models sometimes end a turn with no text and no tool call. The loop doesn't return that as the answer. It just asks again, and the retry still counts toward `MAX_STEPS`. I saw this with Gemma 4 E4B in LM Studio: after a tool result it returned an empty reply once, and the retry got the answer.

## Setup

Python 3.11. I use conda, but any virtualenv works.

```bash
pip install -e ".[dev]"
cp .env.example .env
```

That installs `anthropic`, `python-dotenv` and `pytest`, and adds a `miniharness` command to your PATH.

Then fill in `.env`:

```ini
ENDPOINT=https://api.anthropic.com   # or any Anthropic-compatible base URL
MODEL=claude-sonnet-5-5
API_KEY=sk-...
# optional, where read_file is allowed to look (relative paths start from the project root)
WORKSPACE=data/workspace
```

To run against a local model in LM Studio, point `ENDPOINT` at its local server and set `MODEL` to the model you loaded:

```ini
ENDPOINT=http://127.0.0.1:<port>     # LM Studio local server
MODEL=google/gemma-4-e4b
```

## Running it

```bash
miniharness "What is 1234 * 5678 - 99?"
miniharness "Summarise notes.txt"     # reads data/workspace/notes.txt
```

`python -m miniharness.cli "..."` does the same thing.

If you leave out the task, it asks for one with `Task: `.

I have run it with Gemma 4 E4B served by LM Studio through the Anthropic SDK.

## Tests

```bash
pytest
```

`pyproject.toml` already points pytest at `src/`, so this works without any extra setup. None of the tests touch a real model. `FakeLLM` replays a fixed script of replies and records exactly what the loop sent at each step, so the tests can check things like:

- the tool result actually reaches the second model call, with the right `tool_call_id`
- a model that keeps calling tools stops at `max_steps`
- an empty reply is retried and **not** added to the history
- unknown tools and tool exceptions come back as `is_error=True` instead of crashing

## Adding a tool

Subclass `Tool`, give it a name, a description the model will read, and a JSON schema, then register it:

```python
class Echo(Tool):
    name = "echo"
    description = "Repeat the given text back."
    parameters = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    }

    def run(self, text: str) -> str:
        return text
```

Add `registry.register(Echo())` in `tools/__init__.py`. If `run` raises, the registry handles it.

## Next: evaluation

The harness works. What I don't have yet is a way to _measure_ it. Phase 2 will cover:

- a fixed set of tasks with expected answers or checks
- running them against a real model and scoring the results
- tracking steps, tool errors and failures across runs, so prompt or model changes show up as numbers instead of guesses
