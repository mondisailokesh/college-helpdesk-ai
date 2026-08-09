import sqlite3

conn = sqlite3.connect("database/users.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(

student_id TEXT PRIMARY KEY,

name TEXT,

password TEXT,

department TEXT,

year INTEGER

)
""")

cursor.execute("""
INSERT OR REPLACE INTO students VALUES(

'23PA1A4271',

'Mondi Sai Lokesh',

'123456',

'CSE-AIML',

3

)
""")

conn.commit()

conn.close()

print("Student database created successfully.")