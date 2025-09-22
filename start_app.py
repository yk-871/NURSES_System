import os
from flask import Flask, send_from_directory, redirect
from attendance_api import app as attendance_app

# Create main app
app = Flask(__name__)
app.secret_key = 'nurse_scheduler_2024'

# Register API routes
app.register_blueprint(attendance_app)

@app.route('/')
def index():
    return send_from_directory('mobile_app', 'login.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('mobile_app', filename)

if __name__ == '__main__':
    print("🚀 Starting Nurse Attendance App...")
    print("📱 Open http://localhost:5000 in your browser")
    print("👑 Admin login: admin or 1001")
    app.run(debug=True, host='0.0.0.0', port=5000)