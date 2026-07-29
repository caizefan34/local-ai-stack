# Local AI Stack for VS Code

This extension connects VS Code directly to a local Ollama instance. It offers
an **Explain Selection** command and inline completions from the 1.5B code
model. It sends selected text and editor context only to the configured local
Ollama URL.

To try it locally, open this folder in VS Code and run **Extensions: Install
from VSIX** after packaging with `npx @vscode/vsce package`, or press `F5` from
an Extension Development Host. Install code mode first:

```powershell
.\scripts\setup.ps1 -CodeMode
```
