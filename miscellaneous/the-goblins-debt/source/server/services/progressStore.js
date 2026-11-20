import { DatabaseSync } from "node:sqlite";
import { mkdirSync } from "node:fs";
import { dirname } from "node:path";
export class ProgressStore {
  constructor(path) {
    if (path !== ":memory:") mkdirSync(dirname(path), { recursive: true });
    this.db = new DatabaseSync(path);
    this.db.exec(`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;
      CREATE TABLE IF NOT EXISTS progress(team_id TEXT PRIMARY KEY, balance INTEGER NOT NULL DEFAULT 0 CHECK(balance BETWEEN 0 AND 120), updated_at TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS launches(nonce TEXT PRIMARY KEY, expires INTEGER NOT NULL);`);
    this.read = this.db.prepare(
      "SELECT balance, updated_at AS updatedAt FROM progress WHERE team_id=?",
    );
    // A single UPSERT performs the increment atomically, including across connections.
    this.increment = this.db.prepare(
      `INSERT INTO progress(team_id,balance,updated_at) VALUES(?,?,?) ON CONFLICT(team_id) DO UPDATE SET balance=MIN(120,progress.balance+excluded.balance),updated_at=excluded.updated_at RETURNING balance,updated_at AS updatedAt`,
    );
  }
  progress(id) {
    return this.present(this.read.get(id) || { balance: 0, updatedAt: null });
  }
  deposit(id, coins) {
    return this.present(
      this.increment.get(id, coins, new Date().toISOString()),
    );
  }
  present(row) {
    return { ...row, unlocked: row.balance >= 120, goal: 120 };
  }
  consumeNonce(nonce, expires) {
    this.db
      .prepare("DELETE FROM launches WHERE expires < ?")
      .run(Math.floor(Date.now() / 1000));
    try {
      this.db
        .prepare("INSERT INTO launches(nonce,expires) VALUES(?,?)")
        .run(nonce, expires);
      return true;
    } catch (e) {
      if (e.code === "ERR_SQLITE_ERROR" && String(e.message).includes("UNIQUE"))
        return false;
      throw e;
    }
  }
  close() {
    this.db.close();
  }
}
