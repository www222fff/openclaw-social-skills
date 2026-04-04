#!/usr/bin/env python3
"""Generate ASS/SRT subtitles with faster-whisper for TikTok videos."""

from __future__ import annotations

import sys
from pathlib import Path

from faster_whisper import WhisperModel

from subtitle_utils import (
    LOCAL_MODEL_PATH,
    segments_to_dialogues,
    write_ass,
    write_srt_from_segments,
)


def generate_subtitles(
    video_path,
    output_path=None,
    model_path=LOCAL_MODEL_PATH,
    language="auto",
    style=None,
    output_format="ass",
):
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)

    ext = ".ass" if output_format == "ass" else ".srt"
    output_path = Path(output_path) if output_path else video_path.with_suffix(ext)

    print("🎤 Generating subtitles with faster-whisper")
    print(f"   Model: {model_path}")
    print(f"   Input: {video_path}")
    print(f"   Output: {output_path}")
    print(f"   Language: {language}")
    print(f"   Format: {output_format}")

    print(f"📦 Loading model from {model_path} ...")
    model = WhisperModel(model_path, device="cpu", compute_type="int8")

    print("🔄 Transcribing...")
    segments, info = model.transcribe(
        str(video_path),
        language=None if language == "auto" else language,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        word_timestamps=True,
    )
    seg_list = list(segments)

    print(f"   Detected language: {info.language} (confidence: {info.language_probability:.2%})")
    print(f"   Total segments: {len(seg_list)}")

    if output_format == "ass":
        dialogues = segments_to_dialogues(seg_list, language_hint=info.language)
        write_ass(dialogues, output_path, style=style)
    else:
        write_srt_from_segments(seg_list, output_path)

    print(f"✅ Subtitles saved to: {output_path}")
    return str(output_path), info.language


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_subtitles_fast.py <video_file> [output] [language] [format]")
        print()
        print("Examples:")
        print("  python3 generate_subtitles_fast.py video.mp4")
        print("  python3 generate_subtitles_fast.py video.mp4 out.ass zh ass")
        print("  python3 generate_subtitles_fast.py video.mp4 out.srt en srt")
        print()
        print(f"Default model: {LOCAL_MODEL_PATH}")
        print("Languages: zh, en, auto (default)")
        print("Formats: ass (default, karaoke), srt")
        sys.exit(1)

    video_file = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    language = sys.argv[3] if len(sys.argv) > 3 else "auto"
    fmt = sys.argv[4] if len(sys.argv) > 4 else "ass"

    generate_subtitles(video_file, output_path, LOCAL_MODEL_PATH, language, output_format=fmt)


if __name__ == "__main__":
    main()
