#!/usr/bin/env python3
"""
TikTok Video Maker - Full Automation
从指定账号获取高播放量视频，下载音频，合并到随机视频，上传到Google Drive
"""

import os
import sys
import json
import random
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw/workspace/downloads"
VIDEOS_DIR = WORKSPACE / "videos"
HISTORY_FILE = WORKSPACE / ".download_history.json"
FALLBACK_FILE = WORKSPACE / ".tiktok_fallback.json"
ACCOUNTS = ["motivationversum", "truthful_motivation"]

def load_history():
    """加载下载历史"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {"downloaded_ids": [], "last_update": None}

def save_history(history):
    """保存下载历史"""
    history["last_update"] = datetime.now().isoformat()
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_random_video():
    """随机选择一个视频文件"""
    videos = list(VIDEOS_DIR.glob("video*.mp4"))
    if not videos:
        print(f"❌ Error: No video files found in {VIDEOS_DIR}")
        print(f"   Please add video1.mp4, video2.mp4, etc.")
        sys.exit(1)
    
    selected = random.choice(videos)
    print(f"📹 Selected video: {selected.name}")
    return selected

def extract_video_id(url):
    """从TikTok URL提取视频ID"""
    # URL format: https://www.tiktok.com/@user/video/7355634606177094945
    return url.split("/video/")[-1].split("?")[0] if "/video/" in url else None

def load_fallback_videos():
    """加载备选视频列表"""
    if FALLBACK_FILE.exists():
        with open(FALLBACK_FILE, 'r') as f:
            data = json.load(f)
            return data.get("videos", []), data
    return [], {}

def save_fallback_videos(data):
    """保存备选视频列表"""
    with open(FALLBACK_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_next_video():
    """从备选列表中选择下一个未下载的视频"""
    videos, data = load_fallback_videos()
    if not videos:
        return None, None
    
    # 过滤已下载的（使用 list 中的 downloaded 标识）
    available = [v for v in videos if not v.get("downloaded", False)]
    
    if not available:
        print("⚠️  All videos in fallback list have been downloaded")
        print("   Please re-scrape TikTok to add new videos")
        return None, None
    
    # 按播放量排序，返回最高的
    available.sort(key=lambda x: x.get("views", 0), reverse=True)
    return available[0], data

def mark_video_downloaded(video_id):
    """标记视频为已下载"""
    videos, data = load_fallback_videos()
    for v in videos:
        if v["videoId"] == video_id:
            v["downloaded"] = True
            break
    
    data["videos"] = videos
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    save_fallback_videos(data)
    print(f"✅ Marked {video_id} as downloaded in fallback list")

def main():
    print("🎬 TikTok Video Maker - Full Automation")
    print("=" * 50)
    
    # Step 1: 检查视频文件
    selected_video = get_random_video()
    
    # Step 2: 检查备选列表
    print(f"\n🔍 Checking fallback list...")
    next_video, fallback_data = get_next_video()
    
    if not next_video:
        print("❌ No available videos in fallback list")
        print("   Please re-scrape TikTok to update .tiktok_fallback.json")
        sys.exit(1)
    
    # 统计
    videos, _ = load_fallback_videos()
    total = len(videos)
    downloaded = len([v for v in videos if v.get("downloaded", False)])
    available = total - downloaded
    
    print(f"📊 Stats: {downloaded}/{total} downloaded, {available} available")
    print(f"✅ Selected: {next_video['viewText']} views - {next_video['videoId']}")
    print(f"   URL: {next_video['url']}")
    print()
    print("📋 Next steps for agent:")
    print("   1. Download audio from URL")
    print("   2. Merge with selected_video")
    print("   3. Upload to Google Drive")
    print("   4. Call mark_video_downloaded(video_id)")
    print()
    print(f"   Selected video: {selected_video}")
    
    return {
        "video": str(selected_video),
        "tiktok_video": next_video,
        "fallback_file": str(FALLBACK_FILE)
    }

if __name__ == "__main__":
    result = main()
    print()
    print("📊 Config for agent:")
    print(json.dumps(result, indent=2))
