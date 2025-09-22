import boto3
from datetime import datetime

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY = 'YOUR_SECRET_ACCESS_KEY'
BUCKET_NAME = 'nurse-scheduler-backup'
AWS_REGION = 'us-east-1'

def list_s3_backups():
    """List all backups in S3 bucket"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        print(f"📁 Checking S3 bucket: {BUCKET_NAME}")
        print("=" * 60)
        
        # List all objects in bucket
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        
        if 'Contents' not in response:
            print("❌ No backups found in S3 bucket")
            return
        
        # Group by backup timestamp
        backups = {}
        for obj in response['Contents']:
            key = obj['Key']
            if key.startswith('backup_'):
                timestamp = key.split('/')[0].replace('backup_', '')
                if timestamp not in backups:
                    backups[timestamp] = []
                backups[timestamp].append({
                    'file': key.split('/')[-1],
                    'size': obj['Size'],
                    'modified': obj['LastModified']
                })
        
        # Display backups
        for timestamp, files in sorted(backups.items(), reverse=True):
            backup_date = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
            print(f"\n🗓️  Backup: {backup_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📂 Folder: backup_{timestamp}/")
            print("-" * 40)
            
            total_size = 0
            for file_info in files:
                size_kb = file_info['size'] / 1024
                total_size += file_info['size']
                print(f"   📄 {file_info['file']} ({size_kb:.1f} KB)")
            
            print(f"   💾 Total size: {total_size/1024:.1f} KB")
        
        print(f"\n✅ Found {len(backups)} backup(s) in S3")
        
    except Exception as e:
        print(f"❌ Error accessing S3: {str(e)}")
        print("\n💡 Make sure to:")
        print("   1. Configure AWS credentials in s3_backup.py")
        print("   2. Create S3 bucket 'nurse-scheduler-backup'")
        print("   3. Run s3_backup.py first to create backups")

def download_latest_backup():
    """Download the latest backup from S3"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Get latest backup
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' not in response:
            print("❌ No backups found")
            return
        
        # Find latest backup folder
        latest_backup = None
        for obj in response['Contents']:
            key = obj['Key']
            if key.startswith('backup_'):
                timestamp = key.split('/')[0].replace('backup_', '')
                if not latest_backup or timestamp > latest_backup:
                    latest_backup = timestamp
        
        if not latest_backup:
            print("❌ No backup folders found")
            return
        
        print(f"📥 Downloading backup: {latest_backup}")
        
        # Download all files from latest backup
        objects = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f'backup_{latest_backup}/')
        
        for obj in objects['Contents']:
            key = obj['Key']
            filename = key.split('/')[-1]
            local_path = f"restored_{filename}"
            
            s3_client.download_file(BUCKET_NAME, key, local_path)
            print(f"✅ Downloaded: {filename}")
        
        print(f"\n🎉 Latest backup downloaded successfully!")
        
    except Exception as e:
        print(f"❌ Error downloading from S3: {str(e)}")

if __name__ == "__main__":
    print("🔍 S3 Backup Checker")
    print("1. List all backups")
    print("2. Download latest backup")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        list_s3_backups()
    elif choice == "2":
        download_latest_backup()
    else:
        print("❌ Invalid choice")