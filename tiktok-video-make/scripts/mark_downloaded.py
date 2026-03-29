#!/usr/bin/env python3
"""
标记视频为已下载
Usage: python3 mark_downloaded.py <video_id>
"""

import sys
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw/workspace/downloads"
FALLBACK_FILE = WORKSPACE / ".tiktok_fallback.json"

def mark_video_downloaded(video_id):
    """标记视频为已下载"""
    if not FALLBACK_FILE.exists():
        print(f"❌ Error: {FALLBACK_FILE} not found")
        sys.exit(1)
    
    with open(FALLBACK_FILE, 'r') as f:
        data = json.load(f)
    
    videos = data.get("videos", [])
    found = False
    
    for v in videos:
        if v["videoId"] == video_id:
            v["downloaded"] = True
            found = True
            break
    
    if not found:
        print(f"⚠️  Warning: Video ID {video_id} not found in list")
        sys.exit(1)
    
    data["videos"] = videos
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open(FALLBACK_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # 统计
    total = len(videos)
    downloaded = len([v for v in videos if v.get("downloaded", False)])
    available = total - downloaded
    
    print(f"✅ Marked {video_id} as downloaded")
    print(f"📊 Stats: {downloaded}/{total} downloaded, {available} available")
    
    if available == 0:
        print()
        print("⚠️  All videos have been downloaded!")
        print("   Please re-scrape TikTok to add new videos to the list")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mark_downloaded.py <video_id>")
        sys.exit(1)
    
    video_id = sys.argv[1]
    mark_video_downloaded(video_id)
