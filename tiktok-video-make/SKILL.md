---
name: tiktok-video-make
description: Download TikTok videos, generate Chinese subtitles with faster-whisper, embed subtitles, upload to Google Drive, and publish to Douyin. Use when user asks to download TikTok content with subtitles, add Chinese subtitles to videos, or upload/publish to Google Drive or Douyin.
---

# TikTok Video Maker

从 TikTok 下载视频 → faster-whisper 生成中文字幕（逐字出现效果）→ ffmpeg 嵌入 → 上传 Google Drive → 浏览器发布抖音（私密）

## 🎯 完整流程

Agent 直接按以下步骤执行，不依赖 pipeline 脚本：

### Step 1: 从指定账号选择视频

**必须**从以下两个账号提取视频，按播放量从高到低选择：
- `@kindpush343` → https://www.tiktok.com/@kindpush343
- `@mind_and_measure` → https://www.tiktok.com/@mind_and_measure

**流程**：
1. 用浏览器（openclaw profile）打开账号主页
2. 用 evaluate 抓取视频列表（标题、播放量、链接）
3. 按播放量从高到低排序
4. 跳过已下载的视频（检查 `~/.openclaw/workspace/downloads/` 目录）
5. 选择播放量最高的未处理视频

**不接受**：随意选视频、用 fallback 列表、跳过账号浏览直接用 URL。

### Step 2: 下载视频

```bash
cd ~/.openclaw/workspace/downloads
yt-dlp --proxy http://135.245.192.7:8000 --no-check-certificate -o "%(title)s.%(ext)s" <选中的视频URL>
```

### Step 3: 生成中文字幕（ASS 格式，逐字出现效果）

```bash
python3 ~/.openclaw/workspace/skills/tiktok-video-make/scripts/generate_subtitles_fast.py <video.mp4>
```

- 模型：本地 `/home/dannyaw/fast-whisper`（CTranslate2 格式，~1.5GB）
- 输出：ASS 格式，`\kf` 卡拉OK标签实现逐字填充
- 语言：默认 auto 自动检测（英文视频会先识别英文，agent 再翻译成中文字幕）
- 字体大小：26，底部居中，margin 30px（放在原始英文字幕下方）

### Step 4: 嵌入字幕

```bash
python3 ~/.openclaw/workspace/skills/tiktok-video-make/scripts/embed_subtitles.py <video.mp4> <video.ass>
```

ASS 格式自动使用内嵌样式（保留逐字效果），SRT 格式走 force_style。

### Step 5: 上传 Google Drive

```bash
export http_proxy=http://135.245.192.7:8000
export https_proxy=http://135.245.192.7:8000
~/.local/bin/rclone copy <subtitled_video.mp4> daily_english:daily_english -P
```

### Step 6: 发布到抖音（浏览器，私密发布）

使用 OpenClaw browser 工具（openclaw profile）：

1. 打开 `https://creator.douyin.com/creator-micro/content/upload`
2. 上传视频文件
3. 填写标题和描述
4. **设置为「仅自己可见」**（私密发布）
5. 点击发布

## 📁 目录结构

- **下载目录**：`~/.openclaw/workspace/downloads/`
- **脚本目录**：`~/.openclaw/workspace/skills/tiktok-video-make/scripts/`
  - `generate_subtitles_fast.py` — 字幕生成（ASS/SRT）
  - `embed_subtitles.py` — 字幕嵌入

## 📦 依赖

```bash
sudo apt install ffmpeg
pip install faster-whisper yt-dlp
```

- 字体：Droid Sans Fallback（系统已有），推荐 `sudo apt install fonts-noto-cjk`
- faster-whisper 模型：`/home/dannyaw/fast-whisper`（本地，无需联网）
- rclone：已配置 `daily_english` remote
- 代理：`http://135.245.192.7:8000`

## 🔧 字幕样式配置

在 `generate_subtitles_fast.py` 顶部 `DEFAULT_STYLE` 可调：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| font_name | Droid Sans Fallback | 字体 |
| font_size | 26 | 字号 |
| alignment | 2 | 底部居中 |
| margin_v | 30 | 底部边距 px（贴近底部，在英文字幕下方） |
| outline_width | 2 | 描边宽度 |

## ⚠️ 注意

- 不使用 LLM vision 功能，浏览器操作用 snapshot/evaluate
- 发布到抖音默认**私密发布**
- 浏览器使用 `openclaw` profile
