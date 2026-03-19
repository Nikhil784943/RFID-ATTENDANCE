import sqlite3

DB_NAME = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            name TEXT,
            time TEXT,
            date TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_record(uid, name, time, date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "INSERT INTO attendance (uid, name, time, date) VALUES (?, ?, ?, ?)",
        (uid, name, time, date)
    )

    conn.commit()
    conn.close()


def get_all_records():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT uid, name, time, date FROM attendance ORDER BY id DESC")
    rows = c.fetchall()

    conn.close()
    return rows