#!/usr/bin/env python3
"""Shared helpers for TikTok subtitle generation and ASS translation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

LOCAL_MODEL_PATH = "/home/dannyaw/fast-whisper"

DEFAULT_STYLE = {
    "font_name": "Droid Sans Fallback",
    "font_size": 60,
    "primary_color": "&H00FFFFFF",
    "outline_color": "&H00000000",
    "outline_width": 2,
    "alignment": 2,
    "margin_v": 700,
}

MAX_SOURCE_CHARS_PER_CHUNK = 20
DEFAULT_CN_CHARS_PER_LINE = 14
DEFAULT_CN_MAX_LINES = 2

ASS_TAG_RE = re.compile(r"\{[^}]*\}")


@dataclass
class DialogueLine:
    start: float
    end: float
    text: str


@dataclass
class ParsedAssDialogue:
    raw_prefix_fields: list[str]
    text: str
    start: float
    end: float
    raw_line: str


def format_ass_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        secs += 1
        centis -= 100
    if secs >= 60:
        minutes += 1
        secs -= 60
    if minutes >= 60:
        hours += 1
        minutes -= 60
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def parse_ass_time(value: str) -> float:
    hours, minutes, sec_centis = value.strip().split(":")
    secs, centis = sec_centis.split(".")
    return int(hours) * 3600 + int(minutes) * 60 + int(secs) + int(centis) / 100.0


def format_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        secs += 1
        millis -= 1000
    if secs >= 60:
        minutes += 1
        secs -= 60
    if minutes >= 60:
        hours += 1
        minutes -= 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_ass_header(style: dict | None = None) -> str:
    s = {**DEFAULT_STYLE, **(style or {})}
    return f"""[Script Info]
