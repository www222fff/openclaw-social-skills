#!/bin/bash
# Merge audio with video (audio duration as base)
# Usage: ./merge_audio_video.sh video.mp4 audio.mp3 [output_name] [video_volume] [audio_volume]

set -e

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 input_video input_audio [output_name] [video_volume] [audio_volume]"
    echo "Example: $0 video.mp4 audio.mp3 final 0.05 3.0"
    exit 1
fi

VIDEO="$1"
AUDIO="$2"
TIMESTAMP=$(date +%Y%m%d_%H%M)
OUTPUT_NAME="${3:-merged}"
OUTPUT="${TIMESTAMP}_${OUTPUT_NAME}.mp4"
VIDEO_VOL="${4:-0.05}"  # Default 5%
AUDIO_VOL="${5:-3.0}"   # Default 300%

if [ ! -f "$VIDEO" ]; then
    echo "Error: Video file '$VIDEO' not found"
    exit 1
fi

if [ ! -f "$AUDIO" ]; then
    echo "Error: Audio file '$AUDIO' not found"
    exit 1
fi

ffmpeg -i "$VIDEO" -i "$AUDIO" \
  -filter_complex "[0:a]volume=${VIDEO_VOL}[a0];[1:a]volume=${AUDIO_VOL}[a1];[a0][a1]amix=inputs=2:duration=shortest[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -shortest \
  "$OUTPUT" -y

echo "✅ Merged video created: $OUTPUT (video vol: ${VIDEO_VOL}, audio vol: ${AUDIO_VOL})"
