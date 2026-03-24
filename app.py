from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# 🔥 CONFIG
CLASS_DURATION = 60   # 60 min (change to 120 for lab)

# STUDENTS DATABASE
students = {
    91285723: "Abhishek",
    1409145362: "Animesh",
    77146475: "Nikhil"
}

# INIT DB
def init_db():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("""
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

init_db()

# 🔥 MAIN PAGE
@app.route('/')
def index():
    return render_template("index.html")

# 🔥 LOGIN PAGE
@app.route('/login')
def login():
    return render_template("login.html")

# 🔥 API: GET DATA
@app.route('/data')
def data():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT uid, name, time, date FROM attendance ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()

    return jsonify(rows)

# 🔥 API: SCAN (MAIN LOGIC)
@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    uid = data['uid']

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    current_time = datetime.now()

    # 🔍 CHECK LAST ENTRY
    cursor.execute("""
        SELECT time, date FROM attendance
        WHERE uid = ?
        ORDER BY id DESC LIMIT 1
    """, (uid,))

    result = cursor.fetchone()

    if result:
        last_time, last_date = result
        last_dt = datetime.strptime(f"{last_date} {last_time}", "%Y-%m-%d %H:%M:%S")

        diff = (current_time - last_dt).total_seconds() / 60

        if diff < CLASS_DURATION:
            conn.close()
            return jsonify({"status": "duplicate"})

    # ✅ INSERT NEW ENTRY
    name = students.get(int(uid), "Unknown")

    cursor.execute("""
        INSERT INTO attendance (uid, name, time, date)
        VALUES (?, ?, ?, ?)
    """, (
        uid,
        name,
        current_time.strftime("%H:%M:%S"),
        current_time.strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "success", "name": name})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)