import anthropic
from miniharness.config import API_KEY, ENDPOINT, MAX_TOKENS, MODEL
from miniharness.schemas import Message, ToolCall

if not API_KEY:
    raise RuntimeError("API_KEY is not set. Add it to the .env file in the project root.")

# pass the key/endpoint from our .env explicitly; the SDK on its own only reads ANTHROPIC_API_KEY
_client = anthropic.Anthropic(api_key=API_KEY, base_url=ENDPOINT)


def _to_api(messages: list[Message]) -> list[dict]:
    """Convert our Messages into the API's format."""
    out: list[dict] = []
    for m in messages:
        if m.role == "user":
            out.append({"role": "user", "content": m.content})

        elif m.role == "assistant":
            blocks = []
            if m.content:
                blocks.append({"type": "text", "text": m.content})
            for c in m.tool_calls:
                blocks.append(
                    {"type": "tool_use", "id": c.id, "name": c.name, "input": c.arguments}
                )
            out.append({"role": "assistant", "content": blocks})

        else:  # role == "tool": results go back as a *user* message
            r = m.tool_result
            block = {
                "type": "tool_result",
                "tool_use_id": r.tool_call_id,
                "content": r.content,
                "is_error": r.is_error,
            }
            # several tool results from one step share a single user message
            if out and out[-1]["role"] == "user" and isinstance(out[-1]["content"], list):
                out[-1]["content"].append(block)
            else:
                out.append({"role": "user", "content": [block]})
    return out


def chat(messages: list[Message], tools: list[dict], system: str) -> Message:
    """One model call. Returns our Message, not the raw API response."""
    resp = _client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=_to_api(messages),
        tools=tools,
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    calls = [
        ToolCall(id=b.id, name=b.name, arguments=b.input)
        for b in resp.content
        if b.type == "tool_use"
    ]
    return Message(role="assistant", content=text, tool_calls=calls)