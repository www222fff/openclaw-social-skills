#!/usr/bin/env python3
"""End-to-end subtitle pipeline for TikTok videos.

Flow:
1. faster-whisper transcribes to ASS (word timings preserved)
2. If detected language is English, translate ASS to Chinese while preserving each Dialogue timing
3. Burn ASS into video with ffmpeg
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from generate_subtitles_fast import generate_subtitles
from translate_ass_preserve_timing import translate_ass_preserve_timing


def burn_subtitles(video_path: Path, ass_path: Path, output_path: Path | None = None) -> str:
    script_path = Path(__file__).with_name("embed_subtitles.py")
    cmd = ["python3", str(script_path), str(video_path), str(ass_path)]
    if output_path:
        cmd.append(str(output_path))
    print("🎬 Burning subtitles into video...")
    subprocess.run(cmd, check=True)
    return str(output_path) if output_path else ""


def run_pipeline(video_path, english_ass_path=None, chinese_ass_path=None, output_video_path=None, language="auto"):
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    english_ass_path = Path(english_ass_path) if english_ass_path else video_path.with_suffix(".ass")
    chinese_ass_path = Path(chinese_ass_path) if chinese_ass_path else video_path.with_name(f"{video_path.stem}_cn.ass")
    output_video_path = Path(output_video_path) if output_video_path else None

    generated_ass, detected_language = generate_subtitles(video_path, english_ass_path, language=language, output_format="ass")
    generated_ass = Path(generated_ass)

    final_ass = generated_ass
    if detected_language.startswith("en"):
        final_ass = Path(translate_ass_preserve_timing(generated_ass, chinese_ass_path, source_lang="en", target_lang="zh-CN"))
    elif detected_language.startswith("zh"):
        print("ℹ️ Detected Chinese audio; using original ASS directly.")
    else:
        print(f"ℹ️ Detected language {detected_language}; keeping original ASS without translation.")

    burn_subtitles(video_path, final_ass, output_video_path)
    print(f"✅ Pipeline complete. Final subtitle file: {final_ass}")
    return str(final_ass)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 make_tiktok_subtitles.py <video.mp4> [english.ass] [chinese.ass] [output.mp4] [language]")
        sys.exit(1)

    video_path = sys.argv[1]
    english_ass_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    chinese_ass_path = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None
    output_video_path = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "-" else None
    language = sys.argv[5] if len(sys.argv) > 5 else "auto"

    run_pipeline(video_path, english_ass_path, chinese_ass_path, output_video_path, language=language)


if __name__ == "__main__":
    main()
