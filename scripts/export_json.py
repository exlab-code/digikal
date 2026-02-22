#!/usr/bin/env python3
"""Export foerdermittel.db to a static JSON file for the DigiKal website.

Usage:
    python export_json.py                          # reads foerdermittel.db, writes foerdermittel.json
    python export_json.py -o /path/to/output.json  # custom output path
    python export_json.py --db /path/to/db          # custom DB path
"""

import argparse
import json
import os
import sqlite3
import sys


def _parse_json_field(val):
    """Parse a JSON string field, returning the parsed value or empty list."""
    if not val:
        return []
    if isinstance(val, list):
        return val
    try:
        parsed = json.loads(val)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def export_json(db_path: str, output_path: str) -> int:
    """Export the SQLite database to a frontend-compatible JSON file.

    Returns the number of programs exported.
    """
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("SELECT * FROM foerdermittel").fetchall()

    programs = []
    for row in rows:
        r = dict(row)

        # Fix deadline_type for frontend compatibility
        deadline_type = r.get("deadline_type") or ""
        if deadline_type == "jährlich":
            deadline_type = "jaehrlich"

        program = {
            "id": r["id"],
            "title": r.get("clean_title") or r["title"],
            "original_title": r["title"],
            "description": r.get("short_summary") or "",
            "eligibility_summary": r.get("eligibility_summary") or "",
            "funding_amount_text": r.get("funding_summary") or "",
            "funding_organization": r.get("institution_name") or "",
            "bundesland": r.get("bundesland") or "",
            "funding_type": r.get("funding_type_normalized") or "",
            "application_deadline": r.get("application_deadline"),
            "deadline_type": deadline_type,
            "source_url": r.get("source_url") or "",
            "tag_groups": {
                "super_kategorie": _parse_json_field(r.get("super_kategorien")),
                "thema": _parse_json_field(r.get("themen")),
                "zielgruppe": _parse_json_field(r.get("zielgruppen")),
                "foerderart": _parse_json_field(r.get("foerderart")),
            },
        }

        programs.append(program)

    conn.close()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(programs, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(programs)} programs to {output_path}")
    return len(programs)


def main():
    parser = argparse.ArgumentParser(
        description="Export foerdermittel.db to static JSON for the website",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="website/public/foerdermittel.json",
        help="Output JSON file path (default: website/public/foerdermittel.json)",
    )
    parser.add_argument(
        "--db",
        type=str,
        default="foerdermittel.db",
        help="Path to SQLite database",
    )
    args = parser.parse_args()

    export_json(args.db, args.output)


if __name__ == "__main__":
    main()
