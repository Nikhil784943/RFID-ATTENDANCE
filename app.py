from flask import Flask, request, jsonify, render_template, redirect, session, send_file
from datetime import datetime
import pandas as pd
import os

from database import init_db, insert_record, get_all_records

app = Flask(__name__)
app.secret_key = "super_secret_key_2026"

# Initialize database
init_db()

# Student data
students = {
    "91285723": "Abhishek",
    "1409145362": "Animesh",
    "77146475": "Nikhil"
}


# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "1234":
            session['logged_in'] = True
            return redirect('/')
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# 📡 RFID SCAN API
@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No JSON received"}), 400

        uid = data.get('uid')

        if not uid:
            return jsonify({"status": "error", "message": "UID missing"}), 400

        name = students.get(uid, "Unknown")

        time_now = datetime.now().strftime("%H:%M:%S")
        date_now = datetime.now().strftime("%Y-%m-%d")

        insert_record(uid, name, time_now, date_now)

        return jsonify({
            "status": "success",
            "data": {
                "uid": uid,
                "name": name,
                "time": time_now,
                "date": date_now
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 📊 DATA API (for dashboard)
@app.route('/data')
def data():
    rows = get_all_records()

    result = []
    for r in rows:
        result.append({
            "uid": r[0],
            "name": r[1],
            "time": r[2],
            "date": r[3]
        })

    return jsonify(result)


# 📁 EXPORT EXCEL
@app.route('/export')
def export():
    rows = get_all_records()

    if not rows:
        return "No data available"

    df = pd.DataFrame(rows, columns=["UID", "Name", "Time", "Date"])

    file_path = "attendance.xlsx"
    df.to_excel(file_path, index=False, engine='openpyxl')

    return send_file(file_path, as_attachment=True)


# 🖥 DASHBOARD
@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')

    return render_template("index.html")


# 🚀 RUN
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)