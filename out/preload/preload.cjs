"use strict";
const electron = require("electron");
electron.contextBridge.exposeInMainWorld("ipcRenderer", {
  invoke: (channel, ...args) => {
    const validChannels = [
      "db:search",
      "db:get-chemical",
      "db:get-favorites",
      "db:add-favorite",
      "db:remove-favorite"
    ];
    if (validChannels.includes(channel)) {
      return electron.ipcRenderer.invoke(channel, ...args);
    }
    throw new Error(`Invalid IPC channel: ${channel}`);
  }
});
