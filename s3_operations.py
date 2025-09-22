import boto3
import os
from datetime import datetime

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'nurse-scheduler-backup')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

def get_s3_client():
    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
        return None
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

def backup_to_s3():
    """Backup all data files to S3"""
    try:
        s3_client = get_s3_client()
        
        files_to_backup = [
            'csv/nurse_database.json',
            'csv/hospital_config.json',
            'dataset/covid_dataset.csv',
            'data/attendance.json',
            'data/emergency_calls.json',
            'data/mc_requests.json',
            'data/shift_swaps.json',
            'current_week.txt',
            'output_schedule.xlsx',
            'output_schedule.csv'
        ]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                s3_key = f"backup_{timestamp}/{file_path.replace('/', '_')}"
                s3_client.upload_file(file_path, BUCKET_NAME, s3_key)
        
        return True, f"backup_{timestamp}"
    except Exception as e:
        return False, str(e)

def restore_from_s3():
    """Restore latest backup from S3"""
    try:
        s3_client = get_s3_client()
        
        # Get all backup folders
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' not in response:
            return False, "No backups found"
        
        # Find latest backup
        latest_backup = None
        for obj in response['Contents']:
            key = obj['Key']
            if key.startswith('backup_'):
                timestamp = key.split('/')[0].replace('backup_', '')
                if not latest_backup or timestamp > latest_backup:
                    latest_backup = timestamp
        
        if not latest_backup:
            return False, "No backup folders found"
        
        # Download files from latest backup
        objects = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f'backup_{latest_backup}/')
        
        for obj in objects['Contents']:
            key = obj['Key']
            filename = key.split('/')[-1]
            
            # Map back to original paths
            if filename.startswith('csv_'):
                local_path = f"csv/{filename[4:]}"
            elif filename.startswith('data_'):
                local_path = f"data/{filename[5:]}"
            elif filename.startswith('dataset_'):
                local_path = f"dataset/{filename[8:]}"
            else:
                local_path = filename
            
            # Skip empty filenames
            if not local_path or local_path == '':
                continue
                
            # Create directories if needed
            dir_path = os.path.dirname(local_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            # Download file
            s3_client.download_file(BUCKET_NAME, key, local_path)
        
        return True, f"Restored from backup_{latest_backup}"
    except Exception as e:
        return False, str(e)