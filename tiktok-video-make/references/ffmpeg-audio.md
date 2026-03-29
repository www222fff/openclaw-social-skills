# ffmpeg Audio Processing Reference

## Volume Control

### 单轨调整音量

```bash
# 降低音量到 50%
ffmpeg -i input.mp4 -af "volume=0.5" output.mp4

# 放大音量到 200%
ffmpeg -i input.mp4 -af "volume=2.0" output.mp4

# 增加 10dB
ffmpeg -i input.mp4 -af "volume=10dB" output.mp4
```

### 混合多轨音频

```bash
# 混合两个音频（等权重）
ffmpeg -i audio1.mp3 -i audio2.mp3 -filter_complex \
  "[0:a][1:a]amix=inputs=2:duration=shortest" output.mp3

# 混合时调整各自音量
ffmpeg -i audio1.mp3 -i audio2.mp3 -filter_complex \
  "[0:a]volume=0.3[a0];[1:a]volume=1.5[a1];[a0][a1]amix=inputs=2:duration=shortest" \
  output.mp3
```

### 视频 + 音频混合

```bash
# 保留视频原声 + 叠加新音频
ffmpeg -i video.mp4 -i audio.mp3 -filter_complex \
  "[0:a]volume=0.2[a0];[1:a]volume=1.0[a1];[a0][a1]amix=inputs=2:duration=shortest[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac output.mp4

# 完全替换音频（不混合）
ffmpeg -i video.mp4 -i audio.mp3 -map 0:v -map 1:a -c:v copy -c:a aac -shortest output.mp4
```

## Duration Control

### shortest / longest / first

```bash
# 以最短流为准（默认推荐）
-shortest

# 以最长流为准（会填充静音/黑屏）
-filter_complex "[0:a][1:a]amix=inputs=2:duration=longest"

# 以第一个输入为准
-filter_complex "[0:a][1:a]amix=inputs=2:duration=first"
```

### 循环音频填充

```bash
# 音频循环填充到视频长度
ffmpeg -stream_loop -1 -i audio.mp3 -i video.mp4 -shortest output.mp4
```

## Audio Extraction

```bash
# 提取音频为 MP3（高质量）
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 0 audio.mp3

# 提取音频为 AAC
ffmpeg -i video.mp4 -vn -acodec aac -b:a 192k audio.m4a

# 提取原始音频流（不重编码）
ffmpeg -i video.mp4 -vn -acodec copy audio.aac
```

## Common Patterns

### Pattern 1: 视频原声降低 + 新音频叠加

```bash
ffmpeg -i video.mp4 -i new_audio.mp3 \
  -filter_complex "[0:a]volume=0.1[a0];[1:a]volume=2.0[a1];[a0][a1]amix=inputs=2:duration=shortest[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -shortest output.mp4
```

### Pattern 2: 音频为准截断/循环视频

```bash
# 获取音频时长
AUDIO_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio.mp3)

# 视频截断到音频长度
ffmpeg -i video.mp4 -i audio.mp3 -map 0:v -map 1:a -t $AUDIO_DUR -c:v copy -c:a aac output.mp4

# 视频循环填充到音频长度
ffmpeg -stream_loop -1 -i video.mp4 -i audio.mp3 -map 0:v -map 1:a -shortest -c:v copy -c:a aac output.mp4
```

### Pattern 3: 批量处理

```bash
for f in *.mp4; do
  ffmpeg -i "$f" -vn -acodec libmp3lame -q:a 2 "${f%.mp4}.mp3"
done
```

## Tips

- `-c:v copy`: 视频流不重编码（快速）
- `-c:a aac`: 音频编码为 AAC（兼容性好）
- `-shortest`: 以最短流为准（避免输出过长）
- `-y`: 覆盖输出文件（不询问）
- `-q:a 2`: MP3 质量（0=最高，9=最低，2=高质量）
