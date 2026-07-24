from dataclasses import dataclass

from app.indexing.models import CodeChunk


@dataclass
class RetrievalContext:
    formatted_context: str
    retrieved_chunks: list[CodeChunk]


def build_context(
    chunks: list[CodeChunk],
) -> RetrievalContext:
    if not chunks:
        return RetrievalContext(
            formatted_context="",
            retrieved_chunks=[],
        )

    context_parts: list[str] = []

    for chunk in chunks:
        context_parts.append("=" * 80)
        context_parts.append(f"File: {chunk.file_path}")

        if chunk.symbol:
            context_parts.append(f"Symbol: {chunk.symbol}")

        if chunk.symbol_type:
            context_parts.append(f"Type: {chunk.symbol_type}")

        context_parts.append(
            f"Lines: {chunk.start_line}-{chunk.end_line}"
        )

        if chunk.language:
            context_parts.append(f"Language: {chunk.language}")

        context_parts.append("")
        context_parts.append(chunk.content)
        context_parts.append("")

    formatted_context = "\n".join(context_parts)

    return RetrievalContext(
        formatted_context=formatted_context,
        retrieved_chunks=chunks,
    )