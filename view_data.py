"""Quick script to view all data in the ecommerce database."""
import sqlite3

conn = sqlite3.connect("data/ecommerce.db")
cur = conn.cursor()

# Get all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
tables = [r[0] for r in cur.fetchall()]
print(f"Tables: {tables}\n")

for table in tables:
    print(f"{'='*50}")
    print(f"  {table.upper()}")
    print(f"{'='*50}")
    cur.execute(f"SELECT * FROM {table}")
    columns = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print(f"Columns: {columns}")
    for row in rows:
        print(row)
    print(f"({len(rows)} rows)\n")

conn.close()
