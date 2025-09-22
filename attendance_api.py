from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from scheduling_ai import load_models, predict_next_week, schedule_nurses_optimized
import pandas as pd

app = Flask(__name__)
app.secret_key = 'nurse_scheduler_2024'
CORS(app, supports_credentials=True)

ATTENDANCE_FILE = "data/attendance.json"
ADMIN_IDS = ["admin", "1001"]  # Admin nurse IDs

def load_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_attendance(data):
    os.makedirs("data", exist_ok=True)
    with open(ATTENDANCE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    nurse_id = data.get('nurse_id')
    
    try:
        with open("csv/nurse_database.json", "r") as f:
            nurses = json.load(f)
        
        nurse = next((n for n in nurses if str(n["id"]) == str(nurse_id)), None)
        if nurse:
            session['nurse_id'] = nurse_id
            session['nurse_name'] = nurse.get('name', f'Nurse {nurse_id}')
            session['is_admin'] = nurse_id in ADMIN_IDS
            
            return jsonify({
                "success": True,
                "nurse": {
                    "id": nurse_id,
                    "name": nurse.get('name'),
                    "is_admin": session['is_admin']
                }
            })
        else:
            return jsonify({"error": "Invalid Nurse ID"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/api/checkin', methods=['POST'])
def checkin():
    if 'nurse_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    nurse_id = session['nurse_id']
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    attendance = load_attendance()
    if nurse_id not in attendance:
        attendance[nurse_id] = {}
    
    if date_str not in attendance[nurse_id]:
        attendance[nurse_id][date_str] = {}
    
    attendance[nurse_id][date_str]['checkin'] = time_str
    attendance[nurse_id][date_str]['status'] = 'checked_in'
    
    save_attendance(attendance)
    
    return jsonify({
        "success": True,
        "message": f"Checked in at {time_str}",
        "time": time_str
    })

@app.route('/api/checkout', methods=['POST'])
def checkout():
    if 'nurse_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    nurse_id = session['nurse_id']
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    attendance = load_attendance()
    if nurse_id not in attendance or date_str not in attendance[nurse_id]:
        return jsonify({"error": "No check-in record found"}), 400
    
    checkin_time = attendance[nurse_id][date_str].get('checkin')
    if not checkin_time:
        return jsonify({"error": "No check-in record found"}), 400
    
    attendance[nurse_id][date_str]['checkout'] = time_str
    attendance[nurse_id][date_str]['status'] = 'checked_out'
    
    # Calculate hours worked
    checkin_dt = datetime.strptime(f"{date_str} {checkin_time}", "%Y-%m-%d %H:%M:%S")
    checkout_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    hours_worked = (checkout_dt - checkin_dt).total_seconds() / 3600
    attendance[nurse_id][date_str]['hours_worked'] = round(hours_worked, 2)
    
    save_attendance(attendance)
    
    return jsonify({
        "success": True,
        "message": f"Checked out at {time_str}",
        "time": time_str,
        "hours_worked": round(hours_worked, 2)
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    if 'nurse_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    nurse_id = session['nurse_id']
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    attendance = load_attendance()
    today_record = attendance.get(nurse_id, {}).get(date_str, {})
    
    return jsonify({
        "nurse_id": nurse_id,
        "nurse_name": session['nurse_name'],
        "is_admin": session.get('is_admin', False),
        "today": today_record,
        "status": today_record.get('status', 'not_checked_in')
    })

@app.route('/api/schedule', methods=['POST'])
def generate_schedule():
    if 'nurse_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        data = request.json
        days = data.get('days', 7)
        
        models = load_models()
        df = pd.read_csv("dataset/covid_dataset.csv", parse_dates=["Date"], dayfirst=True)
        
        with open("csv/nurse_database.json", "r") as f:
            nurses = json.load(f)
        
        week_demand = predict_next_week(df, models, days=days)
        wards = ["ED", "GW", "ICU"]
        shifts = ["Morning", "Evening", "Night"]
        schedule_df, summary_df, nurse_hours = schedule_nurses_optimized(
            week_demand, nurses, wards, shifts
        )
        
        if schedule_df is not None:
            schedule_dict = schedule_df.to_dict('index')
            summary_dict = summary_df.to_dict('records')
            
            return jsonify({
                "success": True,
                "schedule": schedule_dict,
                "summary": summary_dict,
                "nurse_hours": nurse_hours,
                "generated_at": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Could not generate schedule"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/attendance/report', methods=['GET'])
def attendance_report():
    if 'nurse_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Admin access required"}), 403
    
    attendance = load_attendance()
    return jsonify({"attendance": attendance})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)