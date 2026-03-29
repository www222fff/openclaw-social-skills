#!/bin/bash
# TikTok Video Maker - Automated Pipeline
# 从指定账号下载高播放量音频，合并到随机视频，上传到Google Drive
# Usage: ./auto_make_video.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE=~/.openclaw/workspace/downloads
HISTORY_FILE="$WORKSPACE/.download_history.txt"
VIDEO_DIR="$WORKSPACE/videos"

# TikTok accounts to fetch from
ACCOUNTS=("motivationversum" "truthful_motivation")

# Ensure workspace and history exist
mkdir -p "$WORKSPACE" "$VIDEO_DIR"
touch "$HISTORY_FILE"

echo "🎬 TikTok Video Maker - Auto Pipeline"
echo "======================================"

# Step 1: Get available videos
echo ""
echo "📹 Step 1: Checking available videos..."
VIDEO_FILES=("$VIDEO_DIR"/video*.mp4)

if [ ! -e "${VIDEO_FILES[0]}" ]; then
    echo "❌ Error: No video files found in $VIDEO_DIR"
    echo "   Please add video1.mp4, video2.mp4, etc. to $VIDEO_DIR"
    exit 1
fi

VIDEO_COUNT=${#VIDEO_FILES[@]}
echo "   Found $VIDEO_COUNT video(s)"

# Step 2: Randomly select a video
RANDOM_INDEX=$((RANDOM % VIDEO_COUNT))
SELECTED_VIDEO="${VIDEO_FILES[$RANDOM_INDEX]}"
VIDEO_NAME=$(basename "$SELECTED_VIDEO")
echo "   Selected: $VIDEO_NAME"

# Step 3: Check for new high-view TikTok audio
echo ""
echo "🎵 Step 2: Fetching high-view TikTok videos..."
echo "   (This requires browser automation - will be handled by OpenClaw agent)"
echo ""
echo "   Accounts: ${ACCOUNTS[@]}"
echo "   History file: $HISTORY_FILE"
echo ""
echo "⚠️  Next steps require OpenClaw agent to:"
echo "   1. Open TikTok with browser tool (profile=openclaw)"
echo "   2. For each account in ${ACCOUNTS[@]}:"
echo "      - Navigate to https://www.tiktok.com/@{account}"
echo "      - Extract video list with view counts (use evaluate)"
echo "      - Filter videos NOT in $HISTORY_FILE"
echo "      - Select top 3 by views"
echo "   3. Pick one randomly and download audio"
echo "   4. Record video ID to $HISTORY_FILE"
echo "   5. Merge with $SELECTED_VIDEO"
echo "   6. Upload to Google Drive"
echo ""
echo "   Run this script through OpenClaw agent for full automation."

# If called directly (not from agent), exit with instructions
if [ -z "$OPENCLAW_SESSION" ]; then
    echo ""
    echo "💡 To run full automation, tell OpenClaw agent:"
    echo "   \"Execute tiktok-video-make auto pipeline\""
    exit 0
fi

# The rest will be handled by OpenClaw agent
echo ""
echo "✅ Script ready. Waiting for agent to continue..."
