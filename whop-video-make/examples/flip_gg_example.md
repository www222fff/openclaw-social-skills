# Flip.gg Street Interviews 完整示例

这是一个完整的 Flip.gg 视频制作工作流示例。

## 背景

Flip.gg 是 Whop 平台上的创意项目，通过制作街头采访短视频赚钱。

- **平台**: TikTok / Instagram / YouTube
- **格式**: 竖屏短视频 (9:16)
- **时长**: 15-60 秒（推荐 30 秒）
- **收益**: $1.25/1k views ($1-$500 per video)
- **要求**: 40% US views，新账号，#viralityflip 标签

## 一键制作

最简单的方式：

```bash
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/make_whop_video.sh
```

这会完成以下步骤：
1. ✓ 从 Google Drive 下载素材
2. ✓ 选择第一个视频
3. ✓ 用 ffmpeg 提取 30 秒
4. ✓ 转换为竖屏 1080x1920
5. ✓ 添加黑边保持长宽比
6. ✓ 编码为 H.264 MP4
7. ✓ 上传到 Google Drive daily_english

### 输出

```
🎬 Whop Video Maker - 一键制作
==================================

📁 从 Google Drive 下载素材库...
✓ 可用素材：
-rw-rw-r-- 1 user user 9.6M Copy of IMG_2168.MOV
-rw-rw-r-- 1 user user 5.0M Copy of IMG_2169.MOV
...

📥 选择素材...
选中: Copy of IMG_2169.MOV
大小: 5.0M

🎬 用 ffmpeg 进行视频处理...
   - 目标时长: 30秒
   - 竖屏规格: 1080x1920 (9:16)

处理中...
✓ 视频编码完成
输出文件: 20260329_1908_flip_gg.mp4
文件大小: 15M

📤 上传到 Google Drive...
✓ 上传完成

✅ 视频制作完成！

📋 视频信息：
  文件名: 20260329_1908_flip_gg.mp4
  规格: 1080x1920 (竖屏 9:16)
  时长: 30秒
  编码: H.264 + AAC 128kbps

💡 后续步骤：
  1. 打开 Whop 项目页面
  2. 点击 'Submit Video'
  3. 从 daily_english 云盘选择视频
  4. 添加标签（如 #viralityflip）
  5. 提交

📍 云盘位置：
  Google Drive / daily_english / 20260329_1908_flip_gg.mp4

🎯 预期收益:
  CPM: $1.25 / 1k views
  单视频: $1 - $500
```

## 手动工作流

如果需要更多控制，分步操作：

### Step 1: 下载素材

```bash
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/download_materials.sh \
  --folder-id "1pLXBhcOOahs4Lgag52rCdirqe_QF4lwE" \
  --output "./materials"
```

### Step 2: 自定义编辑

```bash
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/edit_video.sh \
  --input "./materials/Copy of IMG_2169.MOV" \
  --output "my_video.mp4" \
  --duration 45 \
  --format vertical
```

参数：
- `--input`: 输入视频文件
- `--output`: 输出文件名
- `--duration`: 视频时长（秒），推荐 30
- `--format`: `vertical` 或 `horizontal`

### Step 3: 上传

```bash
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/upload_to_gdrive.sh \
  "my_video.mp4"
```

## 自定义 ffmpeg 处理

如果需要高级控制：

```bash
# 直接用 ffmpeg
ffmpeg -i input.MOV \
  -t 30 \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  output.mp4 -y

# 然后上传
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/upload_to_gdrive.sh output.mp4
```

## 提交到 Whop

1. 打开 https://whop.com/joined/viralitygg/content-rewards-bgZAk8OzoByw9n/app/
2. 选择 "Flip.gg [Street Interviews]" 项目
3. 点击 "Submit Video" 按钮
4. 选择 video file（从 Google Drive daily_english 下载）
5. 添加标签: `#viralityflip`
6. 提交

## 注意事项

### 视频质量
- 确保素材清晰
- 30 秒时长比较合适（平衡内容长度和上传速度）
- 竖屏格式适配 TikTok

### 地域要求
- 项目要求 40% US views
- 建议用美国 VPN 或新美国账号发布
- 前期可能需要多个视频测试

### 标签
- 必须添加 `#viralityflip`
- 其他可选标签：#streetinterview #flipgg

### 收益跟踪
- 每个视频自动跟踪 views
- 累积 $1 以上才能提现
- CPM $1.25，10k views = $12.50

## 常见问题

### Q: 视频上传失败？
A: 检查 Google Drive 和 rclone 配置：
```bash
rclone config
rclone listremotes
```

### Q: ffmpeg 找不到？
A: 安装 ffmpeg：
```bash
sudo apt install ffmpeg -y
```

### Q: 如何修改视频时长？
A: 编辑脚本或用参数：
```bash
# 修改环境变量
export VIDEO_DURATION=45
bash ~/.openclaw/workspace/skills/whop-video-make/scripts/make_whop_video.sh

# 或使用编辑脚本
bash scripts/edit_video.sh --input input.MOV --output output.mp4 --duration 45
```

### Q: 如何使用不同的素材库？
A: 传递 folder ID：
```bash
bash scripts/download_materials.sh --folder-id "YOUR_FOLDER_ID"
```

## 下一步

- 一次制作多个视频进行批量测试
- 根据平台反馈优化内容风格
- 跟踪不同素材的表现
- 建立自动化提交流程

---

**示例完成**: 2026-03-29
**项目**: Flip.gg Street Interviews
**预期收益**: $1.25/1k views
