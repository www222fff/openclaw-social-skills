---
name: whop-video-make
description: Download materials from Google Drive, create TikTok-format videos with ffmpeg, and upload to Google Drive daily_english folder. Use when user asks to create videos for Whop projects (e.g., Flip.gg Street Interviews), download and process video materials, or submit videos to Whop creator platforms.
---

# Whop Video Maker

为 Whop 创意项目（如 Flip.gg、ViralityGG 等）制作、处理和上传短视频。

## 快速开始

### 1. 一键制作视频

**最简单的方式** - 自动下载素材、剪辑、上传：

```bash
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/make_whop_video.sh
```

功能：
- ✓ 从 Google Drive 素材库下载
- ✓ 用 ffmpeg 处理成竖屏格式 (9:16 TikTok)
- ✓ 提取前 30 秒
- ✓ 自动上传到 daily_english 云盘

### 2. 手动工作流

**Step 1: 下载素材**

```bash
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/download_materials.sh \
  --folder-id "1pLXBhcOOahs4Lgag52rCdirqe_QF4lwE"
```

**Step 2: 剪辑视频**

```bash
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/edit_video.sh \
  --input "materials/video.MOV" \
  --output "output.mp4" \
  --duration 30 \
  --format vertical  # 9:16 竖屏
```

**Step 3: 上传到 Google Drive**

```bash
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/upload_to_gdrive.sh \
  "output.mp4"
```

## 项目参考：Flip.gg Street Interviews

### 项目要求
- ✓ 高质量视频（竖屏 9:16）
- ✓ 时长：15-60 秒（推荐 30 秒）
- ✓ 必需标签：`#viralityflip`
- ✓ 地域要求：40% US views
- ✓ 新账号发布
- ✓ 无外部剪辑（仅用官方资源素材）

### 预期收益
- **CPM**: $1.25 / 1k views
- **单视频**: $1 - $500
- **平台**: TikTok / Instagram / YouTube

### 使用示例

```bash
# 为 Flip.gg 项目制作一个视频
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/make_whop_video.sh \
  --project "flip_gg" \
  --duration 30 \
  --materials-folder "1pLXBhcOOahs4Lgag52rCdirqe_QF4lwE"
```

## 完整工作流

### 场景 1：一键制作 + 上传

```bash
# 制作视频（所有步骤自动化）
bash scripts/make_whop_video.sh

# 输出：
# ✓ 下载素材
# ✓ ffmpeg 剪辑
# ✓ 上传到 Google Drive
# ✓ 显示云盘链接
```

### 场景 2：自定义处理

```bash
# 仅下载素材
bash scripts/download_materials.sh --folder-id "YOUR_FOLDER_ID"

# 自定义剪辑
ffmpeg -i materials/video.MOV \
  -t 30 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  output.mp4 -y

# 上传
bash scripts/upload_to_gdrive.sh output.mp4
```

## 文件说明

### 脚本

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `make_whop_video.sh` | 一键制作 + 上传 | 快速创建视频 |
| `download_materials.sh` | 从 Google Drive 下载素材 | 自定义处理 |
| `edit_video.sh` | ffmpeg 视频处理 | 高级剪辑 |
| `upload_to_gdrive.sh` | 上传到 Google Drive | 云盘存储 |

### 配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `MATERIALS_FOLDER_ID` | 素材库 Google Drive Folder ID | 见脚本 |
| `UPLOAD_REMOTE` | rclone remote (Google Drive) | `daily_english:daily_english` |
| `VIDEO_WIDTH` | 竖屏宽度 | 1080 |
| `VIDEO_HEIGHT` | 竖屏高度 | 1920 |
| `VIDEO_DURATION` | 视频时长（秒） | 30 |
| `HTTP_PROXY` | 代理地址 | `http://135.245.192.7:8000` |

## 常见问题

### Q: 视频制作失败，提示 ffmpeg 错误？
A: 确保已安装 ffmpeg：
```bash
sudo apt install ffmpeg -y
```

### Q: 上传到 Google Drive 失败？
A: 检查 rclone 配置：
```bash
rclone config
# 确保 daily_english remote 已正确配置
rclone listremotes
```

### Q: 如何修改视频时长？
A: 编辑脚本或传参：
```bash
bash scripts/make_whop_video.sh --duration 45
```

### Q: 文件太大无法上传？
A: 调整编码质量（-crf 参数）：
```bash
# 更高压缩（质量下降）
# -crf 28 (default 23)
```

### Q: 如何跳过上传只制作视频？
A: 修改 `make_whop_video.sh` 注释掉上传部分，或只运行 `edit_video.sh`

## 集成 tiktok-video-make

此 skill 基于 `tiktok-video-make` 的最佳实践：
- ✓ 重用上传脚本 (`upload_to_gdrive.sh`)
- ✓ 代理配置一致
- ✓ 文件命名规范 (YYYYMMDD_HHMM)
- ✓ rclone 上传方式

## 依赖

- **ffmpeg**: 视频处理
- **yt-dlp**: 媒体下载（可选）
- **gdown**: Google Drive 下载
- **rclone**: Google Drive 上传
- **bash**: 脚本运行

## 工作目录

```
~/.openclaw/workspace/
├── downloads/
│   └── whop_videos/         # 临时工作目录
│       ├── materials/       # 下载的素材
│       └── output/          # 制作的视频
└── skills/
    └── whop-video-make/     # 此 skill
        ├── scripts/         # 脚本
        └── SKILL.md         # 文档
```

## 示例

### 完整例子

```bash
# 制作 Flip.gg 视频
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/make_whop_video.sh

# 输出示例：
# ✅ 视频制作完成！
# 文件名: 20260329_1908_flip_interview.mp4
# 规格: 1080x1920 (竖屏 9:16)
# 时长: 30秒
# 云盘位置: Google Drive / daily_english / 20260329_1908_flip_interview.mp4
```

### 自动提交（下一步）

1. 打开 Whop 项目页面
2. 点击 "Submit Video"
3. 上传从 daily_english 云盘的视频
4. 添加项目标签（如 #viralityflip）
5. 提交

## 参考资源

- Whop: https://whop.com
- FFmpeg 文档: https://ffmpeg.org
- rclone Google Drive: https://rclone.org/drive/
- TikTok 视频规格: 竖屏 9:16 (1080x1920)
