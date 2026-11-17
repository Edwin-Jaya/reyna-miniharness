# cli.py
import sys

from miniharness import llm
from miniharness.agent.loop import Agent
from miniharness.tools import build_default_registry


def main() -> None:
    task = " ".join(sys.argv[1:]) or input("Task: ")
    agent = Agent(chat=llm.chat, registry=build_default_registry())
    print(agent.run(task))


if __name__ == "__main__":
    main()