from miniharness.tools.calculator import Calculator
from miniharness.tools.read_file import ReadFile
from miniharness.tools.registry import ToolRegistry


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(Calculator())
    registry.register(ReadFile())
    return registry