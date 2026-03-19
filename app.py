from flask import Flask, request, jsonify, render_template, redirect, session, send_file
from datetime import datetime
import pandas as pd
import os
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.secret_key = "super_secret_key_2026"

# Fix for Render proxy
app.wsgi_app = ProxyFix(app.wsgi_app)

# In-memory storage
attendance = []

# Student database
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

# 🔓 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# 📡 RFID SCAN (FIXED: POST METHOD)
@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No JSON received"})

        uid = data.get('uid')

        if not uid:
            return jsonify({"status": "error", "message": "No UID provided"})

        name = students.get(uid, "Unknown")

        # Prevent duplicate
        for record in attendance:
            if record["uid"] == uid:
                return jsonify({"status": "already marked"})

        record = {
            "uid": uid,
            "name": name,
            "time": datetime.now().strftime("%H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        attendance.append(record)

        return jsonify({"status": "success", "data": record})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# 📊 DATA API (for dashboard)
@app.route('/data')
def data():
    return jsonify(attendance)

# 📁 EXPORT EXCEL
@app.route('/export')
def export():
    try:
        if not attendance:
            return "No data available"

        df = pd.DataFrame(attendance)
        file_path = "attendance.xlsx"
        df.to_excel(file_path, index=False, engine='openpyxl')

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}"

# 🖥 DASHBOARD
@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')

    return render_template("index.html")

# 🚀 RUN (for local only)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))