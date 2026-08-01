"use strict";

const { app, BrowserWindow, Menu, ipcMain, shell } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "..", "..");
const CONTROL_URL = "http://127.0.0.1:18080";
const STATUS_URL = `${CONTROL_URL}/api/setup/status`;
const ICON = path.join(REPO_ROOT, "desktop-app", "assets", "nailong-mascot.ico");

let splashWindow = null;
let mainWindow = null;
let controlProcess = null;
let userClosed = false;

// ---- helpers ---------------------------------------------------------------

function loadEnv() {
  const env = { ...process.env };
  const envFile = path.join(REPO_ROOT, ".env");
  try {
    const text = fs.readFileSync(envFile, "utf8");
    for (const line of text.split(/\r?\n/)) {
      const m = line.match(/^\s*(CONTROL_PLANE_AGENT_(?:WORKSPACE|MODELS))\s*=\s*(.*?)\s*$/);
      if (m) env[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
  } catch (_) {
    /* .env is optional; defaults apply */
  }
  return env;
}

function setStatus(msg) {
  if (splashWindow && !splashWindow.isDestroyed()) {
    splashWindow.webContents.send("status", msg);
  }
}

async function isControlPlaneReady() {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 2500);
    const res = await fetch(STATUS_URL, { signal: controller.signal });
    clearTimeout(timer);
    return res.status < 500;
  } catch (_) {
    return false;
  }
}

function startControlPlane() {
  const venvPython = path.join(REPO_ROOT, ".venv", "Scripts", "python.exe");
  const python = fs.existsSync(venvPython) ? venvPython : "python";
  setStatus("正在启动本地 AI 服务…");
  controlProcess = spawn(
    python,
    ["-m", "control_plane", "serve", "--host", "127.0.0.1", "--port", "18080"],
    {
      cwd: REPO_ROOT,
      env: loadEnv(),
      windowsHide: true,
      detached: true,
      stdio: "ignore",
    }
  );
  controlProcess.unref();
}

async function waitForControlPlane(timeoutMs = 120000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (await isControlPlaneReady()) return true;
    await new Promise((r) => setTimeout(r, 800));
  }
  return false;
}

// ---- windows ----------------------------------------------------------------

function createSplash() {
  splashWindow = new BrowserWindow({
    width: 460,
    height: 340,
    frame: false,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    show: false,
    icon: ICON,
    backgroundColor: "#0b1020",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  splashWindow.loadFile(path.join(__dirname, "splash.html"));
  splashWindow.once("ready-to-show", () => splashWindow.show());
  splashWindow.on("closed", () => (splashWindow = null));
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 960,
    minHeight: 640,
    show: false,
    icon: ICON,
    title: "Local AI Stack",
    backgroundColor: "#0b1020",
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  Menu.setApplicationMenu(null);
  mainWindow.setMenuBarVisibility(false);

  mainWindow.loadURL(`${CONTROL_URL}/`);
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    if (splashWindow && !splashWindow.isDestroyed()) splashWindow.close();
  });

  // Open external links in the default browser, keep dashboard links in-app.
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith(CONTROL_URL)) return { action: "allow" };
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.webContents.on("did-fail-load", (_e, code, desc, url) => {
    if (url === `${CONTROL_URL}/` && code !== -3) {
      setStatus(`加载失败(${code} ${desc})，正在重试…`);
      setTimeout(() => mainWindow && mainWindow.loadURL(`${CONTROL_URL}/`), 1500);
    }
  });

  mainWindow.on("closed", () => (mainWindow = null));
}

// ---- IPC (used by the frameless splash) --------------------------------------

ipcMain.on("window:close", (e) => {
  const win = BrowserWindow.fromWebContents(e.sender);
  if (win) win.close();
});
ipcMain.on("window:minimize", (e) => {
  const win = BrowserWindow.fromWebContents(e.sender);
  if (win) win.minimize();
});

// ---- lifecycle ---------------------------------------------------------------

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  app.whenReady().then(async () => {
    app.setAppUserModelId("com.localaistack.desktop");
    createSplash();

    let ready = await isControlPlaneReady();
    if (!ready) {
      startControlPlane();
      ready = await waitForControlPlane();
    }

    if (!ready) {
      setStatus("本地 AI 服务启动失败，请检查 Python/Docker 后重试");
      return;
    }
    createMainWindow();
  });

  app.on("window-all-closed", () => {
    // The control plane keeps running so services stay available.
    app.quit();
  });
}
