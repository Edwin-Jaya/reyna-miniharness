from typing import Callable

from miniharness.agent.prompts import SYSTEM_PROMPT
from miniharness.config import MAX_STEPS
from miniharness.schemas import Message
from miniharness.tools.registry import ToolRegistry

ChatFn = Callable[..., Message]


class Agent:
    def __init__(
        self,
        chat: ChatFn,
        registry: ToolRegistry,
        system: str = SYSTEM_PROMPT,
        max_steps: int = MAX_STEPS,
    ) -> None:
        self.chat = chat
        self.registry = registry
        self.system = system
        self.max_steps = max_steps

    def run(self, task: str) -> str:
        messages = [Message(role="user", content=task)]

        for _ in range(self.max_steps):
            reply = self.chat(messages, tools=self.registry.schemas(), system=self.system)

            # small/local models sometimes end their turn with no text and no tool call;
            # don't treat that as the answer, just ask again (counts toward max_steps)
            if not reply.tool_calls and not reply.content.strip():
                continue

            messages.append(reply)

            if not reply.tool_calls:         
                return reply.content

            for call in reply.tool_calls:
                result = self.registry.dispatch(call)
                messages.append(Message(role="tool", tool_result=result))

        return "Stopped: reached the maximum number of steps."