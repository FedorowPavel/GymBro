"""Convert agent Markdown to Telegram HTML."""

from __future__ import annotations

import html
import re

_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+?)\*(?!\*)")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_TABLE_SEP_RE = re.compile(r"^\|[\s\-:|]+\|$")


def markdown_to_telegram_html(text: str) -> str:
    """Best-effort GitHub-style Markdown → Telegram HTML."""
    text = _markdown_tables_to_lines(text)
    placeholders: list[str] = []

    def _stash(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"\x00P{len(placeholders) - 1}\x00"

    text = _LINK_RE.sub(_stash, text)
    text = _CODE_RE.sub(_stash, text)
    text = html.escape(text, quote=False)
    text = _BOLD_RE.sub(r"<b>\1</b>", text)
    text = _ITALIC_RE.sub(r"<i>\1</i>", text)

    for index, raw in enumerate(placeholders):
        if raw.startswith("["):
            link = _LINK_RE.match(raw)
            if link:
                label = html.escape(link.group(1))
                url = html.escape(link.group(2), quote=True)
                replacement = f'<a href="{url}">{label}</a>'
            else:
                replacement = html.escape(raw)
        else:
            code = _CODE_RE.match(raw)
            replacement = (
                f"<code>{html.escape(code.group(1))}</code>" if code else html.escape(raw)
            )
        text = text.replace(f"\x00P{index}\x00", replacement)

    return text


def _markdown_tables_to_lines(text: str) -> str:
    lines = text.splitlines()
    result: list[str] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("|") and "|" in stripped[1:]:
            table_lines: list[str] = []
            while index < len(lines):
                row = lines[index].strip()
                if not row.startswith("|"):
                    break
                table_lines.append(row)
                index += 1
            result.extend(_format_table_rows(table_lines))
            continue
        result.append(lines[index])
        index += 1
    return "\n".join(result)


def _format_table_rows(table_lines: list[str]) -> list[str]:
    formatted: list[str] = []
    for row in table_lines:
        if _TABLE_SEP_RE.match(row):
            continue
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        cells = [cell for cell in cells if cell]
        if len(cells) >= 2:
            formatted.append(f"**{cells[0]}:** {cells[1]}")
        elif len(cells) == 1:
            formatted.append(cells[0])
    if formatted:
        formatted.append("")
    return formatted
