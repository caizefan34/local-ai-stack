# Production hardening checklist

The default stack is intended for a single machine. Before making it reachable from another device:

- Keep `BIND_ADDRESS=127.0.0.1` unless FastGPT is behind an authenticated reverse proxy and a firewall.
- Keep `DATABASE_BIND_ADDRESS=127.0.0.1`. PostgreSQL, MongoDB, and Redis are application-internal services; do not expose their ports to a LAN or the public internet.
- Replace every placeholder and default database credential in `.env`. Treat `.env` as a secret and back it up separately from the repository.
- Pin container image tags and Python dependencies before deploying. Review model repositories before enabling any custom remote code.
- Back up the named Docker volumes before upgrades or any command using `docker compose down -v`; that command permanently deletes the database volumes.
- The VS Code inline completion feature is opt-in. It sends the current code prefix to the configured Ollama URL only in a trusted workspace and for known code languages.

For a remote deployment, prefer a private network or VPN and expose only FastGPT through TLS. The reranker should be reachable from FastGPT, but its request-size limits should remain enabled.
