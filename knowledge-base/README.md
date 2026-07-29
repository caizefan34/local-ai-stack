# 📚 Knowledge Base Import Tools

Tools for importing data into FastGPT knowledge bases.

## GitHub Repos → Knowledge Base

Import GitHub repositories as searchable knowledge:

```bash
python import_github_repos.py --repos "https://github.com/user/repo1,https://github.com/user/repo2"
```

## CC Switch Chats → Knowledge Base

Export your Codex/CC Switch conversation logs as Q&A training data:

```bash
python import_ccswitch_logs.py --output ./train_data.json
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
