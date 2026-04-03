#!/usr/bin/env python3
"""
使用 faster-whisper 生成中文字幕（ASS 格式，支持逐字出现效果）
模型：本地 /home/dannyaw/fast-whisper (CTranslate2 格式)
"""

import os
import sys
from pathlib import Path
from faster_whisper import WhisperModel

# 本地模型路径
LOCAL_MODEL_PATH = "/home/dannyaw/fast-whisper"

# 默认字幕样式
DEFAULT_STYLE = {
    "font_name": "Droid Sans Fallback",
    "font_size": 50,
    "primary_color": "&H00FFFFFF",   # 白色 (ASS: AABBGGRR)
    "outline_color": "&H00000000",   # 黑色描边
    "outline_width": 2,
    "alignment": 2,                   # 底部居中
    "margin_v": 500,
}


def format_ass_time(seconds):
    """将秒数转换为 ASS 时间格式 (H:MM:SS.cc)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def format_srt_time(seconds):
    """将秒数转换为 SRT 时间格式 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_ass_header(style=None):
    """生成 ASS 文件头"""
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


def build_karaoke_line(words, line_start, line_end):
    """
    根据 word-level timestamps 构建卡拉OK效果文本
    使用 \\kf 标签实现逐字填充效果
    """
    parts = []
    for w in words:
        # \\kf 的参数单位是 centiseconds (1/100 秒)
        duration_cs = int((w.end - w.start) * 100)
        if duration_cs < 1:
            duration_cs = 1
        text = w.word.strip()
        if text:
            parts.append(f"{{\\kf{duration_cs}}}{text}")
    return "".join(parts)


def generate_subtitles(video_path, output_path=None, model_path=LOCAL_MODEL_PATH,
                       language="auto", style=None, output_format="ass"):
    """
    使用 faster-whisper 生成字幕

    Args:
        video_path: 视频文件路径
        output_path: 输出文件路径（默认与视频同名）
        model_path: 模型路径（本地目录或模型名）
        language: 语言代码 (zh/en/auto)
        style: 字幕样式覆盖
        output_format: 输出格式 (ass/srt)

    Returns:
        str: 字幕文件路径
    """
    video_path = Path(video_path)
    if not video_path.exists():
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)

    ext = ".ass" if output_format == "ass" else ".srt"
    if output_path is None:
        output_path = video_path.with_suffix(ext)
    else:
        output_path = Path(output_path)

    print(f"🎤 Generating subtitles with faster-whisper")
    print(f"   Model: {model_path}")
    print(f"   Input: {video_path}")
    print(f"   Output: {output_path}")
    print(f"   Language: {language}")
    print(f"   Format: {output_format}")

    # 加载本地模型
    print(f"📦 Loading model from {model_path} ...")
    model = WhisperModel(model_path, device="cpu", compute_type="int8")

    # 转录 — 开启 word_timestamps 以支持逐字效果
    print(f"🔄 Transcribing...")
    segments, info = model.transcribe(
        str(video_path),
        language=None if language == "auto" else language,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        word_timestamps=True,
    )

    # 收集所有 segment（generator → list）
    seg_list = list(segments)
    print(f"   Detected language: {info.language} (confidence: {info.language_probability:.2%})")
    print(f"   Total segments: {len(seg_list)}")

    if output_format == "ass":
        _write_ass(seg_list, output_path, style)
    else:
        _write_srt(seg_list, output_path)

    print(f"✅ Subtitles saved to: {output_path}")
    return str(output_path)


MAX_CHARS_PER_LINE = 20  # 每行最多中文字符数（英文按 word 数量自动适配）


def _split_words_by_char_limit(words, max_chars=MAX_CHARS_PER_LINE):
    """将 word 列表按字符数限制拆分为多个子列表，每段不超过 max_chars 个字符。"""
    chunks = []
    current = []
    current_len = 0
    for w in words:
        wtext = w.word.strip()
        wlen = len(wtext)
        if current and current_len + wlen > max_chars:
            chunks.append(current)
            current = [w]
            current_len = wlen
        else:
            current.append(w)
            current_len += wlen
    if current:
        chunks.append(current)
    return chunks


def _write_ass(segments, output_path, style=None):
    """写 ASS 字幕（带逐字卡拉OK效果，长句自动拆行，每行不超过 MAX_CHARS_PER_LINE 字）"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(generate_ass_header(style))
        for seg in segments:
            if seg.words:
                chunks = _split_words_by_char_limit(seg.words)
                for chunk in chunks:
                    chunk_start = format_ass_time(chunk[0].start)
                    chunk_end = format_ass_time(chunk[-1].end)
                    text = build_karaoke_line(chunk, chunk[0].start, chunk[-1].end)
                    f.write(f"Dialogue: 0,{chunk_start},{chunk_end},Default,,0,0,0,,{text}\n")
            else:
                # 无 word-level 时整段输出
                start = format_ass_time(seg.start)
                end = format_ass_time(seg.end)
                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{seg.text.strip()}\n")


def _write_srt(segments, output_path):
    """写 SRT 字幕（无特效，兼容用途）"""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(f"{format_srt_time(seg.start)} --> {format_srt_time(seg.end)}\n")
            f.write(f"{seg.text.strip()}\n\n")


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
        print("Languages: zh (default), en, auto")
        print("Formats: ass (default, with karaoke), srt")
        sys.exit(1)

    video_file = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
    language = sys.argv[3] if len(sys.argv) > 3 else "auto"
    fmt = sys.argv[4] if len(sys.argv) > 4 else "ass"

    generate_subtitles(video_file, output_path, LOCAL_MODEL_PATH, language,
                       output_format=fmt)


if __name__ == "__main__":
    main()
