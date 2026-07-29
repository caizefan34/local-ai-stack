#!/bin/bash
# Knowledge Base Update Checker
# Checks GitHub repos for updates

KB_HOME="${KB_HOME:-$HOME/knowledge-base}"
REPOS_DIR="$KB_HOME/02_research/active/_repos"

echo "=== Checking GitHub Repo Updates ==="
echo "Date: $(date '+%Y-%m-%d %H:%M')"
echo ""

if [ ! -d "$REPOS_DIR" ]; then
    echo "No repos directory found."
    exit 0
fi

UPDATES=0
for repo in "$REPOS_DIR"/*/; do
    if [ -f "$repo/repo.meta.json" ]; then
        name=$(basename "$repo")
        echo -n "Checking $name... "
        
        # Try git fetch
        cd "$repo" 2>/dev/null
        if git remote -v &>/dev/null; then
            git fetch --depth=1 origin 2>/dev/null
            LOCAL=$(git rev-parse HEAD 2>/dev/null)
            REMOTE=$(git rev-parse origin/HEAD 2>/dev/null 2>/dev/null || git rev-parse origin/main 2>/dev/null || git rev-parse origin/master 2>/dev/null)
            if [ "$LOCAL" != "$REMOTE" ] && [ -n "$REMOTE" ]; then
                echo "UPDATE AVAILABLE"
                UPDATES=$((UPDATES + 1))
            else
                echo "up to date"
            fi
        else
            echo "no git remote"
        fi
    fi
done

echo ""
echo "=== Summary ==="
echo "Repos needing update: $UPDATES"
echo "Done."
