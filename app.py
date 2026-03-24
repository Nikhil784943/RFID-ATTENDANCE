from flask import Flask, render_template, request, jsonify, redirect, session, Response
import sqlite3
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = "rfid_secret_key"

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
IST = pytz.timezone('Asia/Kolkata')

# ==============================
# 🗄️ DB FUNCTIONS
# ==============================

def get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

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
# 🔐 LOGIN
# ==============================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect('/')
        else:
            return render_template("login.html")

    return render_template("login.html")

# ==============================
# 🔓 LOGOUT
# ==============================

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ==============================
# 🏠 HOME (PROTECTED)
# ==============================

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template("index.html")

# ==============================
# 📊 GET DATA (TODAY)
# ==============================

@app.route('/data')
def get_data():
    if 'user' not in session:
        return jsonify([])   # ⚠️ important (avoid redirect loop)

    today = datetime.now(IST).strftime("%Y-%m-%d")

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
# 📡 SCAN API (PICO)
# ==============================

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()

    if not data or "uid" not in data:
        return jsonify({"status": "error"})

    uid = data["uid"]
    now = datetime.now(IST)

    conn = get_db()
    cursor = conn.cursor()

    # 🔍 CHECK DUPLICATE
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
        last_dt = IST.localize(last_dt)

        diff = (now - last_dt).total_seconds() / 60

        if diff < CLASS_DURATION:
            conn.close()
            return jsonify({"status": "duplicate"})

    # ✅ INSERT
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
    if 'user' not in session:
        return redirect('/login')

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
    if 'user' not in session:
        return redirect('/login')

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