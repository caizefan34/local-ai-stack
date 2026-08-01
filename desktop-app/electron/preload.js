"use strict";

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("desktop", {
  versions: {
    electron: process.versions.electron,
    chrome: process.versions.chrome,
    node: process.versions.node,
  },
  window: {
    close: () => ipcRenderer.send("window:close"),
    minimize: () => ipcRenderer.send("window:minimize"),
    toggleMaximize: () => ipcRenderer.send("window:toggle-maximize"),
    onMaximized: (cb) => ipcRenderer.on("window:maximized", (_e, max) => cb(max)),
  },
  nav: {
    select: (page) => ipcRenderer.send("nav:select", page),
    reload: () => ipcRenderer.send("nav:reload"),
    back: () => ipcRenderer.send("nav:back"),
    forward: () => ipcRenderer.send("nav:forward"),
    onState: (cb) => ipcRenderer.on("nav:state", (_e, state) => cb(state)),
  },
  onStatus: (cb) => {
    ipcRenderer.on("status", (_event, msg) => cb(msg));
  },
});