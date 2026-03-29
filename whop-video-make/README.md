# Whop Video Maker Skill

为 Whop 创意平台（Flip.gg、ViralityGG 等）创建、编辑和上传短视频。

## 快速开始

### 一键制作视频
```bash
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/make_whop_video.sh
```

这会自动：
1. 下载 Google Drive 素材
2. 用 ffmpeg 剪辑成竖屏格式
3. 上传到 Google Drive daily_english 文件夹

### 输出示例
```
✅ 视频制作完成！

📋 视频信息：
  文件名: 20260329_1908_flip_gg.mp4
  规格: 1080x1920 (竖屏 9:16)
  时长: 30秒

📍 云盘位置：
  Google Drive / daily_english / 20260329_1908_flip_gg.mp4
```

## 文件结构

```
whop-video-make/
├── SKILL.md                          # 完整文档
├── README.md                         # 此文件
├── scripts/
│   ├── make_whop_video.sh           # 一键制作（推荐）
│   ├── download_materials.sh        # 下载素材
│   ├── edit_video.sh                # ffmpeg 编辑
│   └── upload_to_gdrive.sh          # 上传到云盘
└── examples/
    ├── flip_gg_example.md           # Flip.gg 示例
    └── custom_workflow.md           # 自定义工作流
```

## 项目支持

### Flip.gg Street Interviews
- **默认素材**: Google Drive Folder ID `1pLXBhcOOahs4Lgag52rCdirqe_QF4lwE`
- **上传目标**: Google Drive `daily_english` 文件夹
- **视频格式**: 竖屏 9:16 (1080x1920)
- **时长**: 30 秒
- **标签**: `#viralityflip`
- **预期收益**: $1.25/1k views ($1-$500 per video)

## 依赖

- ffmpeg
- gdown
- rclone (配置了 daily_english remote)
- bash

安装：
```bash
sudo apt install ffmpeg -y
pip install gdown -q
# rclone 应该已通过 tiktok-video-make 配置
```

## 集成

此 skill 基于并集成了 `tiktok-video-make` 的最佳实践：
- 共享上传脚本和代理配置
- 一致的文件命名规范 (YYYYMMDD_HHMM)
- rclone Google Drive 集成

## 参考

- Whop 平台: https://whop.com
- FFmpeg 文档: https://ffmpeg.org
- TikTok 视频规格: https://www.tiktok.com/creator/creator-portal/

---

**制作者**: Irving
**创建日期**: 2026-03-29
**版本**: 1.0
