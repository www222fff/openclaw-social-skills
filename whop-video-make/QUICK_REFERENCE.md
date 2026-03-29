# Whop Video Maker - 快速参考

## 🚀 立即使用

```bash
# 一键制作 + 上传
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/make_whop_video.sh
```

## 📂 脚本列表

| 脚本 | 功能 | 命令 |
|------|------|------|
| make_whop_video.sh | 一键制作 + 上传 | `bash scripts/make_whop_video.sh` |
| download_materials.sh | 下载素材 | `bash scripts/download_materials.sh --folder-id "ID"` |
| edit_video.sh | 编辑视频 | `bash scripts/edit_video.sh --input video.MOV --output out.mp4` |
| upload_to_gdrive.sh | 上传到云盘 | `bash scripts/upload_to_gdrive.sh video.mp4` |

## 💾 文件路径

```
Skill 目录:     ~/.openclaw/workspace/skills/whop-video-make/
脚本目录:       ~/.openclaw/workspace/skills/whop-video-make/scripts/
工作目录:       ~/.openclaw/workspace/downloads/whop_videos/
云盘目标:       Google Drive / daily_english
```

## 🎬 工作流

```
素材库 (Google Drive)
    ↓
下载 (gdown)
    ↓
编辑 (ffmpeg) → 竖屏 1080x1920 → 30秒
    ↓
上传 (rclone) → Google Drive daily_english
    ↓
发布 (Whop) → TikTok / Instagram
```

## 📊 Flip.gg 项目参数

| 参数 | 值 |
|------|-----|
| 素材库 ID | `1pLXBhcOOahs4Lgag52rCdirqe_QF4lwE` |
| 输出格式 | 竖屏 9:16 (1080x1920) |
| 时长 | 30 秒 |
| 编码 | H.264 + AAC 128kbps |
| 标签 | #viralityflip |
| 收益 | $1.25/1k views |

## 🔧 常用命令

### 制作视频
```bash
cd ~/.openclaw/workspace/skills/whop-video-make
bash scripts/make_whop_video.sh
```

### 自定义工作流
```bash
# 只下载
bash scripts/download_materials.sh

# 编辑（改为 45 秒）
bash scripts/edit_video.sh --input materials/video.MOV --output my.mp4 --duration 45

# 上传
bash scripts/upload_to_gdrive.sh my.mp4
```

### 直接用 ffmpeg
```bash
ffmpeg -i input.MOV -t 30 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
  -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k output.mp4 -y
```

## 📖 查看文档

```bash
# 完整技术文档
cat ~/.openclaw/workspace/skills/whop-video-make/SKILL.md

# 快速开始
cat ~/.openclaw/workspace/skills/whop-video-make/README.md

# Flip.gg 示例
cat ~/.openclaw/workspace/skills/whop-video-make/examples/flip_gg_example.md

# 创建总结
cat ~/.openclaw/workspace/skills/whop-video-make/CREATION_SUMMARY.md
```

## ✅ 检查表

在使用前确认：

- [ ] ffmpeg 已安装：`which ffmpeg`
- [ ] gdown 已安装：`pip list | grep gdown`
- [ ] rclone 已配置：`rclone listremotes | grep daily_english`
- [ ] 脚本可执行：`ls -l ~/.openclaw/workspace/skills/whop-video-make/scripts/`
- [ ] 网络正常（代理）：`curl -x http://135.245.192.7:8000 https://google.com`

## 🆘 常见问题

**Q: 提示 ffmpeg 找不到？**  
A: `sudo apt install ffmpeg -y`

**Q: 上传失败？**  
A: `rclone config` 检查 daily_english remote

**Q: 如何看上传进度？**  
A: 脚本已包含 `-P` 参数，会显示进度

**Q: 视频质量太大？**  
A: 编辑脚本，改 `-crf 28`（压缩更高）

**Q: 想要不同的素材库？**  
A: `bash scripts/download_materials.sh --folder-id "YOUR_ID"`

---

**版本**: 1.0  
**最后更新**: 2026-03-29  
**状态**: ✅ 生产就绪
