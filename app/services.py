import json
import threading
import time
from datetime import datetime
from pathlib import Path

import schedule

try:
    from plyer import notification
except Exception:  # pragma: no cover
    notification = None


class JsonSnapshotService:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, payload: dict):
        with self.output_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)


class ReminderScheduler:
    def __init__(self, db, interval_seconds: int = 30):
        self.db = db
        self.interval_seconds = interval_seconds
        self._thread = None
        self._stop = threading.Event()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        schedule.every(1).minutes.do(self._check_deadlines)
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        schedule.clear()

    def _run_loop(self):
        self._check_deadlines()
        while not self._stop.is_set():
            schedule.run_pending()
            time.sleep(self.interval_seconds)

    def _check_deadlines(self):
        now = datetime.now()
        rows = self.db.pending_deadline_notifications()
        for row in rows:
            due = self._parse_date(row["due_date"])
            if not due:
                continue
            delta = due - now
            if delta.total_seconds() <= 24 * 3600:
                self._notify(row["title"], row["due_date"])
                self.db.mark_deadline_notified(row["id"])

    def _parse_date(self, date_str: str):
        # Accept YYYY-MM-DD as canonical format.
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d")
        except ValueError:
            return None

    def _notify(self, title: str, due_date: str):
        msg = f"Deadline approaching: {title} (due {due_date})"
        if notification:
            try:
                notification.notify(
                    title="Dashboard Reminder",
                    message=msg,
                    timeout=8,
                )
                return
            except Exception:
                pass
        print(msg)