Title: Auto-generated subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{s['font_name']},{s['font_size']},{s['primary_color']},&H000000FF,{s['outline_color']},&H80000000,0,0,0,0,100,100,0,0,1,{s['outline_width']},1,{s['alignment']},20,20,{s['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def escape_ass_text(text: str) -> str:
    return (
        text.replace("\\", r"\\")
        .replace("{", "（")
        .replace("}", "）")
        .replace("\r", "")
    )


def ass_text_to_plain(text: str) -> str:
    stripped = ASS_TAG_RE.sub("", text)
    stripped = stripped.replace(r"\N", "\n").replace(r"\n", "\n")
    return stripped.strip()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def distribute_evenly(total: int, count: int) -> list[int]:
    if count <= 0:
        return []
    base = max(1, total // count)
    values = [base] * count
    current_total = base * count
    if current_total < total:
        for i in range(total - current_total):
            values[i % count] += 1
    elif current_total > total:
        overflow = current_total - total
        i = count - 1
        while overflow > 0 and i >= 0:
            reducible = min(overflow, max(0, values[i] - 1))
            values[i] -= reducible
            overflow -= reducible
            i -= 1
    return values


def _visible_len(text: str) -> int:
    return sum(1 for ch in text if not ch.isspace())


STRONG_BREAK_CHARS = "。！？；：.!?;:"
SOFT_BREAK_CHARS = "，、,"


def _find_best_break_index(text: str, max_chars_per_line: int) -> int | None:
    total_visible = _visible_len(text)
    if total_visible <= max_chars_per_line:
        return None

    target = min(max_chars_per_line, max(1, total_visible // 2))
    min_left = max(4, int(max_chars_per_line * 0.55))
    max_left = max_chars_per_line + 4

    candidates: list[tuple[int, int, int]] = []
    visible = 0
    for idx, ch in enumerate(text):
        if not ch.isspace():
            visible += 1

        if ch not in STRONG_BREAK_CHARS + SOFT_BREAK_CHARS + " ":
            continue

        left = text[: idx + 1].rstrip()
        right = text[idx + 1 :].lstrip()
        left_len = _visible_len(left)
        right_len = _visible_len(right)

        if left_len < min_left or left_len > max_left or right_len == 0:
            continue

        if ch in STRONG_BREAK_CHARS:
            priority = 0
        elif ch in SOFT_BREAK_CHARS:
            priority = 1
        else:
            priority = 2

        balance_penalty = abs(left_len - target)
        candidates.append((priority, balance_penalty, idx + 1))

    if candidates:
        candidates.sort()
        return candidates[0][2]

    visible = 0
    best_idx = None
    best_penalty = None
    for idx, ch in enumerate(text):
        if not ch.isspace():
            visible += 1
        if visible >= max(1, max_chars_per_line):
            penalty = abs(visible - target)
            if best_penalty is None or penalty < best_penalty:
                best_penalty = penalty
                best_idx = idx + 1
            if visible >= max_chars_per_line + 2:
                break
    return best_idx


def wrap_chinese_text(text: str, max_chars_per_line: int = DEFAULT_CN_CHARS_PER_LINE,
                      max_lines: int = DEFAULT_CN_MAX_LINES) -> str:
    text = normalize_text(text)
    if not text:
        return text

    raw_lines = [part.strip() for part in text.split("\n") if part.strip()]
    if not raw_lines:
        return ""

    final_lines: list[str] = []
    remaining_slots = max_lines

    for part_index, part in enumerate(raw_lines):
        if remaining_slots <= 0:
            if final_lines:
                final_lines[-1] += part
            else:
                final_lines.append(part)
            continue

        current = part
        while current and remaining_slots > 0:
            if _visible_len(current) <= max_chars_per_line or remaining_slots == 1:
                final_lines.append(current.strip())
                remaining_slots -= 1
                current = ""
                break

            break_idx = _find_best_break_index(current, max_chars_per_line)
            if break_idx is None:
                final_lines.append(current.strip())
                remaining_slots -= 1
                current = ""
                break

            left = current[:break_idx].rstrip()
            right = current[break_idx:].lstrip()
            final_lines.append(left)
            remaining_slots -= 1
            current = right

        if current:
            if final_lines:
                final_lines[-1] += current
            else:
                final_lines.append(current)

        if part_index < len(raw_lines) - 1 and remaining_slots > 0:
            continue

    if len(final_lines) > max_lines:
        kept = final_lines[: max_lines - 1]
        kept.append("".join(final_lines[max_lines - 1 :]))
        final_lines = kept

    return r"\N".join(line.strip() for line in final_lines if line.strip())


def build_char_karaoke_text(text: str, start: float, end: float) -> str:
    total_cs = max(1, int(round((end - start) * 100)))
    normalized = text.replace("\r", "").replace("\n", r"\N")
    char_units = []
    i = 0
    while i < len(normalized):
        if normalized[i : i + 2] == r"\N":
            i += 2
            continue
        ch = normalized[i]
        if not ch.isspace():
            char_units.append(ch)
        i += 1

    durations = distribute_evenly(total_cs, len(char_units))
    duration_index = 0
    parts: list[str] = []
    i = 0
    while i < len(normalized):
        if normalized[i : i + 2] == r"\N":
            parts.append(r"\N")
            i += 2
            continue
        ch = normalized[i]
        if ch.isspace():
            parts.append(ch)
        else:
            duration = durations[duration_index] if duration_index < len(durations) else 1
            duration_index += 1
            parts.append(f"{{\\kf{duration}}}{escape_ass_text(ch)}")
        i += 1
    return "".join(parts).strip()


def build_word_karaoke_text(words: Sequence, keep_spaces: bool = True) -> str:
    parts: list[str] = []
    for word in words:
        duration_cs = max(1, int(round((word.end - word.start) * 100)))
        token = word.word if keep_spaces else word.word.strip()
        if not token:
            continue
        safe = escape_ass_text(token)
        if safe.strip():
            parts.append(f"{{\\kf{duration_cs}}}{safe}")
        else:
            parts.append(safe)
    return "".join(parts).strip()


def split_whisper_words(words: Sequence, max_chars: int = MAX_SOURCE_CHARS_PER_CHUNK) -> list[list]:
    chunks: list[list] = []
    current: list = []
    current_len = 0

    for word in words:
        visible = word.word.strip()
        visible_len = len(visible)
        if not current:
            current = [word]
            current_len = visible_len
            continue

        punctuation_break = visible.endswith((".", ",", "?", "!", ";", ":")) and current_len >= max_chars * 0.6
        if current_len + visible_len > max_chars or punctuation_break:
            chunks.append(current)
            current = [word]
            current_len = visible_len
        else:
            current.append(word)
            current_len += visible_len

    if current:
        chunks.append(current)
    return chunks


def segments_to_dialogues(segments: Sequence, max_chars: int = MAX_SOURCE_CHARS_PER_CHUNK,
                          language_hint: str | None = None) -> list[DialogueLine]:
    dialogues: list[DialogueLine] = []
    zh_like = bool(language_hint and language_hint.startswith("zh"))

    for seg in segments:
        if getattr(seg, "words", None):
            chunks = split_whisper_words(seg.words, max_chars=max_chars)
            for chunk in chunks:
                start = chunk[0].start
                end = chunk[-1].end
                if zh_like:
                    plain = normalize_text("".join(w.word for w in chunk))
                    text = build_char_karaoke_text(plain, start, end)
                else:
                    text = build_word_karaoke_text(chunk)
                dialogues.append(DialogueLine(start=start, end=end, text=text))
        else:
            plain = normalize_text(seg.text)
            if not plain:
                continue
            text = build_char_karaoke_text(plain, seg.start, seg.end) if zh_like else escape_ass_text(plain)
            dialogues.append(DialogueLine(start=seg.start, end=seg.end, text=text))
    return dialogues


def write_ass(dialogues: Sequence[DialogueLine], output_path: str | Path, style: dict | None = None) -> str:
    output_path = Path(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(generate_ass_header(style))
        for dialogue in dialogues:
            f.write(
                f"Dialogue: 0,{format_ass_time(dialogue.start)},{format_ass_time(dialogue.end)},Default,,0,0,0,,{dialogue.text}\n"
            )
    return str(output_path)


def write_srt_from_segments(segments: Sequence, output_path: str | Path) -> str:
    output_path = Path(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(f"{format_srt_time(seg.start)} --> {format_srt_time(seg.end)}\n")
            f.write(f"{normalize_text(seg.text)}\n\n")
    return str(output_path)


def parse_ass_dialogues(ass_path: str | Path) -> tuple[list[str], list[ParsedAssDialogue]]:
    ass_path = Path(ass_path)
    with open(ass_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header: list[str] = []
    dialogues: list[ParsedAssDialogue] = []

    for line in lines:
        if line.startswith("Dialogue:"):
            payload = line[len("Dialogue: ") :].rstrip("\n")
            parts = payload.split(",", 9)
            if len(parts) < 10:
                header.append(line)
                continue
            start = parse_ass_time(parts[1])
            end = parse_ass_time(parts[2])
            dialogues.append(
                ParsedAssDialogue(
                    raw_prefix_fields=parts[:9],
                    text=parts[9],
                    start=start,
                    end=end,
                    raw_line=line,
                )
            )
        else:
            header.append(line)
    return header, dialogues


def write_translated_ass(header: Sequence[str], dialogues: Sequence[ParsedAssDialogue],
                         translated_texts: Sequence[str], output_path: str | Path,
                         sidecar_json_path: str | Path | None = None) -> str:
    output_path = Path(output_path)
    records = []
    with open(output_path, "w", encoding="utf-8") as f:
        for line in header:
            f.write(line)
        for dialogue, translated in zip(dialogues, translated_texts):
            wrapped = wrap_chinese_text(translated)
            karaoke = build_char_karaoke_text(wrapped, dialogue.start, dialogue.end)
            payload = ",".join(dialogue.raw_prefix_fields + [karaoke])
            f.write(f"Dialogue: {payload}\n")
            records.append({
                "start": format_ass_time(dialogue.start),
                "end": format_ass_time(dialogue.end),
                "source": ass_text_to_plain(dialogue.text),
                "translated": translated,
                "wrapped": wrapped,
            })

    if sidecar_json_path:
        sidecar_json_path = Path(sidecar_json_path)
        with open(sidecar_json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    return str(output_path)
