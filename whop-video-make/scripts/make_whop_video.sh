#!/bin/bash

# Whop Video Maker - 一键制作 + 上传
# 用于 Whop 创意项目（Flip.gg, ViralityGG 等）
# 自动下载素材、剪辑、上传到 Google Drive

set -e

# ============ 配置 ============
WORK_DIR="$HOME/.openclaw/workspace/downloads/whop_videos"
MATERIALS_FOLDER_ID="${1:-1pLXBhcOOahs4Lgag52rCdirqe_QF4lwE}"  # Flip.gg 默认
UPLOAD_REMOTE="daily_english:daily_english"
PROXY="http://135.245.192.7:8000"
PROJECT_NAME="${PROJECT_NAME:-flip_gg}"

# TikTok 竖屏规格
VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920
VIDEO_DURATION="${VIDEO_DURATION:-30}"  # 秒

mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "🎬 Whop Video Maker - 一键制作"
echo "=================================="
echo ""

# ============ Step 1: 下载素材 ============
echo "📁 从 Google Drive 下载素材库..."
echo "文件夹 ID: $MATERIALS_FOLDER_ID"

export http_proxy=$PROXY
export https_proxy=$PROXY

MATERIALS_DIR="$WORK_DIR/materials"
mkdir -p "$MATERIALS_DIR"

# 尝试用 gdown 下载（带超时和错误处理）
timeout 120 gdown --folder "https://drive.google.com/drive/folders/$MATERIALS_FOLDER_ID" \
    -O "$MATERIALS_DIR" \
    --quiet 2>/dev/null || {
    echo "⚠️  文件夹下载有问题，继续寻找本地或已缓存的素材..."
}

# 列出已有素材
echo ""
echo "✓ 可用素材："
if [ -d "$MATERIALS_DIR" ] && [ "$(ls -A $MATERIALS_DIR)" ]; then
    ls -lh "$MATERIALS_DIR"/*.{MOV,mp4,m4v} 2>/dev/null | head -5 || echo "未找到视频文件"
else
    echo "素材目录为空或不存在"
fi

# ============ Step 2: 选择素材 ============
echo ""
echo "📥 选择素材..."

SOURCE_FILE=$(find "$MATERIALS_DIR" -type f \( -iname "*.MOV" -o -iname "*.mp4" -o -iname "*.m4v" \) 2>/dev/null | head -1)

if [ -z "$SOURCE_FILE" ]; then
    echo "❌ 没有找到视频素材"
    echo "💡 提示: 确保 Google Drive 文件夹中有 .MOV 或 .mp4 文件"
    exit 1
fi

echo "选中: $(basename "$SOURCE_FILE")"
echo "大小: $(du -h "$SOURCE_FILE" | cut -f1)"

# ============ Step 3: 用 ffmpeg 剪辑 ============
echo ""
echo "🎬 用 ffmpeg 进行视频处理..."
echo "   - 目标时长: ${VIDEO_DURATION}秒"
echo "   - 竖屏规格: ${VIDEO_WIDTH}x${VIDEO_HEIGHT} (9:16)"

# 生成时间戳文件名
OUTPUT_NAME="$(date +%Y%m%d_%H%M)_${PROJECT_NAME}.mp4"
OUTPUT_PATH="$WORK_DIR/$OUTPUT_NAME"

# ffmpeg 处理
ffmpeg -i "$SOURCE_FILE" \
    -t $VIDEO_DURATION \
    -vf "scale=$VIDEO_WIDTH:$VIDEO_HEIGHT:force_original_aspect_ratio=decrease,pad=$VIDEO_WIDTH:$VIDEO_HEIGHT:(ow-iw)/2:(oh-ih)/2:black" \
    -c:v libx264 \
    -preset fast \
    -crf 23 \
    -c:a aac \
    -b:a 128k \
    "$OUTPUT_PATH" \
    -y 2>&1 | grep -E "(frame=|time=|Muxing)" | tail -3

if [ ! -f "$OUTPUT_PATH" ]; then
    echo "❌ 视频编码失败"
    exit 1
fi

echo ""
echo "✓ 视频编码完成"
echo "输出文件: $OUTPUT_NAME"
echo "文件大小: $(du -h "$OUTPUT_PATH" | cut -f1)"

# ============ Step 4: 上传到 Google Drive ============
echo ""
echo "📤 上传到 Google Drive..."

# 使用 tiktok-video-make 的上传脚本
UPLOAD_SCRIPT="$HOME/.openclaw/workspace/skills/tiktok-video-make/scripts/upload_to_gdrive.sh"

if [ -f "$UPLOAD_SCRIPT" ]; then
    bash "$UPLOAD_SCRIPT" "$OUTPUT_PATH"
else
    echo "⚠️  上传脚本不存在，使用 rclone 直接上传..."
    export PATH=~/.local/bin:$PATH
    rclone copy "$OUTPUT_PATH" "$UPLOAD_REMOTE" \
        --http-proxy "$PROXY" \
        -P || echo "⚠️  上传可能有问题，请检查 rclone 配置"
fi

echo "✓ 上传完成"

# ============ Step 5: 生成摘要 ============
echo ""
echo "✅ 视频制作完成！"
echo ""
echo "📋 视频信息："
echo "  文件名: $OUTPUT_NAME"
echo "  规格: ${VIDEO_WIDTH}x${VIDEO_HEIGHT} (竖屏 9:16)"
echo "  时长: ${VIDEO_DURATION}秒"
echo "  编码: H.264 + AAC 128kbps"
echo ""
echo "💡 后续步骤："
echo "  1. 打开 Whop 项目页面"
echo "  2. 点击 'Submit Video'"
echo "  3. 从 daily_english 云盘选择视频"
echo "  4. 添加标签（如 #viralityflip）"
echo "  5. 提交"
echo ""
echo "📍 云盘位置："
echo "  Google Drive / daily_english / $OUTPUT_NAME"
echo ""
echo "🎯 预期收益:"
echo "  CPM: $1.25 / 1k views"
echo "  单视频: $1 - $500"
echo ""
