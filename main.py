from pathlib import Path

from app.bootstrap import seed_if_empty
from app.db import Database
from app.services import JsonSnapshotService, ReminderScheduler
from app.ui import DashboardApp


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "dashboard.sqlite3"
SEED_PATH = DATA_DIR / "seed.json"
SNAPSHOT_PATH = DATA_DIR / "snapshot.json"


def main():
    db = Database(DB_PATH)
    seed_if_empty(db, SEED_PATH)

    snapshot = JsonSnapshotService(SNAPSHOT_PATH)
    reminders = ReminderScheduler(db)
    reminders.start()

    app = DashboardApp(db, snapshot)

    def on_close():
        reminders.stop()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
