#!/usr/bin/env python3
"""
使用 ffmpeg 将 SRT 字幕烧录到视频中，支持自定义位置和样式
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def embed_subtitles(
    video_path,
    srt_path,
    output_path=None,
    position="bottom",  # top/bottom/middle
    font_size=24,
    font_color="white",
    outline_color="black",
    outline_width=2,
    margin_v=50  # 距离边缘的像素距离
):
    """
    将 SRT 字幕烧录到视频中
    
    Args:
        video_path: 输入视频路径
        srt_path: SRT 字幕文件路径
        output_path: 输出视频路径（默认添加时间戳）
        position: 字幕位置 (top/bottom/middle)
        font_size: 字体大小
        font_color: 字体颜色
        outline_color: 描边颜色
        outline_width: 描边宽度
        margin_v: 距离顶部/底部的边距（像素）
    
    Returns:
        str: 输出文件路径
    """
    video_path = Path(video_path)
    srt_path = Path(srt_path)
    
    if not video_path.exists():
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)
    
    if not srt_path.exists():
        print(f"❌ Error: SRT file not found: {srt_path}")
        sys.exit(1)
    
    # 默认输出路径（添加日期时间戳）
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = video_path.parent / f"{timestamp}_{video_path.stem}_subtitled.mp4"
    else:
        output_path = Path(output_path)
    
    print(f"🎬 Embedding subtitles into video...")
    print(f"   Video: {video_path}")
    print(f"   Subtitle: {srt_path}")
    print(f"   Output: {output_path}")
    
    # 构建 ffmpeg subtitles filter
    # 位置映射：
    # - bottom: Alignment=2 (底部居中)
    # - top: Alignment=8 (顶部居中)
    # - middle: Alignment=5 (中间居中)
    alignment_map = {
        "bottom": 2,
        "top": 8,
        "middle": 5
    }
    alignment = alignment_map.get(position, 2)
    
    # SRT 路径需要转义（Windows 路径斜杠、冒号等）
    srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")
    
    # 判断字幕格式：ASS 用 ass= filter（保留内嵌样式和特效），SRT 用 subtitles= filter
    srt_lower = str(srt_path).lower()
    if srt_lower.endswith(".ass") or srt_lower.endswith(".ssa"):
        # ASS 格式 — 直接使用内嵌样式（含卡拉OK效果），不覆盖 force_style
        subtitles_filter = f"ass={srt_escaped}"
        print("   Style source: embedded ASS style (FontSize/MarginV from .ass file)")
    else:
        print(f"   Style source: force_style (Position={position}, Size={font_size}, Margin={margin_v}px)")
        # SRT 格式 — 使用 force_style
        subtitles_filter = (
            f"subtitles={srt_escaped}:"
            f"force_style='"
            f"FontSize={font_size},"
            f"PrimaryColour=&H{color_to_ass(font_color)},"
            f"OutlineColour=&H{color_to_ass(outline_color)},"
            f"Outline={outline_width},"
            f"Alignment={alignment},"
            f"MarginV={margin_v}"
            f"'"
        )
    
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vf", subtitles_filter,
        "-c:a", "copy",  # 音频直接复制
        "-y",
        str(output_path)
    ]
    
    print(f"🔄 Running ffmpeg...")
    print(f"   Filter: {subtitles_filter}")
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print(f"❌ Error: ffmpeg failed with exit code {result.returncode}")
        sys.exit(1)
    
    print(f"✅ Subtitled video saved to: {output_path}")
    return str(output_path)


def color_to_ass(color_name):
    """
    将颜色名称转换为 ASS 字幕格式（BBGGRR）
    ASS 格式为 BGR 而不是 RGB
    """
    colors = {
        "white": "FFFFFF",
        "black": "000000",
        "red": "0000FF",
        "green": "00FF00",
        "blue": "FF0000",
        "yellow": "00FFFF",
        "cyan": "FFFF00",
        "magenta": "FF00FF",
    }
    
    # 如果是十六进制颜色（如 #RRGGBB），转换为 BGR
    if color_name.startswith("#"):
        rgb = color_name[1:]
        if len(rgb) == 6:
            r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
            return f"{b}{g}{r}"
    
    return colors.get(color_name.lower(), "FFFFFF")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 embed_subtitles.py <video> <srt> [output] [position] [size] [margin]")
        print()
        print("Examples:")
        print("  python3 embed_subtitles.py video.mp4 video.srt")
        print("  python3 embed_subtitles.py video.mp4 video.srt output.mp4")
        print("  python3 embed_subtitles.py video.mp4 video.srt output.mp4 top")
        print("  python3 embed_subtitles.py video.mp4 video.srt output.mp4 bottom 28 60")
        print()
        print("Positions: top, bottom (default), middle")
        print("Font size: default 24")
        print("Margin: default 50 (pixels from edge)")
        sys.exit(1)
    
    video = sys.argv[1]
    srt = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else None
    position = sys.argv[4] if len(sys.argv) > 4 else "bottom"
    font_size = int(sys.argv[5]) if len(sys.argv) > 5 else 24
    margin_v = int(sys.argv[6]) if len(sys.argv) > 6 else 50
    
    embed_subtitles(
        video,
        srt,
        output,
        position=position,
        font_size=font_size,
        margin_v=margin_v
    )


if __name__ == "__main__":
    main()
