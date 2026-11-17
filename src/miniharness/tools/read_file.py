from pathlib import Path

from miniharness.config import WORKSPACE
from miniharness.tools.base import Tool

MAX_CHARS = 10_000


class ReadFile(Tool):
    name = "read_file"
    description = "Read a text file from the workspace folder. Path is relative to the workspace."
    parameters = {
        "type": "object",
        "properties": {"path": {"type": "string"}},
        "required": ["path"],
    }

    def run(self, path: str) -> str:
        base = Path(WORKSPACE).resolve()
        target = (base / path).resolve()
        if not target.is_relative_to(base):      # blocks ../../etc/passwd
            raise PermissionError("Path is outside the workspace")
        text = target.read_text(encoding="utf-8")
        if len(text) > MAX_CHARS:
            return text[:MAX_CHARS] + "\n...[truncated]"
        return text