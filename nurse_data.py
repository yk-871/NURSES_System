import pandas as pd
import numpy as np
import random

def generate_nurse_dataset():
    # Lists for random generation
    malaysian_names = [
        "Ahmad Bin Abdullah", "Siti Aminah", "Raj Kumar", "Li Wei", "Nurul Huda",
        "Mohammed Ismail", "Tang Mei Ling", "Kumar Vel", "Nur Fasihah", "Lee Chong Wei",
        "Aisyah Binti Osman", "Mohd Farid", "Tan Siew Ling", "Vijay Anand", "Nur Sabrina",
        "Cheong Kah Mun", "Syafiq Hakim", "Gurpreet Singh", "Chong Mei Yi", "Hafiz Rahman",
        "Liew Wei Jun", "Balakrishnan", "Noraini Binti Hassan", "Chin Wei Ming", "Arun Raj",
        "Fazira Binti Musa", "Lim Sze Hui", "Daniel Wong", "Aiman Hakim", "Indira Devi",
        "Ong Chee Seng", "Amirul Hafiz", "Nisha Kumari", "Ng Mei Xian", "Mohd Zulkifli",
        "Chan Yew Hong", "Pavithra Devi", "Mohd Khairul", "Tan Jia Wei", "Abdul Rahman",
        "Wong Siew Mei", "Suresh Kumar", "Mazlina Binti Ali", "Chong Wei Han", "Harvinder Kaur",
        "Azman Bin Salleh", "Cheah Pei Ling", "Ravi Chandran", "Nur Syuhada", "Low Li Ting",
        "Mohd Faizal", "Lee Kah Wai", "Siti Zubaidah", "Tan Chee Keong", "Anusha Devi",
        "Mohd Fadli", "Yap Wai Mun", "Nurul Izzah", "Koh Siew Ling", "Pravin Kumar",
        "Abdul Malik", "Chia Hui Ying", "Siti Khadijah", "Lim Jun Hao", "Rajesh Nair",
        "Norlina Binti Omar", "Chong Li Xian", "Kavitha Rani", "Mohd Shahril", "Yong Mei Hui",
        "Farhan Bin Idris", "Tan Wei Ming", "Viknesh Kumar", "Rozita Binti Ahmad", "Wong Kah Mun",
        "Nur Aina Sofea", "Mohd Firdaus", "Ng Li Wei", "Siti Mariam", "Lau Chee Hong",
        "Devika Rani", "Mohd Hanif", "Lee Jia Xin", "Afiqah Binti Roslan", "Cheong Wei Jun",
        "Manivannan", "Nurul Nadia", "Hafizah Binti Rahim", "Lim Jia Le", "Subramaniam",
        "Mohd Rashid", "Liew Pei Ying", "Siti Fatimah", "Goh Kah Wai", "Thinesh Kumar",
        "Nur Amirah", "Mohd Danish", "Chin Jia Hui", "Tan Ai Ling", "Ariff Bin Rahman"
    ]
    
    departments = ['GW', 'ICU', 'ED']  # GW=General Ward, ICU=Intensive Care, ED=Emergency
    employment_types = ['Full-time', 'Part-time', 'Contract']
    shift_preferences = ['Morning', 'Evening', 'Night', 'Any']
    
    # Define categories according to the desired ratio (5:5:6:12:5)
    Totalnurses = 30
    categories = (
        ['Senior Nursing Officer'] * int(6 / 30 * Totalnurses) +
        ['Nursing Officer'] * int(6 / 30 * Totalnurses) +
        ['Senior Staff Nurse'] * int(6 / 30 * Totalnurses) +
        ['Staff Nurse'] * int(7 / 30 * Totalnurses) +
        ['Assistant Nurse'] * int(5 / 30 * Totalnurses)
    )

    random.shuffle(categories)
    
    # Define department distribution (6 ED : 6 ICU : 10 GW)
    # Total = 3 + 4 + 15 = 22, but we have 33 nurses
    # We need to distribute 33 nurses across departments
    # Let's calculate the exact distribution
    total_nurses = len(categories)
    ed_nurses = int(total_nurses * 7/21)
    icu_nurses = int(total_nurses * 7/21)
    gw_nurses = total_nurses - ed_nurses - icu_nurses
    
    # Create department assignments
    department_assignments = (
        ['ED'] * ed_nurses +
        ['ICU'] * icu_nurses +
        ['GW'] * gw_nurses
    )
    random.shuffle(department_assignments)
    
    nurses = []
    nurse_id = 1000  # Starting ID
    
    for i, category in enumerate(categories):
        department = department_assignments[i]
        
        # Set grade based on category
        if category == 'Senior Nursing Officer':
            grade = random.choice(['U44', 'U48'])
        elif category == 'Nursing Officer':
            grade = 'U41'
        elif category == 'Senior Staff Nurse':
            grade = random.choice(['U32', 'U36'])
        elif category == 'Staff Nurse':
            grade = 'U29'
        elif category == 'Assistant Nurse':
            grade = 'U19'
        
        # Set experience based on grade
        if grade == 'U19':
            experience = random.randint(2, 5)
        elif grade == 'U29':
            experience = random.randint(4, 8)
        elif grade in ['U32', 'U36']:
            experience = random.randint(9, 15)
        elif grade == 'U41':
            experience = random.randint(16, 20)
        elif grade in ['U44', 'U48']:
            experience = random.randint(21, 25)
        else:
            experience = random.randint(4, 25)
        
        # Set role based on department and grade
        if department == 'ICU':
            if grade in ['U44', 'U48']:
                role = 'ICU Specialist'
            else:
                role = 'ICU Nurse'
        elif department == 'ED':
            if grade in ['U41', 'U44', 'U48']:
                role = 'ED Specialist'
            else:
                role = 'ED Nurse'
        else:  # GW
            if grade in ['U44', 'U48']:
                role = 'Charge Nurse'
            elif grade == 'U41':
                role = 'Nursing Officer'
            elif grade in ['U32', 'U36']:
                role = 'Senior Staff Nurse'
            elif grade == 'U29':
                role = 'Staff Nurse'
            elif grade == 'U19':
                role = 'Assistant Nurse'
        
        nurse = {
            'id': f'N{nurse_id}',
            'name': random.choice(malaysian_names),
            'department': department,
            'role': role,
            'grade': grade,
            'skills': {department, role},
            'max_shifts_per_week': 5 if random.random() > 0.2 else 3,
            'employment_type': random.choice(employment_types),
            'preferred_shifts': random.choice(shift_preferences),
            'seniority': experience,
            'specializations': set()
        }
        
        # Add specializations based on role and experience
        if experience > 10:
            nurse['specializations'].add('Critical Care')
        if department == 'ICU':
            nurse['specializations'].add('Ventilator Management')
        if department == 'ED':
            nurse['specializations'].add('Trauma Care')
        
        nurses.append(nurse)
        nurse_id += 1
    
    return pd.DataFrame(nurses)

# Generate and save the dataset
nurses_df = generate_nurse_dataset()
nurses_df.to_csv('csv/nurse_database.csv', index=False)

# Print sample of the dataset
print(nurses_df.head())

# Print distribution counts
print("\nCategory Distribution:")
print(nurses_df['role'].value_counts())
print("\nDepartment Distribution:")
print(nurses_df['department'].value_counts())

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
