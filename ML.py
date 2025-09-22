# train_models_from_patient_data.py
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# ---------- Config ----------
DATASET_CSV = "dataset/covid_dataset.csv"   # columns: Date,New case,ICU,Nurse_demand,Admission,GW_Nurses,ICU_Nurses,ED_Nurses
models_dir = "models"
os.makedirs(models_dir, exist_ok=True)

# ---------- Load dataset ----------
df = pd.read_csv(DATASET_CSV, parse_dates=['Date'], dayfirst=True)

# Handle missing values
df = df.fillna(0)  # Fill NaN with 0

# Features
X = df[["New case", "ICU", "Admission"]]

# --- Model 1: Predict total Nurse_demand ---
y_total = df["Nurse_demand"]
model_total = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
model_total.fit(X, y_total)
joblib.dump(model_total, os.path.join(models_dir, "total_nurse_demand.pkl"))
print("[OK] Saved model: total_nurse_demand.pkl")

# --- Model 2: Predict per-ward nurse demand ---
ward_targets = {
    "GW": "GW_Nurses",
    "ICU": "ICU_Nurses",
    "ED": "ED_Nurses"
}

for ward, col in ward_targets.items():
    y = df[col]
    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X, y)
    joblib.dump(model, os.path.join(models_dir, f"{ward}_nurse_demand.pkl"))
    print(f"[OK] Saved model: {ward}_nurse_demand.pkl")

print("[SUCCESS] Training complete. Models saved in 'models/' folder.")
