# S3 Database Backup Setup

## Prerequisites
1. **AWS Account** with S3 access
2. **AWS Credentials** (Access Key ID and Secret Access Key)
3. **S3 Bucket** created in your AWS account

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements_s3.txt
```

### 2. Configure AWS Credentials
Edit `s3_backup.py` and replace:
- `YOUR_ACCESS_KEY_ID` with your AWS Access Key ID
- `YOUR_SECRET_ACCESS_KEY` with your AWS Secret Access Key
- `nurse-scheduler-backup` with your S3 bucket name
- `us-east-1` with your preferred AWS region

### 3. Create S3 Bucket
- Go to AWS S3 Console
- Create a new bucket named `nurse-scheduler-backup` (or your preferred name)
- Set appropriate permissions

### 4. Run Backup
```bash
python s3_backup.py
```

## What Gets Backed Up
- Nurse database (JSON)
- Hospital configuration
- COVID dataset (CSV)
- Attendance records
- Emergency calls
- MC requests
- Shift swap requests
- Current week tracker
- Generated schedules (Excel & CSV)

## Backup Structure
Files are uploaded to: `s3://your-bucket/backup_YYYYMMDD_HHMMSS/`

## Security Notes
- Keep AWS credentials secure
- Use IAM roles in production
- Enable S3 bucket encryption
- Set appropriate bucket policies