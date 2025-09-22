import subprocess
import os

def check_aws_setup():
    """Check AWS CLI and S3 setup"""
    print("AWS Setup Checker")
    print("=" * 30)
    
    # Check AWS CLI
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] AWS CLI installed:", result.stdout.strip())
        else:
            print("[ERROR] AWS CLI not found")
            print("Install: https://aws.amazon.com/cli/")
            return
    except FileNotFoundError:
        print("[ERROR] AWS CLI not installed")
        print("Install from: https://aws.amazon.com/cli/")
        return
    
    # Check AWS credentials
    try:
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] AWS credentials configured")
            print("Account info:", result.stdout.strip())
        else:
            print("[ERROR] AWS credentials not configured")
            print("Run: aws configure")
            print("Error:", result.stderr.strip())
            return
    except Exception as e:
        print(f"[ERROR] Cannot check credentials: {e}")
        return
    
    # Check S3 bucket
    bucket_name = 'nurse-scheduler-backup'
    try:
        result = subprocess.run(['aws', 's3', 'ls', f's3://{bucket_name}'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] S3 bucket '{bucket_name}' exists")
            if result.stdout.strip():
                print("Bucket contents:")
                print(result.stdout)
            else:
                print("Bucket is empty - no backups yet")
        else:
            print(f"[ERROR] S3 bucket '{bucket_name}' not found")
            print("Create bucket with: aws s3 mb s3://nurse-scheduler-backup")
    except Exception as e:
        print(f"[ERROR] Cannot check S3 bucket: {e}")
    
    print("\nNext steps:")
    print("1. If AWS CLI not installed: Install from https://aws.amazon.com/cli/")
    print("2. If credentials not configured: Run 'aws configure'")
    print("3. If bucket doesn't exist: Run 'aws s3 mb s3://nurse-scheduler-backup'")
    print("4. Run backup: python s3_backup.py")

if __name__ == "__main__":
    check_aws_setup()