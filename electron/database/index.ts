import initSqlJs, { Database } from 'sql.js';
import * as fs from 'fs-extra';
import * as path from 'path';
import { app } from 'electron';

let chemicalsDB: Database | null = null;
let userDB: Database | null = null;
let SQL: any = null;

export async function initDatabases(): Promise<void> {
  SQL = await initSqlJs({
    locateFile: (file) => {
      const wasmPath = path.join(process.resourcesPath, 'resources', file);
      if (fs.existsSync(wasmPath)) return wasmPath;
      return path.join(__dirname, '..', '..', 'node_modules', 'sql.js', 'dist', file);
    }
  });

  // Load read-only chemicals.db
  const chemicalsPath = path.join(process.resourcesPath, 'resources', 'chemicals.db');
  const chemicalsBuffer = fs.readFileSync(chemicalsPath);
  chemicalsDB = new SQL.Database(chemicalsBuffer);

  // Load or create user.db
  const userDataPath = app.getPath('userData');
  const userDBPath = path.join(userDataPath, 'user.db');
  
  if (fs.existsSync(userDBPath)) {
    const userBuffer = fs.readFileSync(userDBPath);
    userDB = new SQL.Database(userBuffer);
  } else {
    userDB = new SQL.Database();
    userDB!.run(`
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

export function saveUserDB(): void {
  if (!userDB) return;
  const userDataPath = app.getPath('userData');
  const userDBPath = path.join(userDataPath, 'user.db');
  const data = userDB!.export();
  fs.writeFileSync(userDBPath, Buffer.from(data));
}

export function getChemicalsDB(): Database {
  if (!chemicalsDB) throw new Error('Database not initialized');
  return chemicalsDB;
}

export function getUserDB(): Database {
  if (!userDB) throw new Error('User database not initialized');
  return userDB;
}

export function closeDatabases(): void {
  if (chemicalsDB) chemicalsDB.close();
  if (userDB) {
    saveUserDB();
    userDB.close();
  }
}
