# Local AI Stack for VS Code

This extension connects VS Code directly to a local Ollama instance. It offers
a sidebar chat, inline completions from the 1.5B code model, and right-click
commands to explain a selection, suggest an unapplied fix diff, or generate
unit tests in a new preview document. It sends selected text and editor context
only to the configured local Ollama URL; it never writes a project file.

To try it locally, open this folder in VS Code and run **Extensions: Install
from VSIX** after packaging with `npx @vscode/vsce package`, or press `F5` from
an Extension Development Host. Install code mode first:

```powershell
.\scripts\setup.ps1 -CodeMode
```
