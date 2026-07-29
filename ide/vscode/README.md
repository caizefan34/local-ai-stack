# Local AI Stack for VS Code

This extension connects VS Code directly to a local Ollama instance. It offers
a sidebar chat, inline completions from the 1.5B code model, and right-click
commands to explain a selection, suggest an unapplied fix diff, or generate
unit tests in a new preview document. It sends selected text and editor context
only to the configured local Ollama URL; it never writes a project file.

To try it locally, open this `ide/vscode` folder itself in VS Code and press
`F5`. Choose **Run Local AI Stack Extension** if VS Code asks for a launch
configuration; it opens an Extension Development Host window. You can also run
**Extensions: Install from VSIX** after packaging with
`npx @vscode/vsce package`. Install code mode first:

```powershell
.\scripts\setup.ps1 -CodeMode
```
