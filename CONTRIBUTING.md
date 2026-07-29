# Contributing to Local AI Stack

Thank you for your interest in contributing to **Local AI Stack** ¡ª a production-grade, 100% local RAG system. We welcome contributions of all kinds: bug reports, feature suggestions, documentation improvements, and code changes.

> **Note:** By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## How to Report Bugs

If you find a bug, please [open a GitHub Issue](https://github.com/caizefan34/local-ai-stack/issues/new) and include:

- A clear, descriptive title
- Steps to reproduce the bug (minimal and reproducible)
- Expected behavior vs. actual behavior
- Environment details (OS, Docker version, Ollama version, RAM/VRAM)
- Logs or screenshots if relevant

## How to Suggest Features

Feature requests are welcome! [Open a Feature Request](https://github.com/caizefan34/local-ai-stack/issues/new) with:

- A clear description of the problem you want to solve
- Your proposed solution (be as specific as possible)
- Any alternative approaches you have considered
- Why this would benefit the community

## How to Submit Pull Requests

1. **Fork** the repository
2. **Create a branch** with a descriptive name:
   - `fix/` for bug fixes (e.g., `fix/reranker-oom-error`)
   - `feat/` for new features (e.g., `feat/ollama-api-support`)
   - `docs/` for documentation changes (e.g., `docs/update-quickstart`)
3. **Make your changes** ¡ª keep them focused and minimal
4. **Test your changes** ¡ª ensure existing functionality is not broken
5. **Push** your branch to your fork
6. **Open a Pull Request** against the `main` branch

In your PR description, please reference any related issues and summarize the changes you made.

---

## Development Setup

### Prerequisites
- Git
- Docker & Docker Compose
- PowerShell (Windows) or Bash (Linux/macOS)

### Quick Start

```bash
git clone https://github.com/caizefan34/local-ai-stack.git
cd local-ai-stack
docker compose -f docker/docker-compose.yml up -d
```

For Windows, follow the [Quick Start](README.md#-quick-start) guide in the README.

---

## Code Style Guidelines

- **Shell scripts (`.ps1` / `.sh`):** Use consistent indentation (2 spaces). Prefer `Write-Host` / `echo` for status messages.
- **Python:** Follow [PEP 8](https://peps.python.org/pep-0008/). Use 4-space indentation.
- **Markdown:** Use semantic line breaks (one sentence per line). Keep line lengths readable (~80 characters).
- **Docker:** Use explicit image tags (avoid `latest`). Keep layers minimal.
- **Commit messages:** Use concise, descriptive messages in the present tense (e.g., "Add reranker health check", "Fix sync pipeline timeout").

---

## Code of Conduct

Please note that this project has a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold it.

---

*Happy contributing! ??*
