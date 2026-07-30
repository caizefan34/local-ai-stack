'use strict';

const path = require('path');
const fs = require('fs/promises');

function normalizeFeedbackPath(value) {
  const raw = String(value || '').trim().replaceAll('\\', '/');
  if (!raw || raw.includes('\0') || raw.startsWith('/') || /^[A-Za-z]:\//.test(raw)) {
    throw new Error('Feedback path must be a non-empty relative path inside the workspace.');
  }
  const normalized = path.posix.normalize(raw);
  if (normalized === '.' || normalized === '..' || normalized.startsWith('../')) {
    throw new Error('Feedback path must stay inside the workspace.');
  }
  return normalized;
}

async function resolveSafeFeedbackPath(workspacePath, value) {
  const normalized = normalizeFeedbackPath(value);
  const workspaceRealPath = await fs.realpath(workspacePath);
  const target = path.resolve(workspaceRealPath, ...normalized.split('/'));
  let ancestor = path.dirname(target);
  let ancestorRealPath;
  while (!ancestorRealPath) {
    try {
      ancestorRealPath = await fs.realpath(ancestor);
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      const parent = path.dirname(ancestor);
      if (parent === ancestor) throw error;
      ancestor = parent;
    }
  }
  const relative = path.relative(workspaceRealPath, ancestorRealPath);
  if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new Error('Feedback path resolves outside the workspace.');
  }
  return target;
}

module.exports = { normalizeFeedbackPath, resolveSafeFeedbackPath };
