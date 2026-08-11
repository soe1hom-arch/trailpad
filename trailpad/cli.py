from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .storage import (
    APP_DIR,
    STORE_FILE,
    add_note,
    delete_note,
    get_note,
    init_store,
    iter_notes,
    read_store,
    update_note,
)


def _c(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def fmt_note(note: dict) -> str:
    tags = f" [{', '.join(note.get('tags', []))}]" if note.get("tags") else ""
    pin = "📌 " if note.get("pinned") else ""
    return f"{pin}{note['id']:>3} {note['created_at']} {note['text']}{tags}"


def cmd_init(_: argparse.Namespace) -> int:
    data = init_store()
    print(f"Initialized trailpad vault at {STORE_FILE}")
    print(f"Vault version: {data['version']}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    text = " ".join(args.text).strip()
    if not text:
        print("Error: note text required", file=sys.stderr)
        return 1
    note = add_note(text, args.tag or [])
    print(f"Added note {note.id}")
    return 0


def _filter_notes(args: argparse.Namespace) -> list[dict]:
    notes = iter_notes()
    if getattr(args, "tag", None):
        wanted = {t.lower() for t in args.tag}
        notes = [n for n in notes if wanted.intersection({t.lower() for t in n.get("tags", [])})]
    if getattr(args, "query", None):
        q = args.query.lower()
        notes = [
            n for n in notes
            if q in n["text"].lower() or any(q in t.lower() for t in n.get("tags", []))
        ]
    return notes


def cmd_list(args: argparse.Namespace) -> int:
    notes = _filter_notes(args)
    if not notes:
        print(_c("No notes found.", "33"))
        return 0
    for note in notes:
        print(fmt_note(note))
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    notes = _filter_notes(args)
    if not notes:
        print(_c("No matches found.", "33"))
        return 0
    for note in notes:
        print(fmt_note(note))
    return 0


def cmd_pin(args: argparse.Namespace, pinned: bool) -> int:
    note = get_note(args.note_id)
    if not note:
        print(f"Error: note {args.note_id} not found", file=sys.stderr)
        return 1
    updated = update_note(args.note_id, lambda n: {**n, "pinned": pinned})
    print(f"{'Pinned' if pinned else 'Unpinned'} note {updated['id']}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    if not delete_note(args.note_id):
        print(f"Error: note {args.note_id} not found", file=sys.stderr)
        return 1
    print(f"Removed note {args.note_id}")
    return 0


def cmd_stats(_: argparse.Namespace) -> int:
    data = read_store()
    notes = data.get("notes", [])
    total = len(notes)
    pinned = sum(1 for n in notes if n.get("pinned"))
    tagged = sum(1 for n in notes if n.get("tags"))
    print(f"Vault: {STORE_FILE}")
    print(f"Total:  {total}")
    print(f"Pinned: {pinned}")
    print(f"Tagged: {tagged}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    notes = iter_notes()
    dest = Path(args.path)
    if args.format == "json":
        import json
        dest.write_text(json.dumps(notes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        lines = ["# Trailpad Export", ""]
        for note in notes:
            lines.append(f"- {fmt_note(note)}")
        dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Exported {len(notes)} note(s) to {dest}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trailpad", description="Offline note trail manager")
    parser.add_argument("--version", action="version", version=f"trailpad {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="Initialize the vault")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("add", help="Add a note")
    p.add_argument("text", nargs="+", help="Note text")
    p.add_argument("-t", "--tag", action="append", help="Attach a tag", default=[])
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("list", help="List notes")
    p.add_argument("--tag", action="append", help="Filter by tag")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("find", help="Search notes")
    p.add_argument("query", help="Search text")
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("pin", help="Pin a note")
    p.add_argument("note_id", type=int)
    p.set_defaults(func=lambda args: cmd_pin(args, True))

    p = sub.add_parser("unpin", help="Unpin a note")
    p.add_argument("note_id", type=int)
    p.set_defaults(func=lambda args: cmd_pin(args, False))

    p = sub.add_parser("rm", help="Remove a note")
    p.add_argument("note_id", type=int)
    p.set_defaults(func=cmd_remove)

    p = sub.add_parser("stats", help="Show vault stats")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("export", help="Export notes")
    p.add_argument("path", help="Output file path")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.set_defaults(func=cmd_export)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
