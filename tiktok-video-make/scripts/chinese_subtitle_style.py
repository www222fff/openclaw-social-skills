#!/usr/bin/env python3
"""
中文字幕样式优化 + 逐字出现效果
- 大字体、适当位置
- 每个短句一组，逐字 \kf 填充
"""

import re
import sys
from pathlib import Path

# 中文字幕样式
STYLE = {
    "font_name": "Droid Sans Fallback",
    "font_size": 58,           # 大字体，1080x1920 下清晰
    "primary_color": "&H00FFFFFF",
    "outline_color": "&H00000000",
    "back_color": "&H80000000",
    "outline_width": 3,
    "shadow": 2,
    "alignment": 2,            # 底部居中
    "margin_v": 260,           # 距底部 260px，不贴底
}

# 短句分割标点
SPLIT_PUNCT = re.compile(r'[，。！？、；：\s]+')


def split_into_phrases(text):
    """把一句话按标点/空格切成短句"""
    parts = SPLIT_PUNCT.split(text.strip())
    return [p for p in parts if p]


def make_karaoke_text(phrase, duration_sec):
    """给短句的每个字加 \\kf 标签，均匀分配时间"""
    chars = list(phrase)
    if not chars:
        return ""
    per_char_cs = max(1, int(duration_sec * 100 / len(chars)))
    return "".join(f"{{\\kf{per_char_cs}}}{ch}" for ch in chars)


def format_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def generate_header():
    s = STYLE
    return f"""[Script Info]
Title: Chinese subtitles (styled)
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{s['font_name']},{s['font_size']},{s['primary_color']},&H000000FF,{s['outline_color']},{s['back_color']},1,0,0,0,100,100,0,0,1,{s['outline_width']},{s['shadow']},{s['alignment']},20,20,{s['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def parse_ass_dialogue(line):
    """解析 ASS Dialogue 行，返回 (start_sec, end_sec, text)"""
    m = re.match(r'Dialogue:\s*\d+,(\d+:\d+:\d+\.\d+),(\d+:\d+:\d+\.\d+),.*?,,\d+,\d+,\d+,,(.+)', line)
    if not m:
        return None
    
    def to_sec(t):
        parts = t.split(':')
        h, mm = int(parts[0]), int(parts[1])
        s_cs = parts[2].split('.')
        s, cs = int(s_cs[0]), int(s_cs[1])
        return h * 3600 + mm * 60 + s + cs / 100.0
    
    return to_sec(m.group(1)), to_sec(m.group(2)), m.group(3)


def process_ass(input_path, output_path):
    """读取现有 ASS，重新生成带逐字效果的版本"""
    lines = Path(input_path).read_text(encoding='utf-8').splitlines()
    
    dialogues = []
    for line in lines:
        if line.startswith('Dialogue:'):
            parsed = parse_ass_dialogue(line)
            if parsed:
                dialogues.append(parsed)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(generate_header())
        
        for start, end, text in dialogues:
            # 清除已有的 ASS 标签
            clean = re.sub(r'\{[^}]*\}', '', text).strip()
            
            # 分成短句
            phrases = split_into_phrases(clean)
            if not phrases:
                continue
            
            total_dur = end - start
            # 每个短句分配等比时间
            total_chars = sum(len(p) for p in phrases)
            if total_chars == 0:
                continue
            
            t = start
            for phrase in phrases:
                phrase_dur = total_dur * len(phrase) / total_chars
                phrase_end = min(t + phrase_dur, end)
                
                karaoke = make_karaoke_text(phrase, phrase_dur)
                f.write(f"Dialogue: 0,{format_ass_time(t)},{format_ass_time(phrase_end)},Default,,0,0,0,,{karaoke}\n")
                
                t = phrase_end
    
    print(f"✅ Output: {output_path}")
    print(f"   Font: {STYLE['font_name']} @ {STYLE['font_size']}px")
    print(f"   Margin bottom: {STYLE['margin_v']}px")
    print(f"   Phrases: split by punctuation, per-char \\kf karaoke")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 chinese_subtitle_style.py <input.ass> [output.ass]")
        sys.exit(1)
    
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else str(Path(inp).with_suffix('')) + '_styled.ass'
    process_ass(inp, out)


if __name__ == "__main__":
    main()
