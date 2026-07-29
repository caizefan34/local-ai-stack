# 📚 Knowledge Base Import Tools

Tools for importing data into FastGPT knowledge bases.

## GitHub Repos → Knowledge Base

Import GitHub repositories as searchable knowledge:

```bash
# Import repos directly
python knowledge-base/import_github_repos.py --repos "https://github.com/user/repo1,https://github.com/user/repo2"

# Or sync from config
python knowledge-base/sync_github_to_fastgpt.py
```

## CC Switch Chats → Knowledge Base

Extract Q&A pairs from CC Switch logs for training data:

```bash
# Extract from Codex logs
python knowledge-base/ccswitch_extract.py --output ./train_data.json

# Or use the unified data preparation script
python scripts/automation/prepare_lora_data.py --source ccswitch --max 500
```

## Format

All tools output Alpaca-format JSON:
```json
{
  "instruction": "user question",
  "input": "additional context (optional)",
  "output": "model response"
}
```
