#!/bin/bash

# ffmpeg 视频编辑 - 专用于竖屏 TikTok 格式
# Usage: ./edit_video.sh --input video.MOV --output output.mp4 [--duration 30] [--format vertical]

set -e

INPUT_FILE=""
OUTPUT_FILE=""
DURATION=30
FORMAT="vertical"  # vertical 或 horizontal

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --input|-i)
            INPUT_FILE="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --duration|-d)
            DURATION="$2"
            shift 2
            ;;
        --format|-f)
            FORMAT="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# 验证参数
if [ -z "$INPUT_FILE" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "❌ 缺少参数"
    echo "Usage: $0 --input video.MOV --output output.mp4 [--duration 30] [--format vertical]"
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ 输入文件不存在: $INPUT_FILE"
    exit 1
fi

# 验证 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg 未安装"
    echo "安装: sudo apt install ffmpeg -y"
    exit 1
fi

echo "🎬 ffmpeg 视频编辑"
echo "================="
echo "输入: $INPUT_FILE"
echo "输出: $OUTPUT_FILE"
echo "时长: ${DURATION}秒"
echo "格式: $FORMAT"
echo ""

# 根据格式设置分辨率
if [ "$FORMAT" = "vertical" ]; then
    WIDTH=1080
    HEIGHT=1920
    echo "🎯 竖屏规格: ${WIDTH}x${HEIGHT} (9:16 TikTok)"
else
    WIDTH=1920
    HEIGHT=1080
    echo "🎯 横屏规格: ${WIDTH}x${HEIGHT} (16:9)"
fi

echo ""
echo "处理中..."

# ffmpeg 处理
ffmpeg -i "$INPUT_FILE" \
    -t $DURATION \
    -vf "scale=$WIDTH:$HEIGHT:force_original_aspect_ratio=decrease,pad=$WIDTH:$HEIGHT:(ow-iw)/2:(oh-ih)/2:black" \
    -c:v libx264 \
    -preset fast \
    -crf 23 \
    -c:a aac \
    -b:a 128k \
    "$OUTPUT_FILE" \
    -y 2>&1 | grep -E "(frame=|time=|Muxing)" | tail -5

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "❌ 视频编码失败"
    exit 1
fi

echo ""
echo "✅ 编码完成！"
echo ""
echo "📊 输出信息："
echo "  文件: $OUTPUT_FILE"
echo "  大小: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "  规格: ${WIDTH}x${HEIGHT}"
echo "  编码: H.264 + AAC"
echo ""
