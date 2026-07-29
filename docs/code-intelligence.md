# Code Intelligence

Local AI Stack can use separate local models for general chat, code generation,
and low-latency inline completion. The code-intelligence tools never upload a
repository to a cloud service.

## Install code mode

```powershell
.\scripts\setup.ps1 -CodeMode
# or: .\scripts\pull-models.ps1 -CodeMode
```

```bash
bash scripts/setup.sh --code-mode
# or: bash scripts/pull-models.sh --code-mode
```

This pulls `qwen2.5-coder:7b` for code generation and bug fixing, plus
`qwen2.5-coder:1.5b` for inline completion. The OpenCode config exposes both
models; select the 7B model for edits and the 1.5B model for short completions.

## FastGPT routing

FastGPT workflows are stored in a user's FastGPT database, so this repository
does not overwrite them. Add a **Condition** node before the chat model node:

1. Route to `qwen2.5-coder:7b` when the input contains a code fence, an error
   trace, or terms such as `bug`, `function`, `写代码`, `修复 bug`.
2. Route all other prompts to `qwen3:8b`.
3. For editor completion clients, use `qwen2.5-coder:1.5b`.

`code_intelligence/router.py` contains the deterministic rules and can be used
by a custom FastGPT HTTP/tool node without calling a model to make this choice.

## AST-aware code indexing

```bash
python code_intelligence/index_codebase.py /path/to/project --output code-index.json
```

The JSON output contains function/class/method chunks, signatures, docstrings,
per-file imports, called symbol names, and Python/JavaScript import edges. Use
these chunks as the source for a code-specific embedding model or import them
into a separate FastGPT code knowledge base. Keeping code and prose knowledge
bases separate lets each use an appropriate embedding model.

For local CodeBERT embeddings, install the optional dependencies and embed the
index. Code chunks receive the `code` embedding profile while ordinary prose
can remain on `nomic-embed-text`:

```bash
pip install -r code_intelligence/requirements-code-embeddings.txt
python code_intelligence/embed_chunks.py code-index.json --output code-embeddings.json
```

To include this index in the scheduled knowledge-base sync, set
`CODE_INDEX_ENABLED=true` and `LOCAL_AI_STACK_ROOT` in
`knowledge-base/sync/config.env`. Optionally set `CODE_INDEX_ROOT` to a specific
repository; otherwise the knowledge-base root is indexed.

## Safe execution and project operations

Run only user-approved commands with an isolated container:

```bash
python code_intelligence/sandbox.py --workspace /path/to/project \
  --image python:3.12-alpine --command "python -m pytest"
```

The sandbox has no network, a read-only project mount, no Linux capabilities,
PID/CPU/memory limits, and a short timeout. It cannot apply patches or run Git
operations. Keep project mutations outside the sandbox and present the exact
`git` command or patch to the user for explicit confirmation.

`code_intelligence/project_actions.py` provides two confirmation-gated local
operations (`commit` and `create-file`). It always previews a mutation first;
only the identical command with `--confirm` performs it.

## LSP and feedback

Start the lightweight local completion server with:

```bash
python code_intelligence/lsp_server.py
```

Point an LSP-capable editor at this stdio command. It implements
`textDocument/completion` and calls only the local Ollama API. A VS Code client
can use the same command through its LSP extension settings. The server keeps a
small in-memory LRU cache for identical recent prefix requests; it never writes
editor content to disk.

The included [`ide/vscode`](../ide/vscode) extension provides inline completion
and **Local AI: Explain Selection** / **Suggest Fix for Selection** using the
local Ollama API. Fixes are displayed as an unapplied diff; it never applies an
edit or executes a command on behalf of the user. Its chat answer includes
**thumbs-up** and **thumbs-down** buttons. A click is the explicit approval to
append that answer to the workspace-local, git-ignored
`lora-finetune/data/feedback.jsonl` (configurable with
`localAiStack.feedbackPath`); feedback still requires human review before LoRA
training.

Store fine-tuning feedback only after explicit approval:

```bash
python code_intelligence/feedback.py --approved --rating down \
  --prompt "..." --response "..." --correction "..."
```

Approved feedback is written to the git-ignored
`lora-finetune/data/feedback.jsonl`; review and redact it before converting it
to a training dataset.

The **Monthly Approved Feedback LoRA** workflow runs on the first day of each
month on a self-hosted GPU runner. Set its `LOCAL_AI_FEEDBACK_FILE` and
`LOCAL_AI_APPROVED_DATA_FILE` repository variables to absolute runner paths,
or provide both paths when dispatching it manually. It converts candidates but
refuses to train until the approved data file exists.

## Self-hosted quality gate

The **Local Code Quality Evaluation** workflow is manually dispatched on a
self-hosted runner labeled `ollama`. It runs a local benchmark and can compare
against a baseline JSON. The default regression limit is 3%; a larger decline
returns a failing workflow. Replace `benchmarks/codegen-smoke.json` with a
licensed HumanEval/MBPP-compatible dataset for a broader release gate.

On Windows, register the local machine once (requires an authenticated `gh`
CLI and Ollama) and then keep the runner process open:

```powershell
.\scripts\setup-actions-runner.ps1
& 'C:\local-ai-stack-runner\run.cmd'
```

The setup script obtains a short-lived registration token without printing or
persisting it, and registers labels `ollama,gpu`. After the runner appears
online in the repository's **Settings → Actions → Runners**, dispatch **Local
Code Quality Evaluation** from the Actions tab.
