# Whop Video Maker Skill - 文件索引

## 📚 文档文件

| 文件 | 说明 | 对象 |
|------|------|------|
| **SKILL.md** | 完整技术文档 + API 说明 | 开发者/高级用户 |
| **README.md** | 快速开始指南 | 新用户 |
| **QUICK_REFERENCE.md** | 快速参考卡 | 日常使用 |
| **CREATION_SUMMARY.md** | 创建过程总结 | 历史记录 |
| **INDEX.md** | 此文件 | 导航 |

## 🛠️ 脚本文件

所有脚本位于 `scripts/` 目录：

| 脚本 | 用途 | 依赖 |
|------|------|------|
| **make_whop_video.sh** | 一键制作（推荐） | ffmpeg, gdown, rclone |
| **download_materials.sh** | 下载素材 | gdown |
| **edit_video.sh** | 编辑视频 | ffmpeg |
| **upload_to_gdrive.sh** | 上传到云盘 | rclone |

## 📖 示例文件

位于 `examples/` 目录：

| 文件 | 内容 |
|------|------|
| **flip_gg_example.md** | Flip.gg 完整工作流示例 |

## 🎯 快速导航

### 我是第一次使用
→ 阅读 **README.md**

### 我需要快速参考
→ 查看 **QUICK_REFERENCE.md**

### 我需要详细技术文档
→ 阅读 **SKILL.md**

### 我要使用 Flip.gg 项目
→ 查看 **examples/flip_gg_example.md**

### 我要运行脚本
→ 执行 **scripts/make_whop_video.sh**

## 📊 Skill 统计

```
总文件数:    8 个
文档大小:    ~20KB
脚本大小:    ~9KB
总计:        ~29KB

脚本数量:    4 个可执行脚本
文档数量:    5 个文档

支持项目:    Flip.gg Street Interviews + 可扩展
```

## 🔗 快速链接

```bash
# 一键开始
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/make_whop_video.sh

# 查看所有文档
cd ~/.openclaw/workspace/skills/whop-video-make
ls -lah
```

---

**最后更新**: 2026-03-29  
**版本**: 1.0  
**状态**: ✅ 完成
