import sqlite3
from datetime import datetime
from pathlib import Path


class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS deadlines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    notified INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS journal (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    content TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def has_seed_data(self) -> bool:
        with self._connect() as conn:
            todo_count = conn.execute("SELECT COUNT(*) FROM todos").fetchone()[0]
            dead_count = conn.execute("SELECT COUNT(*) FROM deadlines").fetchone()[0]
            return todo_count > 0 or dead_count > 0

    def add_todo(self, text: str):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO todos(text, done, created_at) VALUES (?, 0, ?)",
                (text, datetime.now().isoformat()),
            )
            conn.commit()

    def list_todos(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT id, text, done FROM todos ORDER BY id ASC").fetchall()
            return [dict(r) for r in rows]

    def update_todo_done(self, todo_id: int, done: bool):
        with self._connect() as conn:
            conn.execute("UPDATE todos SET done = ? WHERE id = ?", (1 if done else 0, todo_id))
            conn.commit()

    def delete_done_todos(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM todos WHERE done = 1")
            conn.commit()

    def add_deadline(self, title: str, due_date: str):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO deadlines(title, due_date, notified, created_at) VALUES (?, ?, 0, ?)",
                (title, due_date, datetime.now().isoformat()),
            )
            conn.commit()

    def list_deadlines(self):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, due_date, notified FROM deadlines ORDER BY due_date ASC, id ASC"
            ).fetchall()
            return [dict(r) for r in rows]

    def delete_deadline(self, deadline_id: int):
        with self._connect() as conn:
            conn.execute("DELETE FROM deadlines WHERE id = ?", (deadline_id,))
            conn.commit()

    def delete_last_deadline(self):
        with self._connect() as conn:
            row = conn.execute("SELECT id FROM deadlines ORDER BY id DESC LIMIT 1").fetchone()
            if row:
                conn.execute("DELETE FROM deadlines WHERE id = ?", (row[0],))
                conn.commit()

    def get_journal(self) -> str:
        with self._connect() as conn:
            row = conn.execute("SELECT content FROM journal WHERE id = 1").fetchone()
            return row[0] if row else ""

    def save_journal(self, content: str):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO journal(id, content, updated_at)
                VALUES (1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET content = excluded.content, updated_at = excluded.updated_at
                """,
                (content, datetime.now().isoformat()),
            )
            conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return row[0] if row else default

    def set_setting(self, key: str, value: str):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO settings(key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
            conn.commit()

    def pending_deadline_notifications(self):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, title, due_date FROM deadlines WHERE notified = 0 ORDER BY due_date ASC"
            ).fetchall()
            return [dict(r) for r in rows]

    def mark_deadline_notified(self, deadline_id: int):
        with self._connect() as conn:
            conn.execute("UPDATE deadlines SET notified = 1 WHERE id = ?", (deadline_id,))
            conn.commit()
