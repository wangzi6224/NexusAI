import re
from typing import Any

CHUNK_MAX_CHARS = 1000
CHUNK_OVERLAP_CHARS = 120
MIN_CHUNK_CHARS = 80


class ChunkSplitter:
    def split(self, text: str, file_type: str) -> list[dict[str, Any]]:
        normalized_text = text.strip()

        if not normalized_text:
            return []

        if file_type == "md":
            return self.split_markdown(normalized_text)

        if file_type == "txt":
            return self.split_plain_text(normalized_text)

        return self.split_plain_text(normalized_text)

    def split_markdown(self, text: str) -> list[dict[str, Any]]:
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

        matches = list(heading_pattern.finditer(text))

        if not matches:
            return self.split_plain_text(text)

        chunks: list[dict[str, Any]] = []

        for index, match in enumerate(matches):
            heading = match.group(2).strip()
            heading_level = len(match.group(1))

            section_start = match.end()
            section_end = (
                matches[index + 1].start() if index + 1 < len(matches) else len(text)
            )

            section_content = text[section_start:section_end].strip()

            if not section_content:
                continue

            section_chunks = self._split_by_paragraphs(
                text=section_content,
                heading=heading,
                metadata={
                    "split_method": "markdown_heading",
                    "heading_level": heading_level,
                },
            )

            chunks.extend(section_chunks)

        return chunks

    def split_plain_text(self, text: str) -> list[dict[str, Any]]:
        return self._split_by_paragraphs(
            text=text,
            heading=None,
            metadata={
                "split_method": "paragraph",
            },
        )

    def _split_by_paragraphs(
        self,
        text: str,
        heading: str | None,
        metadata: dict[str, Any],
    ) -> list[dict[str, Any]]:
        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]

        chunks: list[dict[str, Any]] = []
        buffer: list[str] = []
        buffer_chars = 0

        for paragraph in paragraphs:
            paragraph_len = len(paragraph)

            if paragraph_len > CHUNK_MAX_CHARS:
                if buffer:
                    chunks.append(
                        self._build_chunk(
                            content="\n\n".join(buffer),
                            heading=heading,
                            metadata=metadata,
                        )
                    )
                    buffer = []
                    buffer_chars = 0

                chunks.extend(
                    self.split_long_text(
                        text=paragraph,
                        heading=heading,
                        metadata={
                            **metadata,
                            "split_method": "length_fallback",
                        },
                    )
                )
                continue

            next_chars = buffer_chars + paragraph_len

            if buffer and next_chars > CHUNK_MAX_CHARS:
                chunks.append(
                    self._build_chunk(
                        content="\n\n".join(buffer),
                        heading=heading,
                        metadata=metadata,
                    )
                )
                buffer = [paragraph]
                buffer_chars = paragraph_len
            else:
                buffer.append(paragraph)
                buffer_chars = next_chars

        if buffer:
            chunks.append(
                self._build_chunk(
                    content="\n\n".join(buffer),
                    heading=heading,
                    metadata=metadata,
                )
            )

        return [
            chunk
            for chunk in chunks
            if len(chunk["content"]) >= MIN_CHUNK_CHARS or len(chunks) == 1
        ]

    def split_long_text(
        self,
        text: str,
        heading: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []

        start = 0
        text_length = len(text)
        step = max(1, CHUNK_MAX_CHARS - CHUNK_OVERLAP_CHARS)

        while start < text_length:
            end = min(start + CHUNK_MAX_CHARS, text_length)
            content = text[start:end].strip()

            if content:
                chunks.append(
                    self._build_chunk(
                        content=content,
                        heading=heading,
                        metadata=metadata or {"split_method": "length_fallback"},
                    )
                )

            if end >= text_length:
                break

            start += step

        return chunks

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0

        chinese_chars = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
        other_chars = len(text) - chinese_chars

        return chinese_chars + max(1, other_chars // 4)

    def _build_chunk(
        self,
        content: str,
        heading: str | None,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        normalized_content = content.strip()

        return {
            "heading": heading,
            "content": normalized_content,
            "char_count": len(normalized_content),
            "estimated_tokens": self.estimate_tokens(normalized_content),
            "metadata": metadata,
        }
