#!/bin/bash
# FastGPT Knowledge Base Auto-Sync
# This script syncs files from Windows to WSL and imports them into FastGPT

set -e

echo "=== FastGPT KB Auto-Sync ==="
echo "Started: $(date)"

# Step 1: Sync files from Windows to WSL knowledge base
cd $HOME/knowledge-base/_scripts
python3 sync-from-windows.py
echo ""

# Step 2: Copy KB to mongo container  
echo "Step 2: Copying KB files to mongo container..."
docker exec fastgpt-mongo rm -rf /tmp/kb-files 2>/dev/null || true
docker exec fastgpt-mongo mkdir -p /tmp/kb-files
docker exec fastgpt tar -cf - -C /app/kb . 2>/dev/null | docker exec -i fastgpt-mongo tar -xf - -C /tmp/kb-files 2>/dev/null
echo "  Done"

# Step 3: Import new files into FastGPT
echo "Step 3: Importing new files into FastGPT dataset..."
RESULT=$(docker exec -i fastgpt-mongo mongosh --quiet --file /tmp/fastgpt-mongo-import.js 2>/dev/null)
echo "  $RESULT"

# Step 4: Cleanup
docker exec fastgpt-mongo rm -rf /tmp/kb-files 2>/dev/null || true

echo "=== Sync Complete: $(date) ==="
