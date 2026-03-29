#!/bin/bash
# Upload file to Google Drive daily_english folder
# Automatically adds timestamp to filename if not present
# Usage: ./upload_to_gdrive.sh file.mp4

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 file_to_upload"
    exit 1
fi

FILE="$1"

if [ ! -f "$FILE" ]; then
    echo "Error: File '$FILE' not found"
    exit 1
fi

# Extract filename and extension
BASENAME=$(basename "$FILE")
FILENAME="${BASENAME%.*}"
EXT="${BASENAME##*.}"

# Check if filename already has timestamp pattern (YYYYMMDD_HHMM)
if [[ "$FILENAME" =~ ^[0-9]{8}_[0-9]{4}_ ]]; then
    # Already has timestamp, use as-is
    UPLOAD_NAME="$BASENAME"
else
    # Add timestamp
    TIMESTAMP=$(date +%Y%m%d_%H%M)
    UPLOAD_NAME="${TIMESTAMP}_${BASENAME}"
fi

export PATH=~/.local/bin:$PATH
export http_proxy=http://135.245.192.7:8000
export https_proxy=http://135.245.192.7:8000

echo "Uploading $FILE as $UPLOAD_NAME to daily_english:daily_english..."
rclone copyto "$FILE" "daily_english:daily_english/$UPLOAD_NAME" -P

echo "✅ Upload complete: $UPLOAD_NAME"
