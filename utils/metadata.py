"""
metadata.py — Fetches table and column info from the SQLite database.
"""

from db import get_connection


def get_table_names():
    """Return a list of all table names in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def get_columns(table_name: str):
    """Return column info for a given table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info('{table_name}');")
    columns = cursor.fetchall()
    conn.close()
    return [
        {"name": col[1], "type": col[2], "notnull": bool(col[3]), "pk": bool(col[5])}
        for col in columns
    ]


def get_schema_summary():
    """
    Build a human-readable schema summary string for use in prompts.
    Example output:
        Table: customers
          - id (INTEGER, PK)
          - name (TEXT, NOT NULL)
          ...
    """
    tables = get_table_names()
    lines = []
    for table in tables:
        lines.append(f"Table: {table}")
        for col in get_columns(table):
            flags = []
            if col["pk"]:
                flags.append("PK")
            if col["notnull"]:
                flags.append("NOT NULL")
            flag_str = f", {', '.join(flags)}" if flags else ""
            lines.append(f"  - {col['name']} ({col['type']}{flag_str})")
        lines.append("")
    return "\n".join(lines)
