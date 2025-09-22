import os
import json
from datetime import datetime

def show_data_status():
    """Show current local data status"""
    print("Nurse Scheduling System - Data Status")
    print("=" * 50)
    
    # Check database files
    files_to_check = [
        ('csv/nurse_database.json', 'Nurse Database'),
        ('csv/hospital_config.json', 'Hospital Config'),
        ('dataset/covid_dataset.csv', 'COVID Dataset'),
        ('data/attendance.json', 'Attendance Records'),
        ('data/emergency_calls.json', 'Emergency Calls'),
        ('data/mc_requests.json', 'MC Requests'),
        ('data/shift_swaps.json', 'Shift Swaps'),
        ('current_week.txt', 'Current Week'),
        ('output_schedule.xlsx', 'Excel Schedule'),
        ('output_schedule.csv', 'CSV Schedule')
    ]
    
    print("\nLocal Data Files:")
    print("-" * 30)
    
    total_files = 0
    existing_files = 0
    
    for file_path, description in files_to_check:
        total_files += 1
        if os.path.exists(file_path):
            existing_files += 1
            size = os.path.getsize(file_path)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"[OK] {description}")
            print(f"   File: {file_path}")
            print(f"   Size: {size} bytes")
            print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show content preview for small JSON files
            if file_path.endswith('.json') and size < 5000:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        print(f"   Records: {len(data)}")
                    elif isinstance(data, dict):
                        print(f"   Keys: {len(data)}")
                except:
                    pass
            print()
        else:
            print(f"[MISSING] {description}")
            print(f"   File: {file_path} (NOT FOUND)")
            print()
    
    print(f"Summary: {existing_files}/{total_files} files found")
    
    # Check current week
    if os.path.exists('current_week.txt'):
        with open('current_week.txt', 'r') as f:
            current_week = f.read().strip()
        print(f"Current Week: {current_week}")
    
    # S3 backup status
    print("\nS3 Backup Status:")
    print("-" * 20)
    if os.path.exists('s3_backup.py'):
        print("[OK] S3 backup script available")
        print("To backup to S3:")
        print("   1. Configure AWS credentials in s3_backup.py")
        print("   2. Run: python s3_backup.py")
        print("   3. Check with: python check_s3_data.py")
    else:
        print("[MISSING] S3 backup script not found")

if __name__ == "__main__":
    show_data_status()