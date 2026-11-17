from miniharness.schemas import Message, ToolCall


class FakeLLM:
    """Plays back a scripted list of replies instead of calling a real model."""

    def __init__(self, script: list[Message]) -> None:
        self.script = list(script)
        self.calls: list[list[Message]] = []   # what the loop sent us, per step

    def chat(self, messages, tools, system) -> Message:
        self.calls.append(list(messages))      # copy: the loop keeps mutating its list
        if not self.script:
            raise AssertionError("FakeLLM script exhausted: the loop called the model too often")
        return self.script.pop(0)


def text_msg(text: str) -> Message:
    return Message(role="assistant", content=text)


def tool_msg(name: str, arguments: dict, call_id: str = "call_1") -> Message:
    return Message(
        role="assistant",
        tool_calls=[ToolCall(id=call_id, name=name, arguments=arguments)],
    )