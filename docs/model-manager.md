# One-click model download manager

The authenticated Dashboard includes a recommended Ollama model catalog. Operators and administrators can start a background download with one click; viewers can inspect installed models and download status.

The catalog is intentionally allowlisted:

- Qwen3 0.6B and 8B;
- Qwen2.5-Coder 1.5B and 7B;
- Nomic Embed Text.

The control plane invokes `ollama pull` through direct process arguments, never through a shell. It keeps the last 20 job states in memory and limits displayed command output. Downloads continue while the control-plane process is running; restart it if a machine reboot interrupts a job.
