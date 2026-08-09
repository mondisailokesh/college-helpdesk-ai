import sqlite3

conn = sqlite3.connect("database/helpdesk.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT,

    issue TEXT,

    status TEXT
)
""")

conn.commit()

conn.close()

print("Database Created Successfully!")