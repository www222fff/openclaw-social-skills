---
name: tiktok-video-make
description: Download TikTok videos, generate Chinese subtitles with faster-whisper, embed subtitles, upload to Google Drive, and publish to Douyin. Use when user asks to download TikTok content with subtitles, add Chinese subtitles to videos, or upload/publish to Google Drive or Douyin.
---

# TikTok Video Maker

从 TikTok 下载视频 → faster-whisper 生成中文字幕（逐字出现效果）→ ffmpeg 嵌入 → 上传 Google Drive → 浏览器发布抖音（私密）

## 🎯 完整流程

Agent 直接按以下步骤执行，不依赖 pipeline 脚本：

### Step 1: 从视频队列选择视频

从预缓存的视频队列文件中**轮换账号**选取下一个待处理视频：

**队列文件**：`~/.openclaw/workspace/skills/tiktok-video-make/video_queue.json`

**结构**：两个账号各一个独立列表（按播放量降序），`nextAccount` 字段指示本次该用哪个账号。

```json
{
  "lastUpdated": "2026-04-02",
  "nextAccount": "kindpush343",
  "kindpush343": [ {"id":"...","views":"7.3M","url":"...","done":false}, ... ],
  "mind_and_measure": [ {"id":"...","views":"601.5K","url":"...","done":false}, ... ]
}
```

**流程**：
1. 读取 `video_queue.json`
2. 从 `nextAccount` 指示的列表中取第一个 `"done": false` 的视频
3. 如果该列表已全部 done，则从另一个列表取
4. 下载完成后：将该视频标记为 `"done": true`，**切换 `nextAccount` 到另一个账号**，写回文件
5. 如果两个列表都全部 done → 重新爬取（见下方）

**两个列表都用完时**：
1. 用浏览器（openclaw profile）打开各账号主页
2. 点 Popular 排序，用 evaluate 抓取视频链接和播放量
3. 分别写入各自的列表，更新 `video_queue.json`

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
| font_size | 50 | 字号 |
| alignment | 2 | 底部居中 |
| margin_v | 500 | 底部边距 px |
| outline_width | 2 | 描边宽度 |

## ⚠️ 注意

- 不使用 LLM vision 功能，浏览器操作用 snapshot/evaluate
- 发布到抖音默认**私密发布**
- 浏览器使用 `openclaw` profile
