#!/bin/bash

# 从 Google Drive 下载素材库
# Usage: ./download_materials.sh --folder-id "FOLDER_ID"

set -e

FOLDER_ID="${1:-1pLXBhcOOahs4Lgag52rCdirqe_QF4lwE}"
OUTPUT_DIR="${2:-.}"
PROXY="http://135.245.192.7:8000"

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --folder-id)
            FOLDER_ID="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

mkdir -p "$OUTPUT_DIR"

echo "📥 从 Google Drive 下载素材..."
echo "文件夹 ID: $FOLDER_ID"
echo "输出目录: $OUTPUT_DIR"
echo ""

export http_proxy=$PROXY
export https_proxy=$PROXY

# 尝试下载
if command -v gdown &> /dev/null; then
    echo "使用 gdown 下载..."
    timeout 120 gdown --folder "https://drive.google.com/drive/folders/$FOLDER_ID" \
        -O "$OUTPUT_DIR" \
        --quiet || echo "⚠️  下载超时或失败"
else
    echo "⚠️  gdown not found，尝试安装..."
    pip install gdown -q
    timeout 120 gdown --folder "https://drive.google.com/drive/folders/$FOLDER_ID" \
        -O "$OUTPUT_DIR" \
        --quiet || echo "⚠️  下载失败"
fi

# 列出下载的文件
echo ""
echo "✓ 下载完成。可用文件："
ls -lh "$OUTPUT_DIR"/*.{MOV,mp4,m4v} 2>/dev/null | head -10 || echo "未找到视频文件"
