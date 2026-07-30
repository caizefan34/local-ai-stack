# Local AI Stack for VS Code

This extension connects VS Code to the configured Ollama-compatible endpoint.
It offers a sidebar chat, right-click commands to explain a selection, suggest
an unapplied fix diff, or generate unit tests in a new preview document.

Inline completion is privacy opt-in: set
`localAiStack.inlineCompletionsEnabled` to `true` in a trusted workspace. When
enabled, only supported code files send a bounded prefix to the configured
endpoint. Requests have a configurable timeout via
`localAiStack.requestTimeoutMs`. Rating an answer writes an approved-up or
unapproved-down JSONL record to the configured workspace-relative feedback
path; review records before training and keep secrets out of prompts.

To try it locally, open this `ide/vscode` folder itself in VS Code and press
`F5`. Choose **Run Local AI Stack Extension** if VS Code asks for a launch
configuration; it opens an Extension Development Host window. You can also run
**Extensions: Install from VSIX** after packaging with
`npx @vscode/vsce package`. Install code mode first:

```powershell
.\scripts\setup.ps1 -CodeMode
```
