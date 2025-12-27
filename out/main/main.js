import { app, ipcMain, BrowserWindow } from "electron";
import * as path from "path";
import initSqlJs from "sql.js";
import * as fs from "fs-extra";
import __cjs_mod__ from "node:module";
const __filename = import.meta.filename;
const __dirname = import.meta.dirname;
const require2 = __cjs_mod__.createRequire(import.meta.url);
let chemicalsDB = null;
let userDB = null;
let SQL = null;
async function initDatabases() {
  SQL = await initSqlJs({
    locateFile: (file) => {
      const wasmPath = path.join(process.resourcesPath, "resources", file);
      if (fs.existsSync(wasmPath)) return wasmPath;
      return path.join(__dirname, "..", "..", "node_modules", "sql.js", "dist", file);
    }
  });
  const chemicalsPath = path.join(process.resourcesPath, "resources", "chemicals.db");
  const chemicalsBuffer = fs.readFileSync(chemicalsPath);
  chemicalsDB = new SQL.Database(chemicalsBuffer);
  const userDataPath = app.getPath("userData");
  const userDBPath = path.join(userDataPath, "user.db");
  if (fs.existsSync(userDBPath)) {
    const userBuffer = fs.readFileSync(userDBPath);
    userDB = new SQL.Database(userBuffer);
  } else {
    userDB = new SQL.Database();
    userDB.run(`
      CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chemical_id INTEGER NOT NULL,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        note TEXT
      );
    `);
    saveUserDB();
  }
}
function saveUserDB() {
  if (!userDB) return;
  const userDataPath = app.getPath("userData");
  const userDBPath = path.join(userDataPath, "user.db");
  const data = userDB.export();
  fs.writeFileSync(userDBPath, Buffer.from(data));
}
function getChemicalsDB() {
  if (!chemicalsDB) throw new Error("Database not initialized");
  return chemicalsDB;
}
function getUserDB() {
  if (!userDB) throw new Error("User database not initialized");
  return userDB;
}
function closeDatabases() {
  if (chemicalsDB) chemicalsDB.close();
  if (userDB) {
    saveUserDB();
    userDB.close();
  }
}
let mainWindow = null;
async function createWindow() {
  await initDatabases();
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  if (process.env.NODE_ENV === "development") {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, "../renderer/index.html"));
  }
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}
app.whenReady().then(createWindow);
app.on("window-all-closed", () => {
  closeDatabases();
  if (process.platform !== "darwin") {
    app.quit();
  }
});
app.on("activate", () => {
  if (mainWindow === null) {
    createWindow();
  }
});
ipcMain.handle("db:search", async (_event, query) => {
  try {
    const db = getChemicalsDB();
    const sql = `
      SELECT id, name, synonyms 
      FROM chemicals 
      WHERE name LIKE ? OR synonyms LIKE ?
      LIMIT 50
    `;
    const results = db.exec(sql, [`%${query}%`, `%${query}%`]);
    if (results.length === 0) {
      return { items: [], total: 0 };
    }
    const items = results[0].values.map((row) => ({
      id: row[0],
      name: row[1],
      synonyms: row[2]
    }));
    return { items, total: items.length };
  } catch (error) {
    console.error("Search error:", error);
    return { items: [], total: 0 };
  }
});
ipcMain.handle("db:get-chemical", async (_event, id) => {
  try {
    const db = getChemicalsDB();
    const sql = `SELECT * FROM chemicals WHERE id = ?`;
    const results = db.exec(sql, [id]);
    if (results.length === 0 || results[0].values.length === 0) {
      return null;
    }
    const row = results[0].values[0];
    const columns = results[0].columns;
    const chemical = {};
    columns.forEach((col, idx) => {
      chemical[col] = row[idx];
    });
    return chemical;
  } catch (error) {
    console.error("Get chemical error:", error);
    return null;
  }
});
ipcMain.handle("db:get-favorites", async () => {
  try {
    const db = getUserDB();
    const results = db.exec("SELECT * FROM favorites ORDER BY added_at DESC");
    if (results.length === 0) return [];
    return results[0].values.map((row) => ({
      id: row[0],
      chemical_id: row[1],
      added_at: row[2],
      note: row[3]
    }));
  } catch (error) {
    console.error("Get favorites error:", error);
    return [];
  }
});
ipcMain.handle("db:add-favorite", async (_event, chemicalId, note) => {
  try {
    const db = getUserDB();
    db.run("INSERT INTO favorites (chemical_id, note) VALUES (?, ?)", [chemicalId, note || null]);
    saveUserDB();
    return { success: true };
  } catch (error) {
    console.error("Add favorite error:", error);
    return { success: false, error: String(error) };
  }
});
ipcMain.handle("db:remove-favorite", async (_event, chemicalId) => {
  try {
    const db = getUserDB();
    db.run("DELETE FROM favorites WHERE chemical_id = ?", [chemicalId]);
    saveUserDB();
    return { success: true };
  } catch (error) {
    console.error("Remove favorite error:", error);
    return { success: false, error: String(error) };
  }
});
