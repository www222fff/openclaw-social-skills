---
name: tiktok-video-make
description: Download TikTok videos, extract audio, merge with custom video, adjust audio volume, and upload to Google Drive. Use when user asks to download TikTok content, replace video audio, create videos with TikTok audio, or upload media to Google Drive folder daily_english.
---

# TikTok Video Maker

Download TikTok videos, extract/replace audio, and upload to Google Drive.

## Quick Start

### 1. Download Audio from TikTok (Recommended)

**直接下载音频文件**（yt-dlp 自动提取，无需 ffmpeg 手动处理）：

```bash
cd ~/.openclaw/workspace/downloads
yt-dlp --proxy "http://135.245.192.7:8000" \
  --extract-audio --audio-format mp3 --audio-quality 0 \
  -o "%(title)s.%(ext)s" \
  <TikTok URL>
```

### 2. (Alternative) Download Video then Extract Audio

如果需要保留视频文件：

```bash
# Step 1: Download video
yt-dlp --proxy "http://135.245.192.7:8000" \
  -o "%(title)s.%(ext)s" \
  <TikTok URL>

# Step 2: Extract audio
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3 -y
```

### 3. Merge Audio with Video

**以音频时长为准**（视频长→截断，视频短→循环）

文件名自动添加日期时间戳（格式：`YYYYMMDD_HHMM_名称.mp4`）

```bash
# 视频原声降到5%，新音频放大3倍
# 输出文件名：20260316_1406_output.mp4
ffmpeg -i video.mp4 -i audio.mp3 \
  -filter_complex "[0:a]volume=0.05[a0];[1:a]volume=3.0[a1];[a0][a1]amix=inputs=2:duration=shortest[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -shortest \
  "$(date +%Y%m%d_%H%M)_output.mp4" -y
```

### 4. Upload to Google Drive

```bash
export PATH=~/.local/bin:$PATH
export http_proxy=http://135.245.192.7:8000 https_proxy=http://135.245.192.7:8000
rclone copy output.mp4 daily_english:daily_english -P
```

## Common Workflows

### Workflow A: Full Automation (Recommended)

**完全自动化**：从备选视频列表获取高播放量音频，合并到随机视频，上传到 Google Drive

```bash
# 准备工作（只需一次）：
# 1. 将视频文件放到 downloads/videos/ 目录
cp video1.mp4 video2.mp4 video3.mp4 ~/.openclaw/workspace/downloads/videos/

# 2. 运行自动化流程
python3 scripts/auto_pipeline.py
```

**自动化流程**：
1. 从 `videos/` 随机选择一个视频
2. 从 `.tiktok_fallback.json` 读取备选视频列表
3. 筛选播放量最高的视频（排除已下载）
4. 下载音频
5. 合并到选中的视频
6. 上传到 Google Drive
7. 记录视频ID到历史文件

**配置**：
- **备选视频列表**：`~/.openclaw/workspace/downloads/.tiktok_fallback.json`
- **视频目录**：`~/.openclaw/workspace/downloads/videos/`
- **历史文件**：`~/.openclaw/workspace/downloads/.download_history.json`

**更新备选列表**：
当需要添加新视频时，手动编辑 `.tiktok_fallback.json` 或重新抓取 TikTok 账号。

### Workflow B: TikTok Audio → Custom Video

1. **Download audio directly** from TikTok (use yt-dlp `--extract-audio`)
2. Merge with user's video
3. Upload to Google Drive

### Workflow B: Download TikTok Video (with Audio)

1. Open TikTok in browser (`profile=openclaw`)
2. Search user or keyword
3. Filter by highest views (use `evaluate` to extract video list + view counts)
4. Download with yt-dlp

## Important Notes

### Browser Control

- **Profile**: Use default browser (no profile specified) for TikTok scraping
- **No screenshot/vision**: 禁用 vision 功能，全部走 DOM/evaluate
- **Search on TikTok**: 用 `evaluate` + JS 操作搜索框，不依赖 snapshot

### Audio Volume Control

- 视频原声：`[0:a]volume=0.05` (5%)
- 新音频：`[1:a]volume=3.0` (300%)
- 混合：`amix=inputs=2:duration=shortest`

### File Organization

- 下载目录：`~/.openclaw/workspace/downloads/`
- Google Drive 目标文件夹：`daily_english:daily_english`

### Prerequisites

- **ffmpeg**: 必须安装（`sudo apt install ffmpeg`）
- **yt-dlp**: 已安装
- **rclone**: 已安装并配置 `daily_english` remote

## Troubleshooting

### yt-dlp SSL Error

- 加代理：`--proxy "http://135.245.192.7:8000"`
- 加 `--no-check-certificate`（不推荐）

### 无水印下载

yt-dlp 默认下载带水印视频。去水印需要：
- 第三方网站（snapany.com / snaptik.app，但可能有反自动化）
- 或接受带水印版本

### 字幕生成

需要 Whisper 模型（当前网络环境下载困难）。备选方案：
- 手动听写文本
- 用在线字幕服务（需要稳定网络）

## Reference

- yt-dlp docs: https://github.com/yt-dlp/yt-dlp
- ffmpeg audio filters: https://ffmpeg.org/ffmpeg-filters.html#Audio-Filters
- rclone Google Drive: https://rclone.org/drive/
