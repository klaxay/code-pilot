from dataclasses import dataclass, field
from typing import Any

@dataclass
class CodeChunk:
    content: str
    file_path: str
    start_line: int
    end_line: int

    symbol: str | None = None
    symbol_type: str | None = None
    language: str | None = None

    metadata: dict[str, Any] = field(
        default_factory = dict
    )