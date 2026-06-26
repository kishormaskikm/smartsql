"""
db.py — Database connection and query execution.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "ecommerce.db")


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def run_query(sql: str):
    """
    Execute a read-only SQL query and return the results.
    Returns a tuple of (column_names, rows).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return columns, [dict(row) for row in rows]
    except Exception as e:
        raise e
    finally:
        conn.close()
