from fakes import FakeLLM, text_msg, tool_msg

from miniharness.agent.loop import Agent
from miniharness.tools import build_default_registry


def make_agent(script, max_steps=5):
    fake = FakeLLM(script)
    agent = Agent(chat=fake.chat, registry=build_default_registry(), max_steps=max_steps)
    return agent, fake


def test_returns_final_answer_without_tools():
    agent, fake = make_agent([text_msg("Hello!")])
    assert agent.run("hi") == "Hello!"
    assert len(fake.calls) == 1


def test_runs_tool_then_answers():
    agent, fake = make_agent([
        tool_msg("calculator", {"expression": "12*7"}),
        text_msg("12 x 7 = 84"),
    ])
    assert agent.run("What is 12 x 7?") == "12 x 7 = 84"

    # the second model call must have received the tool result
    last = fake.calls[1][-1]
    assert last.role == "tool"
    assert last.tool_result.content == "84"
    assert last.tool_result.tool_call_id == "call_1"


def test_stops_at_max_steps():
    # model keeps asking for tools forever
    script = [tool_msg("calculator", {"expression": "1+1"}, f"call_{i}") for i in range(3)]
    agent, fake = make_agent(script, max_steps=3)
    result = agent.run("loop forever")
    assert "maximum number of steps" in result
    assert len(fake.calls) == 3


def test_empty_reply_is_retried_not_returned():
    agent, fake = make_agent([
        tool_msg("calculator", {"expression": "12*7"}),
        text_msg(""),            # model glitch: no text, no tool call
        text_msg("84"),
    ])
    assert agent.run("What is 12 x 7?") == "84"
    assert len(fake.calls) == 3
    # the empty reply must not be added to the conversation
    assert fake.calls[2] == fake.calls[1]


def test_tool_error_is_sent_back_to_model():
    agent, fake = make_agent([
        tool_msg("calculator", {"expression": "__import__('os')"}),
        text_msg("Sorry, I couldn't compute that."),
    ])
    agent.run("do something bad")
    result = fake.calls[1][-1].tool_result
    assert result.is_error is True


def test_unknown_tool_is_reported_not_crashed():
    agent, fake = make_agent([
        tool_msg("does_not_exist", {}),
        text_msg("ok"),
    ])
    assert agent.run("x") == "ok"
    result = fake.calls[1][-1].tool_result
    assert result.is_error is True
    assert "Unknown tool" in result.content