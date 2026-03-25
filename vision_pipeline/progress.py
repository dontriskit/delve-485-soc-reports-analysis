"""Progress tracking with resume capability."""
import json
from .config import PROGRESS_FILE


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed": {}, "failed": {}, "in_progress": {}}


def save_progress(progress: dict):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def mark_completed(doc_id: str, pages: int):
    p = load_progress()
    p["completed"][doc_id] = {"pages": pages}
    p.pop("in_progress", {}).pop(doc_id, None)
    save_progress(p)


def mark_failed(doc_id: str, error: str):
    p = load_progress()
    p["failed"][doc_id] = {"error": error}
    p.pop("in_progress", {}).pop(doc_id, None)
    save_progress(p)


def mark_in_progress(doc_id: str):
    p = load_progress()
    p.setdefault("in_progress", {})[doc_id] = True
    save_progress(p)


def is_done(doc_id: str) -> bool:
    p = load_progress()
    return doc_id in p.get("completed", {})
