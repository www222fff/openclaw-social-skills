#!/usr/bin/env python3
"""Translate English ASS subtitles to Chinese while preserving original timings."""

from __future__ import annotations

import sys
from pathlib import Path

from subtitle_utils import (
    ass_text_to_plain,
    parse_ass_dialogues,
    translate_texts_google,
    write_translated_ass,
)


def translate_ass_preserve_timing(ass_path, output_path=None, source_lang="en", target_lang="zh-CN"):
    ass_path = Path(ass_path)
    if not ass_path.exists():
        raise FileNotFoundError(f"ASS file not found: {ass_path}")

    output_path = Path(output_path) if output_path else ass_path.with_name(f"{ass_path.stem}_cn.ass")
    sidecar_path = output_path.with_suffix(".json")

    header, dialogues = parse_ass_dialogues(ass_path)
    if not dialogues:
        raise RuntimeError("No Dialogue lines found in ASS file")

    source_texts = [ass_text_to_plain(d.text) for d in dialogues]

    print("🌐 Translating ASS subtitles while preserving timestamps")
    print(f"   Input: {ass_path}")
    print(f"   Output: {output_path}")
    print(f"   Dialogue lines: {len(dialogues)}")
    print(f"   Source language: {source_lang}")
    print(f"   Target language: {target_lang}")

    translated_texts = translate_texts_google(source_texts, source_lang=source_lang, target_lang=target_lang)
    write_translated_ass(header, dialogues, translated_texts, output_path, sidecar_json_path=sidecar_path)

    print(f"✅ Chinese ASS written: {output_path}")
    print(f"📝 Translation sidecar: {sidecar_path}")
    return str(output_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 translate_ass_preserve_timing.py <input.ass> [output.ass] [source_lang] [target_lang]")
        sys.exit(1)

    ass_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    source_lang = sys.argv[3] if len(sys.argv) > 3 else "en"
    target_lang = sys.argv[4] if len(sys.argv) > 4 else "zh-CN"

    translate_ass_preserve_timing(ass_path, output_path, source_lang=source_lang, target_lang=target_lang)


if __name__ == "__main__":
    main()
