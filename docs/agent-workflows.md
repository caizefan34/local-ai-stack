# Agent workflows

Local AI Stack includes bounded, read-only multi-step workflows. The model selects one tool at a time using strict JSON; the engine executes only registered workspace tools and returns the observation for the next step.

```bash
python -m agent_workflows "Find where feedback approval is enforced" --workspace .
python -m agent_workflows "Diagnose the failing sync test" --workflow code-diagnose --workspace . --json
```

Safety boundaries:

- maximum step and repeated-action budgets;
- no arbitrary shell, network tool, file write, commit, or patch application;
- real-path containment and denial of `.git`, `.env*`, credentials, keys, and certificates;
- file, search-result, and tool-output size limits;
- file contents are marked as untrusted and cannot redefine the workflow;
- the trace stores user-visible action summaries, not hidden chain-of-thought.

The initial workflows are `workspace-investigate` and `code-diagnose`. Both return reports or suggested fixes only. Execution and mutation can be added later through a separate one-use approval mechanism.
