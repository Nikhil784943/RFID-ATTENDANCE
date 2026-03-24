from flask import Flask, render_template, request, jsonify, redirect, Response
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ==============================
# 🔧 CONFIG
# ==============================

CLASS_DURATION = 60  # minutes

students = {
    91285723: "Abhishek",
    1409145362: "Animesh",
    77146475: "Nikhil"
}

DB_NAME = "attendance.db"

# ==============================
# 🗄️ DB FUNCTIONS
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
# 📊 GET TODAY DATA
# ==============================

@app.route('/data')
def get_data():
    today = datetime.now().strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT uid, name, time, date
        FROM attendance
        WHERE date = ?
        ORDER BY id DESC
    """, (today,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify(rows)

# ==============================
# 📡 SCAN API
# ==============================

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()

    if not data or "uid" not in data:
        return jsonify({"status": "error"})

    uid = data["uid"]
    now = datetime.now()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT time, date FROM attendance
        WHERE uid = ?
        ORDER BY id DESC LIMIT 1
    """, (uid,))

    result = cursor.fetchone()

    if result:
        last_time, last_date = result
        last_dt = datetime.strptime(f"{last_date} {last_time}", "%Y-%m-%d %H:%M:%S")

        diff = (now - last_dt).total_seconds() / 60

        if diff < CLASS_DURATION:
            conn.close()
            return jsonify({"status": "duplicate"})

    name = students.get(int(uid), "Unknown")

    cursor.execute("""
        INSERT INTO attendance (uid, name, time, date)
        VALUES (?, ?, ?, ?)
    """, (
        uid,
        name,
        now.strftime("%H:%M:%S"),
        now.strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "success", "name": name})

# ==============================
# 🧹 CLEAR DATA
# ==============================

@app.route('/clear')
def clear():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM attendance")

    conn.commit()
    conn.close()

    return redirect('/')

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
        for r in rows:
            yield f"{r[0]},{r[1]},{r[2]},{r[3]}\n"

    return Response(generate(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=attendance.csv"}
    )

# ==============================
# ▶️ RUN
# ==============================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)