from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import sys
import warnings
warnings.filterwarnings('ignore')

try:
    import google.generativeai as genai
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        GEMINI_AVAILABLE = False
        print("⚠️ GEMINI_API_KEY not set - AI chat will use fallback responses")
    else:
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )
        GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Gemini AI not available. Install google-generativeai package.")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'nurse_scheduler_2024')
CORS(app, supports_credentials=True)

ATTENDANCE_FILE = "data/attendance.json"
MC_FILE = "data/mc_requests.json"
EMERGENCY_FILE = "data/emergency_calls.json"
SWAP_FILE = "data/shift_swaps.json"
ADMIN_IDS = ["N1001", "N1015"]  # Use existing nurse IDs as admins

def load_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_attendance(data):
    os.makedirs("data", exist_ok=True)
    with open(ATTENDANCE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_mc_requests():
    if os.path.exists(MC_FILE):
        with open(MC_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_mc_requests(data):
    os.makedirs("data", exist_ok=True)
    with open(MC_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_emergency_calls():
    if os.path.exists(EMERGENCY_FILE):
        with open(EMERGENCY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_emergency_calls(data):
    os.makedirs("data", exist_ok=True)
    with open(EMERGENCY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_shift_swaps():
    if os.path.exists(SWAP_FILE):
        with open(SWAP_FILE, 'r') as f:
            return json.load(f)
    return []

def save_shift_swaps(data):
    os.makedirs("data", exist_ok=True)
    with open(SWAP_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return send_from_directory('mobile_app', 'login.html')

@app.route('/main')
def main_app():
    return send_from_directory('mobile_app', 'main.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('mobile_app', filename)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    nurse_id = data.get('nurse_id')
    password = data.get('password')
    
    if not nurse_id or not password:
        return jsonify({"error": "Nurse ID and password required"}), 401
    
    # Check password format: nurseID_Hack
    expected_password = f"{nurse_id}_Hack"
    if password != expected_password:
        return jsonify({"error": "Invalid credentials"}), 401
    
    try:
        with open("csv/nurse_database.json", "r") as f:
            nurses = json.load(f)
        
        nurse = next((n for n in nurses if str(n["id"]) == str(nurse_id)), None)
        if nurse:
            session['nurse_id'] = nurse_id
            session['nurse_name'] = nurse.get('name', f'Nurse {nurse_id}')
            session['is_admin'] = nurse_id in ADMIN_IDS
            
            # Log active user
            user_type = "ADMIN" if session['is_admin'] else "USER"
            print(f"🔐 LOGIN: {session['nurse_name']} ({nurse_id}) - {user_type}")
            
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
    # Log logout
    if 'nurse_name' in session and 'nurse_id' in session:
        print(f"🚪 LOGOUT: {session['nurse_name']} ({session['nurse_id']})")
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
    
    data = request.json or {}
    admission_data = data.get('admission_data', {})
    
    try:
        # Save admission data if provided
        if admission_data:
            with open('temp_admission_data.json', 'w') as f:
                json.dump(admission_data, f)
        
        # Run the actual AI scheduling system
        result = subprocess.run([sys.executable, 'scheduling_ai.py'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            # Read the generated schedule
            if os.path.exists('output_schedule.xlsx'):
                df = pd.read_excel('output_schedule.xlsx', sheet_name='Schedule')
                # Also save as CSV for compatibility
                df.to_csv('output_schedule.csv', index=False)
                
                # Auto backup to S3 after schedule generation
                try:
                    from s3_operations import backup_to_s3
                    success, backup_id = backup_to_s3()
                    backup_msg = f" (Backed up to S3: {backup_id})" if success else ""
                except Exception as e:
                    backup_msg = f" (S3 backup failed: {str(e)})"
                
                # Clean up temp file
                if os.path.exists('temp_admission_data.json'):
                    os.remove('temp_admission_data.json')
                
                return jsonify({
                    "success": True,
                    "message": f"AI-optimized schedule generated successfully!{backup_msg}",
                    "generated_at": datetime.now().isoformat()
                })
            else:
                return jsonify({"error": "Schedule file not generated"}), 500
        else:
            return jsonify({"error": f"Scheduling failed: {result.stderr}"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/schedule/upload', methods=['POST'])
def upload_schedule_data():
    if 'nurse_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Admin access required"}), 403
    
    if 'admission_file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['admission_file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        # Save uploaded file temporarily first
        temp_filename = f"temp_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file.save(temp_filename)
        
        # Try reading as text first
        try:
            # Simple text-based parsing
            with open(temp_filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                return jsonify({"error": "Uploaded file is empty"}), 400
            
            # Parse manually
            header = lines[0].strip().split(',')
            data_rows = []
            for line in lines[1:]:
                if line.strip():
                    data_rows.append(line.strip().split(','))
            
            new_data = pd.DataFrame(data_rows, columns=header)
            print(f"Manual parsing successful: {new_data.shape}")
            print(f"Columns: {list(new_data.columns)}")
            
        except Exception as manual_error:
            print(f"Manual parsing failed: {manual_error}")
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            return jsonify({"error": f"File parsing failed: {str(manual_error)}"}), 400
        
        # Append to existing dataset
        dataset_path = 'dataset/covid_dataset.csv'
        if os.path.exists(dataset_path):
            existing_data = pd.read_csv(dataset_path)
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            combined_data = new_data
        
        # Save updated dataset
        combined_data.to_csv(dataset_path, index=False)
        print(f"Updated dataset saved with {len(combined_data)} rows")
        
        # Clean up temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        
        # Retrain models
        print("Retraining ML models...")
        ml_result = subprocess.run([sys.executable, 'ML.py'], 
                                 capture_output=True, text=True, cwd='.')
        
        if ml_result.returncode != 0:
            return jsonify({"error": f"Model training failed: {ml_result.stderr}"}), 500
        
        print("Models retrained successfully")
        
        # Generate new schedules
        result = subprocess.run([sys.executable, 'scheduling_ai.py'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            if os.path.exists('output_schedule.xlsx'):
                df = pd.read_excel('output_schedule.xlsx', sheet_name='Schedule')
                df.to_csv('output_schedule.csv', index=False)
                
                # Log schedule generation
                admin_name = session.get('nurse_name', 'Unknown')
                admin_id = session.get('nurse_id', 'Unknown')
                print(f"📅 SCHEDULE GENERATED by {admin_name} ({admin_id})")
                
                # Auto backup to S3 after schedule generation
                try:
                    from s3_operations import backup_to_s3
                    success, backup_id = backup_to_s3()
                    backup_msg = f" (Backed up to S3: {backup_id})" if success else ""
                    if success:
                        print(f"📤 AUTO-BACKUP: {backup_id}")
                except Exception as e:
                    backup_msg = f" (S3 backup failed: {str(e)})"
                    print(f"❌ BACKUP FAILED: {str(e)}")
                
                # Get current week info
                week_info = ""
                if os.path.exists('current_week.txt'):
                    with open('current_week.txt', 'r') as f:
                        current_week = f.read().strip()
                        week_info = f" for week starting {current_week}"
                
                return jsonify({
                    "success": True,
                    "message": f"Models retrained and schedule generated{week_info}!{backup_msg}",
                    "generated_at": datetime.now().isoformat()
                })
            else:
                return jsonify({"error": "Schedule file not generated"}), 500
        else:
            return jsonify({"error": f"Scheduling failed: {result.stderr}"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/attendance/report', methods=['GET'])
def attendance_report():
    if 'nurse_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Admin access required"}), 403
    
    attendance = load_attendance()
    return jsonify({"attendance": attendance})

def check_schedule(nurse_identifier):
    """Return the schedule of a nurse using name or ID."""
    try:
        # Try to load from Excel first, then CSV
        if os.path.exists("output_schedule.xlsx"):
            df = pd.read_excel("output_schedule.xlsx", sheet_name="Schedule")
        elif os.path.exists("output_schedule.csv"):
            df = pd.read_csv("output_schedule.csv")
        else:
            return f"No schedule file found. Please generate a schedule first."
        
        # Search by nurse ID first (exact match)
        nurse_row = pd.DataFrame()  # Initialize as empty DataFrame
        if 'Nurse_ID' in df.columns:
            nurse_row = df[df['Nurse_ID'].astype(str) == str(nurse_identifier)]
        
        # If no match by ID, try by name (partial match)
        if nurse_row.empty and 'Name' in df.columns:
            nurse_row = df[df["Name"].str.contains(nurse_identifier, case=False, na=False)]
        
        if not nurse_row.empty:
            nurse_data = nurse_row.iloc[0]
            nurse_id = nurse_data.get('Nurse_ID', 'N/A')
            nurse_name = nurse_data.get('Name', 'Unknown')
            schedule_lines = [f"Schedule for {nurse_name} (ID: {nurse_id}):"]
            schedule_lines.append("=" * 50)
            
            # Get all schedule columns (excluding Nurse_ID and Name)
            schedule_columns = [col for col in df.columns if col not in ['Nurse_ID', 'Name']]
            
            # Group by day (Monday, Tuesday, etc.)
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for day_name in days:
                day_columns = [col for col in schedule_columns if col.startswith(day_name)]
                
                if day_columns:
                    day_schedule = []
                    for col in day_columns:
                        shift_value = nurse_data.get(col, 'Off')
                        if shift_value != 'Off':
                            if 'Morning' in col:
                                day_schedule.append(f"Morning: {shift_value}")
                            elif 'Evening' in col:
                                day_schedule.append(f"Evening: {shift_value}")
                            elif 'Night' in col:
                                day_schedule.append(f"Night: {shift_value}")
                    
                    # Extract date from column name
                    date_match = None
                    if day_columns:
                        import re
                        date_match = re.search(r'\d{4}-\d{2}-\d{2}', day_columns[0])
                    
                    date_str = f" ({date_match.group()})" if date_match else ""
                    
                    if day_schedule:
                        schedule_lines.append(f"{day_name}{date_str}: {' | '.join(day_schedule)}")
                    else:
                        schedule_lines.append(f"{day_name}{date_str}: Off")
            
            return "\n".join(schedule_lines)
        
        return f"No schedule found for '{nurse_identifier}'. Please generate a schedule first."
    except Exception as e:
        return f"Error checking schedule: {str(e)}"

def get_today_schedule(nurse_identifier):
    """Return today's schedule for a nurse."""
    try:
        # Try to load from Excel first, then CSV
        if os.path.exists("output_schedule.xlsx"):
            df = pd.read_excel("output_schedule.xlsx", sheet_name="Schedule")
        elif os.path.exists("output_schedule.csv"):
            df = pd.read_csv("output_schedule.csv")
        else:
            return "No schedule available"
        
        # Search by nurse ID first (exact match)
        nurse_row = pd.DataFrame()
        if 'Nurse_ID' in df.columns:
            nurse_row = df[df['Nurse_ID'].astype(str) == str(nurse_identifier)]
        
        if nurse_row.empty and 'Name' in df.columns:
            nurse_row = df[df["Name"].str.contains(nurse_identifier, case=False, na=False)]
        
        if not nurse_row.empty:
            nurse_data = nurse_row.iloc[0]
            today = datetime.now()
            today_str = today.strftime('%Y-%m-%d')
            day_name = today.strftime('%A')
            
            # Find today's schedule columns
            schedule_columns = [col for col in df.columns if col not in ['Nurse_ID', 'Name']]
            today_columns = [col for col in schedule_columns if today_str in col and day_name in col]
            
            if today_columns:
                today_shifts = []
                for col in today_columns:
                    shift_value = nurse_data.get(col, 'Off')
                    if shift_value != 'Off':
                        if 'Morning' in col:
                            today_shifts.append(f"Morning: {shift_value.replace('On Duty - ', '')}")
                        elif 'Evening' in col:
                            today_shifts.append(f"Evening: {shift_value.replace('On Duty - ', '')}")
                        elif 'Night' in col:
                            today_shifts.append(f"Night: {shift_value.replace('On Duty - ', '')}")
                
                if today_shifts:
                    return f"{day_name} {today_str}: {' | '.join(today_shifts)}"
                else:
                    return f"{day_name} {today_str}: Off"
            else:
                return "No schedule available for today"
        
        return "No schedule available"
    except Exception as e:
        return "No schedule available"

def get_current_week_schedule(nurse_identifier):
    """Return current week schedule for a nurse."""
    try:
        if os.path.exists("output_schedule.xlsx"):
            df = pd.read_excel("output_schedule.xlsx", sheet_name="Schedule")
        elif os.path.exists("output_schedule.csv"):
            df = pd.read_csv("output_schedule.csv")
        else:
            return "No schedule available"
        
        nurse_row = pd.DataFrame()
        if 'Nurse_ID' in df.columns:
            nurse_row = df[df['Nurse_ID'].astype(str) == str(nurse_identifier)]
        
        if nurse_row.empty and 'Name' in df.columns:
            nurse_row = df[df["Name"].str.contains(nurse_identifier, case=False, na=False)]
        
        if not nurse_row.empty:
            nurse_data = nurse_row.iloc[0]
            today = datetime.now()
            
            # Get current week Monday
            days_since_monday = today.weekday()
            current_monday = today - timedelta(days=days_since_monday)
            
            current_week_schedule = []
            for i in range(7):
                day_date = current_monday + timedelta(days=i)
                day_str = day_date.strftime('%Y-%m-%d')
                day_name = day_date.strftime('%A')
                
                schedule_columns = [col for col in df.columns if col not in ['Nurse_ID', 'Name']]
                day_columns = [col for col in schedule_columns if day_str in col and day_name in col]
                
                if day_columns:
                    day_shifts = []
                    for col in day_columns:
                        shift_value = nurse_data.get(col, 'Off')
                        if shift_value != 'Off':
                            if 'Morning' in col:
                                day_shifts.append(f"M: {shift_value.replace('On Duty - ', '')}")
                            elif 'Evening' in col:
                                day_shifts.append(f"E: {shift_value.replace('On Duty - ', '')}")
                            elif 'Night' in col:
                                day_shifts.append(f"N: {shift_value.replace('On Duty - ', '')}")
                    
                    if day_shifts:
                        current_week_schedule.append(f"{day_name} {day_str}: {', '.join(day_shifts)}")
                    else:
                        current_week_schedule.append(f"{day_name} {day_str}: Off")
            
            return "\n".join(current_week_schedule)
        
        return "No schedule available"
    except Exception as e:
        return "No schedule available"

def generate_ai_response(input_text, nurse_name=None):
    """Generate AI response using Gemini or fallback."""
    if not GEMINI_AVAILABLE:
        return get_fallback_response(input_text)
    
    try:
        # Handle sick/medical leave requests for nurses
        input_lower = input_text.lower().strip()
        
        # Check for sick nurse requests
        sick_keywords = ["im sick", "i'm sick", "i am sick", "feeling sick", "not well", "unwell", "ill"]
        if any(keyword in input_lower for keyword in sick_keywords):
            return 'I understand you\'re not feeling well. As a nurse, do you need to take medical leave? Let me help you submit an MC request.' + '''<div class="mc-form">
<h4>📋 Submit Medical Certificate</h4>
<form id="mcForm">
<div class="form-group">
<label>Start Date:</label>
<input type="date" id="startDate" required>
</div>
<div class="form-group">
<label>End Date:</label>
<input type="date" id="endDate" required>
</div>
<div class="form-group">
<label>Reason:</label>
<input type="text" id="reason" placeholder="e.g., Fever, flu symptoms" required>
</div>
<div class="form-group">
<label>Documentation:</label>
<textarea id="documentation" placeholder="Describe your medical certificate or how you will provide it" required></textarea>
</div>
<button type="button" onclick="submitMC()" class="submit-btn">Submit MC Request</button>
</form>
</div>'''
        
        # Check for leave requests
        leave_keywords = ["mc leave", "medical leave", "sick leave"]
        if any(keyword in input_lower for keyword in leave_keywords):
            return '''<div class="mc-form">
<h4>📋 Submit Medical Certificate</h4>
<form id="mcForm">
<div class="form-group">
<label>Start Date:</label>
<input type="date" id="startDate" required>
</div>
<div class="form-group">
<label>End Date:</label>
<input type="date" id="endDate" required>
</div>
<div class="form-group">
<label>Reason:</label>
<input type="text" id="reason" placeholder="e.g., Medical appointment, illness" required>
</div>
<div class="form-group">
<label>Documentation:</label>
<textarea id="documentation" placeholder="Describe your medical certificate or how you will provide it" required></textarea>
</div>
<button type="button" onclick="submitMC()" class="submit-btn">Submit MC Request</button>
</form>
</div>'''
        
        # Handle MC submission requests
        mc_keywords = ["submit mc", "medical certificate", "request mc", "take mc", "get mc", "mc request", "mc submission", "apply mc", "i wan mc", "i want mc", "need mc"]
        mc_match = input_lower == "mc" or any(keyword in input_lower for keyword in mc_keywords)
        
        if mc_match:
            return '''<div class="mc-form">
<h4>📋 Submit Medical Certificate</h4>
<form id="mcForm">
<div class="form-group">
<label>Start Date:</label>
<input type="date" id="startDate" required>
</div>
<div class="form-group">
<label>End Date:</label>
<input type="date" id="endDate" required>
</div>
<div class="form-group">
<label>Reason:</label>
<input type="text" id="reason" placeholder="e.g., Doctor's appointment, illness" required>
</div>
<div class="form-group">
<label>Documentation:</label>
<textarea id="documentation" placeholder="Describe your medical certificate or how you will provide it" required></textarea>
</div>
<button type="button" onclick="submitMC()" class="submit-btn">Submit MC Request</button>
</form>
</div>'''
        

        # Handle schedule queries
        if "schedule" in input_text.lower():
            if "i am" in input_text.lower():
                parts = input_text.split("I am") if "I am" in input_text else input_text.split("i am")
                if len(parts) > 1:
                    name_part = parts[1].split(",")[0].strip()
                    return check_schedule(name_part)
            
            if "my schedule" in input_text.lower():
                # Use logged-in nurse's ID for more accurate lookup
                from flask import session
                if 'nurse_id' in session:
                    # Show both current and next week schedules
                    full_schedule = check_schedule(session['nurse_id'])
                    return full_schedule
                elif nurse_name:
                    return check_schedule(nurse_name)
                else:
                    return "Please tell me your name or ID so I can look up your schedule."
        
        # Use Gemini AI with enhanced capabilities
        response = model.generate_content([
            "input: who are you",
            "output: I am an AI-powered nurse assistant designed to help with scheduling, medical procedures, emergency protocols, and general nursing support.",
            "input: What all can you do?",
            "output: I can help with work schedules, shift management, emergency procedures, medical protocols, patient care guidance, medication information, and general nursing questions. I'm here to support you in your nursing duties.",
            f"input: {input_text}",
            "output: ",
        ])
        
        return response.text
    except Exception as e:
        return get_fallback_response(input_text)

def get_fallback_response(message):
    """Fallback responses when Gemini is not available."""
    msg = message.lower()
    
    if 'schedule' in msg:
        return 'Your schedule is available in the Schedule tab. You can also ask admin to generate new schedules.'
    elif any(keyword in msg for keyword in ['swap', 'change shift', 'shift swap', 'swap shift']):
        return '''<div class="swap-form">
<h4>🔄 Shift Swap Request</h4>
<form id="swapForm">
<div class="form-group">
<label>Current Shift to Swap:</label>
<select id="currentShift" required>
<option value="">Select your current shift</option>
<option value="Day 1 Morning">Day 1 Morning</option>
<option value="Day 1 Evening">Day 1 Evening</option>
<option value="Day 1 Night">Day 1 Night</option>
<option value="Day 2 Morning">Day 2 Morning</option>
<option value="Day 2 Evening">Day 2 Evening</option>
<option value="Day 2 Night">Day 2 Night</option>
<option value="Day 3 Morning">Day 3 Morning</option>
<option value="Day 3 Evening">Day 3 Evening</option>
<option value="Day 3 Night">Day 3 Night</option>
<option value="Day 4 Morning">Day 4 Morning</option>
<option value="Day 4 Evening">Day 4 Evening</option>
<option value="Day 4 Night">Day 4 Night</option>
<option value="Day 5 Morning">Day 5 Morning</option>
<option value="Day 5 Evening">Day 5 Evening</option>
<option value="Day 5 Night">Day 5 Night</option>
<option value="Day 6 Morning">Day 6 Morning</option>
<option value="Day 6 Evening">Day 6 Evening</option>
<option value="Day 6 Night">Day 6 Night</option>
<option value="Day 7 Morning">Day 7 Morning</option>
<option value="Day 7 Evening">Day 7 Evening</option>
<option value="Day 7 Night">Day 7 Night</option>
</select>
</div>
<div class="form-group">
<label>Desired Shift:</label>
<select id="desiredShift" required>
<option value="">Select desired shift</option>
<option value="Day 1 Morning">Day 1 Morning</option>
<option value="Day 1 Evening">Day 1 Evening</option>
<option value="Day 1 Night">Day 1 Night</option>
<option value="Day 2 Morning">Day 2 Morning</option>
<option value="Day 2 Evening">Day 2 Evening</option>
<option value="Day 2 Night">Day 2 Night</option>
<option value="Day 3 Morning">Day 3 Morning</option>
<option value="Day 3 Evening">Day 3 Evening</option>
<option value="Day 3 Night">Day 3 Night</option>
<option value="Day 4 Morning">Day 4 Morning</option>
<option value="Day 4 Evening">Day 4 Evening</option>
<option value="Day 4 Night">Day 4 Night</option>
<option value="Day 5 Morning">Day 5 Morning</option>
<option value="Day 5 Evening">Day 5 Evening</option>
<option value="Day 5 Night">Day 5 Night</option>
<option value="Day 6 Morning">Day 6 Morning</option>
<option value="Day 6 Evening">Day 6 Evening</option>
<option value="Day 6 Night">Day 6 Night</option>
<option value="Day 7 Morning">Day 7 Morning</option>
<option value="Day 7 Evening">Day 7 Evening</option>
<option value="Day 7 Night">Day 7 Night</option>
</select>
</div>
<div class="form-group">
<label>Reason for Swap:</label>
<textarea id="swapReason" placeholder="Please explain why you need this shift swap" required></textarea>
</div>
<button type="button" onclick="submitSwapRequest()" class="submit-btn">Submit Swap Request</button>
</form>
</div>'''
    elif 'emergency' in msg or 'procedure' in msg:
        return '''Emergency Procedures:<br>
• **Code Blue (Cardiac Arrest)**: Call 2222 immediately, start CPR if trained<br>
• **Fire Emergency**: Call 3333, evacuate patients safely, use RACE protocol<br>
• **Security Alert**: Call 4444 for violent patients or intruders<br>
• **Medical Emergency**: Assess patient, call doctor, prepare emergency cart<br>
• **Choking**: Heimlich maneuver for conscious patients, back blows for infants<br>
• **Severe Bleeding**: Apply direct pressure, elevate if possible, call for help<br>
• **Allergic Reaction**: Check for EpiPen, call doctor, monitor airway<br>
• **Fall**: Don't move patient, assess injuries, call doctor<br>
• **Medication Error**: Stop administration, assess patient, report immediately<br>
• **Equipment Failure**: Switch to backup, call maintenance, document incident<br><br>
Always follow your hospital's specific protocols and call for help when needed.'''
    elif 'protocol' in msg:
        return 'I do not have access to real-time information, including ward protocols. Those are specific to individual hospitals and healthcare facilities. To find out about ward protocols, you should consult your hospital\'s internal documentation, your supervisor, or a senior nurse on the ward.'
    elif any(keyword in msg for keyword in ['mc', 'medical certificate', 'request mc', 'take mc', 'get mc', 'i wan mc', 'i want mc', 'need mc', 'sick leave', 'medical leave']) or msg.strip() == 'mc':
        return '''<div class="mc-form">
<h4>📋 Submit Medical Certificate</h4>
<form id="mcForm">
<div class="form-group">
<label>Start Date:</label>
<input type="date" id="startDate" required>
</div>
<div class="form-group">
<label>End Date:</label>
<input type="date" id="endDate" required>
</div>
<div class="form-group">
<label>Reason:</label>
<input type="text" id="reason" placeholder="e.g., Doctor's appointment, illness" required>
</div>
<div class="form-group">
<label>Documentation:</label>
<textarea id="documentation" placeholder="Describe your medical certificate or how you will provide it" required></textarea>
</div>
<button type="button" onclick="submitMC()" class="submit-btn">Submit MC Request</button>
</form>
</div>'''
    elif 'help' in msg:
        return 'I can help with:<br>• Schedule information<br>• Emergency procedures<br>• Ward protocols<br>• Shift swaps (say "shift swap")<br>• MC submissions (say "request mc")'
    else:
        return f'I understand you\'re asking about: "{message}". I\'m here to help with nursing questions, medical procedures, emergency protocols, and scheduling. What specific information do you need?'

@app.route('/api/chat', methods=['POST'])
def chat():
    if 'nurse_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    message = data.get('message', '')
    nurse_name = session.get('nurse_name', '')
    
    try:
        response = generate_ai_response(message, nurse_name)
        return jsonify({
            "success": True,
            "response": response
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/mc/submit', methods=['POST'])
def submit_mc():
    if 'nurse_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    nurse_id = session['nurse_id']
    nurse_name = session['nurse_name']
    
    mc_request = {
        "id": f"MC_{nurse_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "nurse_id": nurse_id,
        "nurse_name": nurse_name,
        "start_date": data.get('start_date'),
        "end_date": data.get('end_date'),
        "reason": data.get('reason'),
        "documentation": data.get('documentation'),
        "status": "pending",
        "submitted_at": datetime.now().isoformat()
    }
    
    mc_requests = load_mc_requests()
    if nurse_id not in mc_requests:
        mc_requests[nurse_id] = []
    
    mc_requests[nurse_id].append(mc_request)
    save_mc_requests(mc_requests)
    
    return jsonify({
        "success": True,
        "message": "MC request submitted successfully",
        "request_id": mc_request["id"]
    })

@app.route('/api/mc/list', methods=['GET'])
def list_mc():
    if 'nurse_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    nurse_id = session['nurse_id']
    is_admin = session.get('is_admin', False)
    
    mc_requests = load_mc_requests()
    
    if is_admin:
        all_requests = []
        for nurse_requests in mc_requests.values():
            all_requests.extend(nurse_requests)
        return jsonify({"requests": all_requests})
    else:
        nurse_requests = mc_requests.get(nurse_id, [])
        return jsonify({"requests": nurse_requests})

@app.route('/api/schedule/full', methods=['GET'])
def get_full_schedule():
    if 'nurse_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        # Try to load from Excel first, then CSV
        if os.path.exists("output_schedule.xlsx"):
            df = pd.read_excel("output_schedule.xlsx", sheet_name="Schedule")
        elif os.path.exists("output_schedule.csv"):
            df = pd.read_csv("output_schedule.csv")
        else:
            return jsonify({"error": "No schedule file found. Please generate a schedule first."}), 404
        
        # Convert to dictionary format
        schedule_data = df.to_dict('records')
        
        return jsonify({
            "success": True,
            "schedule": schedule_data,
            "total_nurses": len(schedule_data)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency/call', methods=['POST'])
def emergency_call():
    if 'nurse_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    nurse_id = session['nurse_id']
    nurse_name = session['nurse_name']
    
    # Get nurse ward information
    try:
        with open("csv/nurse_database.json", "r") as f:
            nurses = json.load(f)
        nurse_info = next((n for n in nurses if n["id"] == nurse_id), None)
        ward = nurse_info.get('department', 'Unknown') if nurse_info else 'Unknown'
        role = nurse_info.get('role', 'Nurse') if nurse_info else 'Nurse'
    except:
        ward = 'Unknown'
        role = 'Nurse'
    
    emergency_call = {
        "id": f"EMRG_{nurse_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "nurse_id": nurse_id,
        "nurse_name": nurse_name,
        "ward": ward,
        "role": role,
        "emergency_type": data.get('emergency_type'),
        "location": data.get('location', ward),
        "message": data.get('message'),
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }
    
    emergency_calls = load_emergency_calls()
    emergency_calls.append(emergency_call)
    save_emergency_calls(emergency_calls)
    
    return jsonify({
        "success": True,
        "message": "Emergency call sent to admin",
        "call_id": emergency_call["id"]
    })

@app.route('/api/emergency/list', methods=['GET'])
def list_emergency_calls():
    if 'nurse_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Admin access required"}), 403
    
    emergency_calls = load_emergency_calls()
    # Show only active calls from last 24 hours
    recent_calls = [call for call in emergency_calls 
                   if call.get('status') == 'active' and 
                   (datetime.now() - datetime.fromisoformat(call['timestamp'])).days < 1]
    
    return jsonify({"emergency_calls": recent_calls, "count": len(recent_calls)})

@app.route('/api/emergency/solve', methods=['POST'])
def solve_emergency_call():
    if 'nurse_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.json
    call_id = data.get('call_id')
    
    if not call_id:
        return jsonify({"error": "Call ID required"}), 400
    
    emergency_calls = load_emergency_calls()
    
    # Find and update the call status
    for call in emergency_calls:
        if call.get('id') == call_id:
            call['status'] = 'solved'
            call['solved_at'] = datetime.now().isoformat()
            call['solved_by'] = session['nurse_id']
            break
    else:
        return jsonify({"error": "Emergency call not found"}), 404
    
    save_emergency_calls(emergency_calls)
    
    return jsonify({
        "success": True,
        "message": "Emergency call marked as solved"
    })

@app.route('/api/swap/submit', methods=['POST'])
def submit_swap_request():
    if 'nurse_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    nurse_id = session['nurse_id']
    nurse_name = session['nurse_name']
    
    swap_request = {
        "id": f"SWAP_{nurse_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "nurse_id": nurse_id,
        "nurse_name": nurse_name,
        "current_shift": data.get('current_shift'),
        "desired_shift": data.get('desired_shift'),
        "reason": data.get('reason'),
        "status": "pending",
        "submitted_at": datetime.now().isoformat()
    }
    
    swap_requests = load_shift_swaps()
    swap_requests.append(swap_request)
    save_shift_swaps(swap_requests)
    
    return jsonify({
        "success": True,
        "message": "Shift swap request submitted successfully",
        "request_id": swap_request["id"]
    })

@app.route('/api/s3/restore', methods=['POST'])
def restore_from_s3():
    if 'nurse_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        admin_name = session.get('nurse_name', 'Unknown')
        admin_id = session.get('nurse_id', 'Unknown')
        print(f"📥 S3 RESTORE initiated by {admin_name} ({admin_id})")
        
        from s3_operations import restore_from_s3
        success, message = restore_from_s3()
        
        if success:
            print(f"✅ S3 RESTORE SUCCESS: {message}")
            return jsonify({
                "success": True,
                "message": f"Data restored from S3: {message}"
            })
        else:
            print(f"❌ S3 RESTORE FAILED: {message}")
            return jsonify({"error": f"S3 restore failed: {message}"}), 500
    except Exception as e:
        return jsonify({"error": f"S3 restore error: {str(e)}"}), 500

@app.route('/api/s3/backup', methods=['POST'])
def manual_backup_to_s3():
    if 'nurse_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        from s3_operations import backup_to_s3
        success, backup_id = backup_to_s3()
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Manual backup completed: {backup_id}"
            })
        else:
            return jsonify({"error": f"S3 backup failed: {backup_id}"}), 500
    except Exception as e:
        return jsonify({"error": f"S3 backup error: {str(e)}"}), 500

@app.route('/api/admin/reset', methods=['POST'])
def reset_data():
    if 'nurse_id' not in session or not session.get('is_admin'):
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        admin_name = session.get('nurse_name', 'Unknown')
        admin_id = session.get('nurse_id', 'Unknown')
        print(f"🔄 DATA RESET initiated by {admin_name} ({admin_id})")
        
        # Reset attendance
        save_attendance({})
        
        # Reset emergency calls
        save_emergency_calls([])
        
        print("✅ RESET COMPLETE: Attendance and Emergency calls cleared")
        
        return jsonify({
            "success": True,
            "message": "Attendance and emergency calls reset successfully"
        })
    except Exception as e:
        print(f"❌ RESET FAILED: {str(e)}")
        return jsonify({"error": f"Reset failed: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    print("🚀 Starting Nurse Attendance App...")
    print(f"📱 Running on port {port}")
    print("👑 Admin IDs: N1001, N1015")
    app.run(debug=debug, host='0.0.0.0', port=port)