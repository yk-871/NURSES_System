from flask import Blueprint, request, jsonify
import json
import pandas as pd
import os
from datetime import datetime, timedelta

app = Blueprint('api', __name__)

# Load models once at startup
models = None
try:
    from scheduling_ai import load_models, predict_next_week, schedule_nurses_optimized
    models = load_models()
    print("✅ Models loaded successfully")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    print("⚠️  API will work with mock data")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "models_loaded": models is not None})

@app.route('/nurses', methods=['GET'])
def get_nurses():
    try:
        with open("csv/nurse_database.json", "r", encoding="utf-8") as f:
            nurses = json.load(f)
        return jsonify({"nurses": nurses})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/schedule', methods=['POST'])
def generate_schedule():
    try:
        data = request.json
        days = data.get('days', 7)
        
        # Load dataset
        df = pd.read_csv("dataset/covid_dataset.csv", parse_dates=["Date"], dayfirst=True)
        
        # Load nurses
        with open("csv/nurse_database.json", "r", encoding="utf-8") as f:
            nurses = json.load(f)
        
        # Predict demand
        week_demand = predict_next_week(df, models, days=days)
        
        # Generate schedule
        wards = ["ED", "GW", "ICU"]
        shifts = ["Morning", "Evening", "Night"]
        schedule_df, summary_df, nurse_hours = schedule_nurses_optimized(
            week_demand, nurses, wards, shifts
        )
        
        if schedule_df is not None:
            # Convert to mobile-friendly format
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

@app.route('/nurse/<nurse_id>/schedule', methods=['GET'])
def get_nurse_schedule(nurse_id):
    try:
        # Generate current week schedule (simplified)
        df = pd.read_csv("dataset/covid_dataset.csv", parse_dates=["Date"], dayfirst=True)
        with open("csv/nurse_database.json", "r", encoding="utf-8") as f:
            nurses = json.load(f)
        
        week_demand = predict_next_week(df, models, days=7)
        wards = ["ED", "GW", "ICU"]
        shifts = ["Morning", "Evening", "Night"]
        schedule_df, _, _ = schedule_nurses_optimized(week_demand, nurses, wards, shifts)
        
        if schedule_df is not None:
            # Find nurse by ID
            nurse = next((n for n in nurses if str(n["id"]) == str(nurse_id)), None)
            if not nurse:
                return jsonify({"error": "Nurse not found"}), 404
            
            nurse_name = nurse.get("name", f"ID {nurse['id']}")
            if nurse_name in schedule_df.index:
                nurse_schedule = schedule_df.loc[nurse_name].to_dict()
                return jsonify({
                    "nurse_id": nurse_id,
                    "nurse_name": nurse_name,
                    "schedule": nurse_schedule
                })
            else:
                return jsonify({"error": "Schedule not found for nurse"}), 404
        else:
            return jsonify({"error": "Could not generate schedule"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This is now a blueprint, not a standalone app