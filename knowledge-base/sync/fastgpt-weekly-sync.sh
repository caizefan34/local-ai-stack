#!/bin/bash
# FastGPT Knowledge Base Auto-Sync (with document extraction)
set -e
LOG_FILE="${KB_HOME:-$HOME/knowledge-base}/_scripts/auto-sync.log"

logn() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

logn "=== FastGPT KB Auto-Sync ==="

# Step 1: Sync files from Windows to WSL
logn "Step 1: Syncing from Windows..."
cd ${KB_HOME:-$HOME/knowledge-base}/_scripts
python3 sync-from-windows.py 2>&1 | tail -3 >> "$LOG_FILE" || true
logn "  Done"

# Step 2: Extract text from PDF/Office documents
logn "Step 2: Extracting text from documents..."
python3 ${KB_HOME:-$HOME/knowledge-base}/_scripts/extract-docs.py ${KB_HOME:-$HOME/knowledge-base} 2>&1 | tail -3 >> "$LOG_FILE" || true
logn "  Done"

# Step 3: Copy KB to containers
logn "Step 3: Updating containers..."
docker exec fastgpt rm -rf /app/kb 2>/dev/null || true
timeout 30 docker cp ${KB_HOME:-$HOME/knowledge-base} fastgpt:/app/kb 2>/dev/null
docker exec fastgpt-mongo rm -rf /tmp/kb-files 2>/dev/null || true
docker exec fastgpt-mongo mkdir -p /tmp/kb-files
docker exec fastgpt tar -cf - -C /app/kb . | docker exec -i fastgpt-mongo tar -xf - -C /tmp/kb-files
logn "  Done"

# Step 4: Import new files into FastGPT
logn "Step 4: Importing to FastGPT..."
RESULT=$(docker exec -i fastgpt-mongo mongosh --quiet --file /tmp/fastgpt-mongo-import.js 2>/dev/null)
logn "  $RESULT"

# Step 5: Verify and cleanup
docker exec fastgpt-mongo rm -rf /tmp/kb-files 2>/dev/null || true
logn "=== Done ==="
