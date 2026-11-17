from miniharness.schemas import ToolCall, ToolResult
from miniharness.tools.base import Tool

class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def schemas(self) -> list[dict]:
        return [t.schema() for t in self._tools.values()]

    def dispatch(self, call: ToolCall) -> ToolResult:
        tool = self._tools.get(call.name)
        if tool is None:
            return ToolResult(
                tool_call_id=call.id, content=f"Unknown tool: {call.name}", is_error=True
            )
        try:
            return ToolResult(tool_call_id=call.id, content=tool.run(**call.arguments))
        except Exception as e: 
            return ToolResult(
                tool_call_id=call.id, content=f"{type(e).__name__}: {e}", is_error=True
            )