import json

# Your Python dictionaries
shifts = {
    "Morning": {"start": "07:00", "end": "15:00"},
    "Evening": {"start": "15:00", "end": "23:00"},
    "Night": {"start": "23:00", "end": "07:00"},
}

department_staffing = {
    "GW": {
        "Morning": {"Charge/Senior": 1, "RN": 3, "AN": 2},
        "Evening": {"Senior": 1, "RN": 2, "AN": 1},
        "Night": {"Senior": 1, "RN": 2, "AN": 1},
    },
    "ICU": {
        "Any": {"Charge": 1, "RN": 3, "Tech": 1},
    },
    "ED": {
        "Peak": {"Senior": 1, "RN": 3, "ED_RN": 1},
        "Off-Peak": {"Senior": 1, "RN": 2},
    }
}

grade_replacement = {
    "U54": ["U44","U48","U41","U36","U32","U29","U19"],
    "U52": ["U44","U48","U41","U36","U32","U29","U19"],
    "U48": ["U41","U36","U32","U29","U19"],
    "U44": ["U41","U36","U32","U29","U19"],
    "U41": ["U36","U32","U29","U19"],
    "U36": ["U32","U29","U19"],
    "U32": ["U29","U19"],
    "U29": ["U19"],
}

# Combine all into a single dictionary
config = {
    "shifts": shifts,
    "department_staffing": department_staffing,
    "grade_replacement": grade_replacement
}

# Convert to JSON string
json_str = json.dumps(config, indent=4)

# Save to file
with open("csv/hospital_config.json", "w") as f:
    f.write(json_str)

print("JSON saved to hospital_config.json")

import pandas as pd

# Load your CSV
csv_file = "csv/nurse_database.csv"
df = pd.read_csv(csv_file)

# Optional: convert string representations of sets to actual Python lists
# This handles columns like 'skills' or 'specializations'
for col in ["skills", "specializations"]:
    df[col] = df[col].apply(lambda x: list(eval(x)) if pd.notnull(x) else [])

# Convert the DataFrame to a list of dictionaries
nurses_list = df.to_dict(orient="records")

# Save as JSON
json_file = "csv/nurse_database.json"
with open(json_file, "w") as f:
    json.dump(nurses_list, f, indent=4)

print(f"JSON saved to {json_file}")
