import sqlite3
from pathlib import Path
from typing import Optional

_SCHEMA = '''
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS cards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nickname TEXT NOT NULL,
  issuer TEXT,
  last4 TEXT,
  reward_currency TEXT NOT NULL DEFAULT 'points',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reward_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  card_id INTEGER NOT NULL,
  category TEXT NOT NULL,
  multiplier REAL NOT NULL,
  unit TEXT NOT NULL,   -- 'x' or 'percent'
  notes TEXT,
  FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_rules_card_cat ON reward_rules(card_id, category);
'''

class Database:
    def __init__(self, db_path: Optional[str] = None):
        # On iOS this resolves inside the app sandbox.
        base = Path.home()
        self.path = str(Path(db_path) if db_path else (base / "wallet.db"))

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(_SCHEMA)
            conn.commit()
