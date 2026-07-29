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
  renderHtml() {
    return `<!doctype html><html><body><main>
      <header><div class="brand-mark">&lt;/&gt;</div><div><h1>Local AI</h1><p><span class="status-dot"></span>Ollama is local</p></div></header>
      <section id="empty" class="welcome"><h2>How can I help?</h2><p>Ask about this workspace, explain selected code, or get a safe diff preview.</p><div class="suggestions"><button data-prompt="Explain the selected code and flag risks.">Explain selection</button><button data-prompt="Review the current file for bugs and edge cases.">Review current file</button><button data-prompt="Suggest focused unit tests for the selected code.">Generate tests</button></div></section>
      <section id="response" class="response" hidden><div class="response-label">LOCAL AI RESPONSE</div><pre id="answer"></pre><div id="feedback" class="feedback" hidden><span>Was this useful?</span><button id="thumb-up" title="Useful answer" aria-label="Useful answer">&#128077;</button><button id="thumb-down" title="Needs correction" aria-label="Needs correction">&#128078;</button></div></section>
      <form id="chat-form"><label for="prompt">Message</label><textarea id="prompt" rows="4" placeholder="Ask about the current code..." autofocus></textarea><div class="composer-footer"><span>Selected code is included automatically.</span><button id="send" type="submit">Send <span aria-hidden="true">&#8599;</span></button></div></form>
    </main><style>
      :root{--accent:#7c83ff;--accent-strong:#6269ed;--surface:color-mix(in srgb,var(--vscode-sideBar-background) 88%,#7c83ff);--line:var(--vscode-widget-border,rgba(128,128,128,.32));--muted:var(--vscode-descriptionForeground)}
      *{box-sizing:border-box}body{margin:0;color:var(--vscode-foreground);font-family:var(--vscode-font-family);font-size:13px}main{padding:14px 12px 12px}header{display:flex;align-items:center;gap:10px;margin:2px 2px 18px}.brand-mark{display:grid;place-items:center;width:34px;height:34px;border-radius:11px;background:linear-gradient(145deg,#969bff,#656ced);box-shadow:0 5px 14px rgba(90,97,230,.3);color:#fff;font-family:var(--vscode-editor-font-family);font-weight:800;font-size:12px}h1{font-size:15px;line-height:1.2;margin:0;font-weight:700}header p{margin:3px 0 0;color:var(--muted);font-size:11px}.status-dot{display:inline-block;width:6px;height:6px;margin:0 4px 1px 0;border-radius:50%;background:#57c785}.welcome{margin-bottom:16px;padding:14px;border:1px solid var(--line);border-radius:12px;background:linear-gradient(135deg,var(--surface),var(--vscode-sideBar-background))}.welcome h2{font-size:14px;margin:0 0 5px}.welcome p{margin:0;color:var(--muted);line-height:1.45}.suggestions{display:grid;gap:7px;margin-top:13px}.suggestions button{width:100%;padding:8px 10px;text-align:left;border:1px solid var(--line);border-radius:7px;background:var(--vscode-button-secondaryBackground);color:var(--vscode-button-secondaryForeground);cursor:pointer;font:inherit}.suggestions button:hover{border-color:var(--accent);background:var(--vscode-button-secondaryHoverBackground)}.response{margin:0 0 14px;padding:12px;border:1px solid var(--line);border-radius:12px;background:var(--vscode-editor-background);box-shadow:0 3px 12px rgba(0,0,0,.08)}.response-label{margin-bottom:9px;color:var(--accent);font-size:10px;font-weight:700;letter-spacing:.08em}pre{max-height:310px;margin:0;overflow:auto;white-space:pre-wrap;word-break:break-word;font-family:var(--vscode-editor-font-family);font-size:12px;line-height:1.55}.feedback{display:flex;align-items:center;gap:6px;margin-top:12px;padding-top:10px;border-top:1px solid var(--line);color:var(--muted);font-size:11px}.feedback span{margin-right:auto}.feedback button{width:27px;height:25px;border:1px solid transparent;border-radius:6px;background:transparent;color:var(--vscode-foreground);cursor:pointer}.feedback button:hover{border-color:var(--line);background:var(--vscode-toolbar-hoverBackground)}form{border:1px solid var(--line);border-radius:11px;background:var(--vscode-input-background);overflow:hidden}label{display:block;padding:9px 10px 0;color:var(--muted);font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase}textarea{display:block;width:100%;min-height:82px;padding:7px 10px;resize:vertical;border:0;outline:0;background:transparent;color:var(--vscode-input-foreground);font:inherit;line-height:1.45}textarea::placeholder{color:var(--vscode-input-placeholderForeground)}.composer-footer{display:flex;align-items:center;gap:8px;padding:8px 9px;border-top:1px solid var(--line);color:var(--muted);font-size:10px}.composer-footer span{line-height:1.25}.composer-footer button{margin-left:auto;flex:none;padding:6px 10px;border:0;border-radius:6px;background:var(--accent);color:white;cursor:pointer;font:600 12px var(--vscode-font-family)}.composer-footer button:hover{background:var(--accent-strong)}.composer-footer button:disabled{opacity:.6;cursor:wait}
    </style><script>
      const api=acquireVsCodeApi();const form=document.getElementById('chat-form');const prompt=document.getElementById('prompt');const answer=document.getElementById('answer');const response=document.getElementById('response');const empty=document.getElementById('empty');const send=document.getElementById('send');function ask(text){if(!text.trim())return;empty.hidden=true;response.hidden=false;document.getElementById('feedback').hidden=true;answer.textContent='Thinking...';send.disabled=true;api.postMessage({type:'chat',text})}form.onsubmit=e=>{e.preventDefault();ask(prompt.value)};document.querySelectorAll('[data-prompt]').forEach(button=>button.onclick=()=>{prompt.value=button.dataset.prompt;ask(prompt.value)});window.addEventListener('message',e=>{if(e.data.answer!==undefined){answer.textContent=e.data.answer;send.disabled=false}});
      let lastPrompt='';let lastAnswer='';for(const rating of ['up','down'])document.getElementById('thumb-'+rating).onclick=()=>{document.getElementById('feedback').hidden=true;api.postMessage({type:'feedback',rating,prompt:lastPrompt,response:lastAnswer})};window.addEventListener('message',e=>{if(e.data.prompt&&e.data.answer){lastPrompt=e.data.prompt;lastAnswer=e.data.answer;document.getElementById('feedback').hidden=false}});
    </script></body></html>`;
  }

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
    view.webview.html = this.renderHtml();
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
