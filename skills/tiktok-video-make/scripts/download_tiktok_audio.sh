#!/bin/bash
# Download audio directly from TikTok
# Usage: ./download_tiktok_audio.sh <TikTok_URL> [output_name]

set -e

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <TikTok_URL> [output_name]"
    echo "Example: $0 https://www.tiktok.com/@user/video/123456 my_audio"
    exit 1
fi

URL="$1"
TIMESTAMP=$(date +%Y%m%d_%H%M)
BASE_NAME="${2:-%(title)s}"
OUTPUT="${TIMESTAMP}_${BASE_NAME}"

cd ~/.openclaw/workspace/downloads

yt-dlp --proxy "http://135.245.192.7:8000" \
  --extract-audio --audio-format mp3 --audio-quality 0 \
  -o "${OUTPUT}.%(ext)s" \
  "$URL"

echo "✅ Audio downloaded to downloads/"
ls -lh *.mp3 | tail -1
