from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ==============================
# 🔧 CONFIG
# ==============================

CLASS_DURATION = 60   # minutes (use 120 for lab)

students = {
    91285723: "Abhishek",
    1409145362: "Animesh",
    77146475: "Nikhil"
}

DB_NAME = "attendance.db"

# ==============================
# 🗄️ DATABASE INIT
# ==============================

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
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

# ==============================
# 🌐 ROUTES
# ==============================

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

# ==============================
# 📊 GET ATTENDANCE DATA
# ==============================

@app.route('/data')
def get_data():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT uid, name, time, date
        FROM attendance
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return jsonify(rows)

# ==============================
# 📡 SCAN API (MAIN LOGIC)
# ==============================

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()

    if not data or "uid" not in data:
        return jsonify({"status": "error", "message": "Invalid data"})

    uid = data["uid"]
    current_time = datetime.now()

    conn = get_db()
    cursor = conn.cursor()

    # 🔍 CHECK LAST ENTRY
    cursor.execute("""
        SELECT time, date FROM attendance
        WHERE uid = ?
        ORDER BY id DESC LIMIT 1
    """, (uid,))

    result = cursor.fetchone()

    if result:
        last_time, last_date = result

        last_dt = datetime.strptime(
            f"{last_date} {last_time}",
            "%Y-%m-%d %H:%M:%S"
        )

        diff_minutes = (current_time - last_dt).total_seconds() / 60

        if diff_minutes < CLASS_DURATION:
            conn.close()
            return jsonify({
                "status": "duplicate",
                "message": "Already marked"
            })

    # ✅ INSERT NEW RECORD
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

    return jsonify({
        "status": "success",
        "name": name
    })

# ==============================
# 📥 EXPORT CSV
# ==============================

@app.route('/export')
def export():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT uid, name, time, date FROM attendance")
    rows = cursor.fetchall()
    conn.close()

    def generate():
        yield "UID,Name,Time,Date\n"
        for row in rows:
            yield f"{row[0]},{row[1]},{row[2]},{row[3]}\n"

    return Response(
        generate(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=attendance.csv"}
    )

# ==============================
# ▶️ RUN SERVER
# ==============================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)