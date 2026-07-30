const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { normalizeFeedbackPath, resolveSafeFeedbackPath } = require('../extension-core');

test('accepts a safe workspace-relative path', () => {
  assert.equal(normalizeFeedbackPath('lora-finetune\\data\\feedback.jsonl'), 'lora-finetune/data/feedback.jsonl');
});

for (const value of ['../outside.jsonl', '/tmp/outside.jsonl', 'C:/outside.jsonl', '']) {
  test(`rejects unsafe feedback path: ${value || 'empty'}`, () => {
    assert.throws(() => normalizeFeedbackPath(value));
  });
}

test('rejects an existing junction that escapes the workspace', async () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), 'local-ai-workspace-'));
  const outside = fs.mkdtempSync(path.join(os.tmpdir(), 'local-ai-outside-'));
  try {
    fs.symlinkSync(outside, path.join(workspace, 'linked'), 'junction');
    await assert.rejects(resolveSafeFeedbackPath(workspace, 'linked/feedback.jsonl'));
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
    fs.rmSync(outside, { recursive: true, force: true });
  }
});
