"use strict";

const { app, BrowserWindow, WebContentsView, Menu, ipcMain, shell } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "..", "..");
const CONTROL_URL = "http://127.0.0.1:18080";
const FASTGPT_URL = "http://127.0.0.1:3000";
const STATUS_URL = `${CONTROL_URL}/api/setup/status`;
const ICON = path.join(REPO_ROOT, "desktop-app", "assets", "nailong-mascot.ico");
const TOP_BAR_HEIGHT = 46;

const PAGES = {
  control: { url: `${CONTROL_URL}/`, label: "控制台" },
  fastgpt: { url: `${FASTGPT_URL}/`, label: "FastGPT" },
};
const ALLOWED_PORTS = new Set(["18080", "3000"]);

let splashWindow = null;
let mainWindow = null;
let contentView = null;
let controlProcess = null;
let currentPage = "control";

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

function isAllowedUrl(url) {
  try {
    const u = new URL(url);
    return (
      (u.protocol === "http:" || u.protocol === "https:") &&
      (u.hostname === "127.0.0.1" || u.hostname === "localhost") &&
      ALLOWED_PORTS.has(u.port)
    );
  } catch (_) {
    return false;
  }
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

function layoutContent() {
  if (!mainWindow || !contentView) return;
  const [w, h] = mainWindow.getContentSize();
  contentView.setBounds({ x: 0, y: TOP_BAR_HEIGHT, width: w, height: Math.max(0, h - TOP_BAR_HEIGHT) });
}

function syncNavState() {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  const url = contentView && contentView.webContents ? contentView.webContents.getURL() : "";
  let page = currentPage;
  if (url.startsWith(FASTGPT_URL)) page = "fastgpt";
  else if (url.startsWith(CONTROL_URL)) page = "control";
  mainWindow.webContents.send("nav:state", { page, url });
}

function loadPage(page) {
  if (!PAGES[page]) page = "control";
  currentPage = page;
  contentView.webContents.loadURL(PAGES[page].url);
  syncNavState();
}

function sendMaximizeState(max) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send("window:maximized", !!max);
  }
}

function createMainWindow(initialPage = "control") {
  currentPage = PAGES[initialPage] ? initialPage : "control";

  mainWindow = new BrowserWindow({
    width: 1360,
    height: 860,
    minWidth: 1000,
    minHeight: 660,
    show: false,
    frame: false,
    icon: ICON,
    title: "Local AI Stack",
    backgroundColor: "#0b1020",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  Menu.setApplicationMenu(null);
  mainWindow.loadFile(path.join(__dirname, "shell.html"));

  contentView = new WebContentsView({
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  mainWindow.contentView.addChildView(contentView);
  layoutContent();
  mainWindow.on("resize", layoutContent);

  // Local pages stay in-app; anything else opens in the default browser.
  contentView.webContents.setWindowOpenHandler(({ url }) => {
    if (isAllowedUrl(url)) return { action: "allow" };
    shell.openExternal(url);
    return { action: "deny" };
  });
  contentView.webContents.on("will-navigate", (event, url) => {
    if (!isAllowedUrl(url)) {
      event.preventDefault();
      shell.openExternal(url);
    }
  });

  // Keep the tab highlight in sync with actual navigation.
  contentView.webContents.on("did-navigate", () => syncNavState());
  contentView.webContents.on("did-navigate-in-page", () => syncNavState());

  loadPage(currentPage);

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    if (splashWindow && !splashWindow.isDestroyed()) splashWindow.close();
  });
  mainWindow.on("maximize", () => sendMaximizeState(true));
  mainWindow.on("unmaximize", () => sendMaximizeState(false));
  mainWindow.on("closed", () => {
    mainWindow = null;
    contentView = null;
  });
}

// ---- IPC (used by splash + shell) -------------------------------------------

ipcMain.on("nav:select", (_e, page) => {
  if (PAGES[page]) loadPage(page);
});
ipcMain.on("nav:reload", () => {
  if (contentView && contentView.webContents) contentView.webContents.reload();
});
ipcMain.on("nav:back", () => {
  if (contentView && contentView.webContents.navigationHistory.canGoBack()) {
    contentView.webContents.navigationHistory.goBack();
  }
});
ipcMain.on("nav:forward", () => {
  if (contentView && contentView.webContents.navigationHistory.canGoForward()) {
    contentView.webContents.navigationHistory.goForward();
  }
});

ipcMain.on("window:close", (e) => {
  const win = BrowserWindow.fromWebContents(e.sender);
  if (win) win.close();
});
ipcMain.on("window:minimize", (e) => {
  const win = BrowserWindow.fromWebContents(e.sender);
  if (win) win.minimize();
});
ipcMain.on("window:toggle-maximize", (e) => {
  const win = BrowserWindow.fromWebContents(e.sender);
  if (!win) return;
  if (win.isMaximized()) win.unmaximize();
  else win.maximize();
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

    const initialPage = process.argv.includes("--fastgpt") ? "fastgpt" : "control";
    createMainWindow(initialPage);
  });

  app.on("window-all-closed", () => {
    // The control plane keeps running so services stay available.
    app.quit();
  });
}