import json
from pathlib import Path


def seed_if_empty(db, seed_file: Path):
    if db.has_seed_data():
        return
    if not seed_file.exists():
        return

    data = json.loads(seed_file.read_text(encoding="utf-8"))

    for text in data.get("todos", []):
        db.add_todo(text)

    for row in data.get("deadlines", []):
        title = row.get("title", "")
        due = row.get("due_date", "")
        if title and due:
            db.add_deadline(title, due)

    db.save_journal(data.get("journal", ""))
    if data.get("chart_mode"):
        db.set_setting("chart_mode", data["chart_mode"])
