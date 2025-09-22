import boto3
import os
from datetime import datetime

# Use AWS CLI credentials (no hardcoded keys needed)
BUCKET_NAME = 'nurse-scheduler-backup'

def upload_to_s3():
    """Upload database files to S3 using AWS CLI credentials"""
    try:
        # Initialize S3 client using AWS CLI credentials
        s3_client = boto3.client('s3')
        
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
        
        # Check if bucket exists, create if not
        try:
            s3_client.head_bucket(Bucket=BUCKET_NAME)
            print(f"Using existing bucket: {BUCKET_NAME}")
        except:
            print(f"Creating bucket: {BUCKET_NAME}")
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        
        uploaded_count = 0
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                # S3 key with timestamp
                s3_key = f"backup_{timestamp}/{file_path.replace('/', '_')}"
                
                # Upload file
                s3_client.upload_file(file_path, BUCKET_NAME, s3_key)
                print(f"[OK] Uploaded: {file_path}")
                uploaded_count += 1
            else:
                print(f"[SKIP] File not found: {file_path}")
        
        print(f"\nBackup completed successfully!")
        print(f"Files uploaded: {uploaded_count}")
        print(f"S3 location: s3://{BUCKET_NAME}/backup_{timestamp}/")
        print(f"AWS Console: https://s3.console.aws.amazon.com/s3/buckets/{BUCKET_NAME}")
        
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Run: aws configure")
        print("2. Enter your AWS Access Key ID")
        print("3. Enter your AWS Secret Access Key")
        print("4. Enter region (e.g., us-east-1)")
        print("5. Try again")

if __name__ == "__main__":
    print("S3 Backup (using AWS CLI credentials)")
    print("=" * 40)
    upload_to_s3()