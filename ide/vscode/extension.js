const vscode = require('vscode');

function settings() {
  const config = vscode.workspace.getConfiguration('localAiStack');
  return { url: config.get('ollamaUrl'), codeModel: config.get('codeModel'), completionModel: config.get('completionModel'), feedbackPath: config.get('feedbackPath') };
}

async function generate(prompt, model) {
  const { url } = settings();
  const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ model, prompt, stream: false, options: { temperature: 0.1, num_predict: 256 } }) });
  if (!response.ok) throw new Error(`Ollama returned ${response.status}`);
  return (await response.json()).response || '';
}

class ChatViewProvider {
  async recordFeedback(prompt, response, rating) {
    const folder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
    if (!folder || !prompt || !response || !['up', 'down'].includes(rating)) throw new Error('Open a workspace and receive an answer before rating it.');
    const relativePath = settings().feedbackPath.replaceAll('\\', '/');
    const path = vscode.Uri.joinPath(folder.uri, ...relativePath.split('/'));
    const line = `${JSON.stringify({ prompt, response, rating, approved: true, source: 'vscode', created_at: new Date().toISOString() })}\n`;
    await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(folder.uri, ...relativePath.split('/').slice(0, -1)));
    let existing = new Uint8Array();
    try { existing = await vscode.workspace.fs.readFile(path); } catch (error) { if (error.code !== 'FileNotFound') throw error; }
    await vscode.workspace.fs.writeFile(path, Buffer.concat([Buffer.from(existing), Buffer.from(line, 'utf8')]));
  }

  resolveWebviewView(view) {
    view.webview.options = { enableScripts: true };
    view.webview.html = `<!doctype html><html><body>
      <style>body{font-family:var(--vscode-font-family);padding:8px}textarea{width:100%;box-sizing:border-box}button{margin-top:8px}pre{white-space:pre-wrap;word-break:break-word}</style>
      <textarea id="prompt" rows="5" placeholder="Ask about the current code..."></textarea><button id="send">Send</button><pre id="answer"></pre><div id="feedback" style="display:none"><button id="thumb-up" title="Useful answer">👍</button><button id="thumb-down" title="Needs correction">👎</button></div>
      <script>const api=acquireVsCodeApi();const prompt=document.getElementById('prompt');const answer=document.getElementById('answer');document.getElementById('send').onclick=()=>{answer.textContent='Thinking…';api.postMessage({type:'chat',text:prompt.value})};window.addEventListener('message',e=>answer.textContent=e.data.answer);</script>
      <script>let lastPrompt='';let lastAnswer='';for(const rating of ['up','down'])document.getElementById('thumb-'+rating).onclick=()=>{document.getElementById('feedback').style.display='none';api.postMessage({type:'feedback',rating,prompt:lastPrompt,response:lastAnswer})};window.addEventListener('message',e=>{if(e.data.prompt&&e.data.answer){lastPrompt=e.data.prompt;lastAnswer=e.data.answer;document.getElementById('feedback').style.display='block'}});</script></body></html>`;
    view.webview.onDidReceiveMessage(async ({ type, text, prompt, response, rating }) => {
      if (type === 'feedback') {
        try { await this.recordFeedback(prompt, response, rating); view.webview.postMessage({ answer: 'Feedback saved locally. Review it before LoRA training.' }); }
        catch (error) { view.webview.postMessage({ answer: `Feedback was not saved: ${error.message}` }); }
        return;
      }
      if (type !== 'chat' || !String(text).trim()) return;
      try {
        const editor = vscode.window.activeTextEditor;
        const selection = editor && !editor.selection.isEmpty ? `\n\nSelected code:\n${editor.document.getText(editor.selection)}` : '';
        const answer = await generate(`${text}${selection}`, settings().codeModel);
        view.webview.postMessage({ answer, prompt: text });
      } catch (error) { view.webview.postMessage({ answer: `Local AI request failed: ${error.message}` }); }
    });
  }
}

function activate(context) {
  context.subscriptions.push(vscode.window.registerWebviewViewProvider('localAiStack.chat', new ChatViewProvider()));
  context.subscriptions.push(vscode.commands.registerCommand('localAiStack.explainSelection', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.selection.isEmpty) return vscode.window.showInformationMessage('Select code to explain first.');
    try {
      const text = editor.document.getText(editor.selection);
      const answer = await generate(`Explain this code concisely. Mention bugs or risks when present.\n\n${text}`, settings().codeModel);
      const document = await vscode.workspace.openTextDocument({ content: answer, language: 'markdown' });
      await vscode.window.showTextDocument(document, { preview: true });
    } catch (error) { vscode.window.showErrorMessage(`Local AI request failed: ${error.message}`); }
  }));
  context.subscriptions.push(vscode.commands.registerCommand('localAiStack.fixSelection', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.selection.isEmpty) return vscode.window.showInformationMessage('Select an error, stack trace, or code region first.');
    try {
      const text = editor.document.getText(editor.selection);
      const answer = await generate(`Diagnose this code or error. Return a minimal unified diff only; do not apply it.\n\n${text}`, settings().codeModel);
      const document = await vscode.workspace.openTextDocument({ content: answer, language: 'diff' });
      await vscode.window.showTextDocument(document, { preview: true });
    } catch (error) { vscode.window.showErrorMessage(`Local AI request failed: ${error.message}`); }
  }));
  context.subscriptions.push(vscode.commands.registerCommand('localAiStack.generateTests', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.selection.isEmpty) return vscode.window.showInformationMessage('Select code to generate tests for first.');
    try {
      const text = editor.document.getText(editor.selection);
      const answer = await generate(`Generate focused unit tests for this selection. State assumptions, use the surrounding project test style when visible, and return test code only. Do not write files.\n\n${text}`, settings().codeModel);
      const document = await vscode.workspace.openTextDocument({ content: answer, language: editor.document.languageId });
      await vscode.window.showTextDocument(document, { preview: true });
    } catch (error) { vscode.window.showErrorMessage(`Local AI request failed: ${error.message}`); }
  }));
  context.subscriptions.push(vscode.languages.registerInlineCompletionItemProvider({ pattern: '**' }, {
    async provideInlineCompletionItems(document, position) {
      const prefix = document.getText(new vscode.Range(new vscode.Position(Math.max(0, position.line - 80), 0), position)).slice(-12000);
      if (!prefix.trim()) return [];
      try {
        const text = await generate(`Complete only the next code tokens. Do not explain.\n\n${prefix}`, settings().completionModel);
        return text ? [new vscode.InlineCompletionItem(text, new vscode.Range(position, position))] : [];
      } catch { return []; }
    }
  }));
}

function deactivate() {}
module.exports = { activate, deactivate };
