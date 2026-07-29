# Knowledge Base Auto-Sync

Automated syncing and import pipeline for FastGPT knowledge bases.

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `sync-from-windows.py` | Sync files from Windows folders to WSL KB directory |
| `fastgpt-sync.py` | Sync/import files into FastGPT via API |
| `extract-docs.py` | Extract text from PDF/DOCX/PPTX files |
| `dedup.py` | Find and remove duplicate files |
| `add_course.py` | Interactive course material importer |
| `add_paper.py` | Interactive paper importer with metadata extraction |
| `add_github.py` | Clone and import GitHub repos |
| `check_updates.sh` | Check for updates to tracked GitHub repos |
| `report.py` | Generate KB status report |
| `fastgpt-weekly-sync.sh` | Full weekly sync orchestrator |
| `run-kb-sync.sh` | Quick one-shot sync runner |

## Setup

### 1. Windows → WSL Sync

The `sync-from-windows.py` script syncs files from Windows folders into WSL.
Set environment variables:

```bash
export KB_WINDOWS_SOURCE=/mnt/d/your-knowledge-folder
```

### 2. Scheduled Task (Windows)

Run as Administrator:

```powershell
.\scripts\setup_kb_sync_task.ps1
```

This creates a weekly scheduled task (Sunday 03:00) that runs the full sync pipeline.

### 3. Environment Variables

Copy `config.env.example` to `config.env` and adjust paths.
