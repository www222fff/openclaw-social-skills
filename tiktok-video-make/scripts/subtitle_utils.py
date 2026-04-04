#!/usr/bin/env python3
"""Shared helpers for TikTok subtitle generation and ASS translation."""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

LOCAL_MODEL_PATH = "/home/dannyaw/fast-whisper"

DEFAULT_STYLE = {
    "font_name": "Droid Sans Fallback",
    "font_size": 50,
    "primary_color": "&H00FFFFFF",
    "outline_color": "&H00000000",
    "outline_width": 2,
    "alignment": 2,
    "margin_v": 500,
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


def wrap_chinese_text(text: str, max_chars_per_line: int = DEFAULT_CN_CHARS_PER_LINE,
                      max_lines: int = DEFAULT_CN_MAX_LINES) -> str:
    text = normalize_text(text)
    if not text:
        return text

    chars: list[str] = []
    for ch in text:
        if ch == "\n":
            chars.append(r"\N")
        elif ch.isspace():
            if chars and chars[-1] not in {" ", r"\N"}:
                chars.append(" ")
        else:
            chars.append(ch)

    lines: list[str] = []
    current: list[str] = []
    visible_count = 0

    for ch in chars:
        if ch == r"\N":
            lines.append("".join(current).strip())
            current = []
            visible_count = 0
            continue

        current.append(ch)
        if not ch.isspace():
            visible_count += 1

        should_break = False
        if visible_count >= max_chars_per_line:
            if ch in "，。！？；：,.!?;:" or visible_count >= max_chars_per_line + 2:
                should_break = True

        if should_break and len(lines) < max_lines - 1:
            lines.append("".join(current).strip())
            current = []
            visible_count = 0

    if current:
        lines.append("".join(current).strip())

    if len(lines) > max_lines:
        kept = lines[: max_lines - 1]
        kept.append("".join(lines[max_lines - 1 :]))
        lines = kept

    return r"\N".join(line for line in lines if line)


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


def translate_text_google(text: str, source_lang: str = "auto", target_lang: str = "zh-CN",
                          timeout: int = 20, retries: int = 3) -> str:
    endpoint = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": source_lang,
        "tl": target_lang,
        "dt": "t",
        "q": text,
    }
    url = endpoint + "?" + urllib.parse.urlencode(params)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36"
    }

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            translated = "".join(part[0] for part in data[0] if part and part[0])
            return normalize_text(translated)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * attempt)
    raise RuntimeError(f"Translation failed after {retries} attempts: {last_error}")


def translate_texts_google(texts: Iterable[str], source_lang: str = "auto", target_lang: str = "zh-CN",
                           sleep_seconds: float = 0.15) -> list[str]:
    results: list[str] = []
    cache: dict[str, str] = {}

    for text in texts:
        normalized = normalize_text(text)
        if not normalized:
            results.append("")
            continue
        if normalized in cache:
            results.append(cache[normalized])
            continue
        translated = translate_text_google(normalized, source_lang=source_lang, target_lang=target_lang)
        cache[normalized] = translated
        results.append(translated)
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
    return results
