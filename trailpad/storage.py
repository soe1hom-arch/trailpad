from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import tempfile
from typing import Any


APP_DIR = Path.home() / ".trailpad"
STORE_FILE = APP_DIR / "vault.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(slots=True)
class Note:
    id: int
    created_at: str
    text: str
    tags: list[str]
    pinned: bool = False


def init_store() -> dict[str, Any]:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not STORE_FILE.exists():
        data = {"version": 1, "created_at": now_iso(), "notes": []}
        write_store(data)
        return data
    return read_store()


def read_store() -> dict[str, Any]:
    if not STORE_FILE.exists():
        return {"version": 1, "created_at": now_iso(), "notes": []}
    with STORE_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_store(data: dict[str, Any]) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix="trailpad-", suffix=".tmp", dir=str(APP_DIR))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp_name, STORE_FILE)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _notes(data: dict[str, Any]) -> list[dict[str, Any]]:
    return data.setdefault("notes", [])


def next_id(data: dict[str, Any]) -> int:
    notes = _notes(data)
    return max((int(n["id"]) for n in notes), default=0) + 1


def add_note(text: str, tags: list[str]) -> Note:
    data = read_store()
    note = Note(
        id=next_id(data),
        created_at=now_iso(),
        text=text.strip(),
        tags=sorted({t.strip() for t in tags if t.strip()}),
    )
    _notes(data).append(asdict(note))
    write_store(data)
    return note


def get_note(note_id: int) -> dict[str, Any] | None:
    data = read_store()
    for note in _notes(data):
        if int(note["id"]) == note_id:
            return note
    return None


def update_note(note_id: int, updater) -> dict[str, Any] | None:
    data = read_store()
    notes = _notes(data)
    for idx, note in enumerate(notes):
        if int(note["id"]) == note_id:
            new_note = updater(dict(note))
            notes[idx] = new_note
            write_store(data)
            return new_note
    return None


def delete_note(note_id: int) -> bool:
    data = read_store()
    notes = _notes(data)
    before = len(notes)
    notes[:] = [n for n in notes if int(n["id"]) != note_id]
    if len(notes) == before:
        return False
    write_store(data)
    return True


def iter_notes() -> list[dict[str, Any]]:
    data = read_store()
    notes = list(_notes(data))
    notes.sort(key=lambda n: (not bool(n.get("pinned")), int(n["id"])))
    return notes

