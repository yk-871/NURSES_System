import boto3
import os
from datetime import datetime

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'nurse-scheduler-backup')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Alternative: Use AWS CLI credentials (recommended)
# Comment out the above and uncomment below to use AWS CLI credentials:
# s3_client = boto3.client('s3')  # Uses AWS CLI credentials automatically

def upload_to_s3():
    """Upload database files to S3"""
    try:
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
            print("❌ AWS credentials not configured in environment variables")
            return
            
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Files to backup
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
                # S3 key with timestamp
                s3_key = f"backup_{timestamp}/{file_path.replace('/', '_')}"
                
                # Upload file
                s3_client.upload_file(file_path, BUCKET_NAME, s3_key)
                print(f"✅ Uploaded: {file_path} -> s3://{BUCKET_NAME}/{s3_key}")
            else:
                print(f"⚠️ File not found: {file_path}")
        
        print(f"\n🎉 Backup completed successfully!")
        print(f"📁 Backup location: s3://{BUCKET_NAME}/backup_{timestamp}/")
        
    except Exception as e:
        print(f"❌ Error uploading to S3: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting S3 backup...")
    upload_to_s3()