# Cloud Deployment Guide - Nurse Scheduling System

## Quick Deploy Options

### Option 1: AWS ECS (Recommended)
**Cost**: ~$15-30/month for small usage

1. **Prerequisites**:
   ```bash
   # Install AWS CLI
   aws configure
   # Install Docker Desktop
   ```

2. **Deploy**:
   ```bash
   cd deploy
   chmod +x deploy.sh
   ./deploy.sh
   ```

### Option 2: Railway (Easiest)
**Cost**: Free tier available, ~$5/month for production

1. **Setup**:
   - Go to [railway.app](https://railway.app)
   - Connect GitHub repository
   - Deploy automatically

2. **Environment Variables**:
   ```
   PORT=5000
   FLASK_ENV=production
   ```

### Option 3: Heroku
**Cost**: ~$7/month

1. **Setup**:
   ```bash
   # Install Heroku CLI
   heroku create nurse-scheduler-app
   git push heroku main
   ```

2. **Add Procfile**:
   ```
   web: gunicorn app:app
   ```

### Option 4: DigitalOcean App Platform
**Cost**: ~$12/month

1. **Setup**:
   - Go to DigitalOcean App Platform
   - Connect GitHub repository
   - Configure build settings

## Files Created for Deployment

- `Dockerfile` - Container configuration
- `docker-compose.yml` - Local testing
- `aws-deploy.yml` - AWS CloudFormation template
- `deploy.sh` - Automated AWS deployment script
- `requirements.txt` - Python dependencies

## Environment Variables Needed

```
PORT=5000
FLASK_ENV=production
AWS_DEFAULT_REGION=us-east-1
```

## Post-Deployment Steps

1. **Upload nurse database**: Copy `csv/nurse_database.json` to production
2. **Generate initial schedule**: Use admin account to upload admission data
3. **Test all features**: Login, emergency calls, schedule generation
4. **Setup S3 backup**: Configure AWS credentials for database backup

## Security Notes

- Change default admin passwords
- Use HTTPS in production
- Secure API keys and credentials
- Regular database backups

## Monitoring

- Check application logs regularly
- Monitor resource usage
- Set up alerts for downtime
- Regular health checks

Choose the deployment option that best fits your budget and technical requirements.