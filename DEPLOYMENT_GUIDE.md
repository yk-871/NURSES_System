# 📱 Nurse Scheduler Mobile App Deployment Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
python mobile_api.py
```

### 3. Open Mobile App
Open `mobile_app/index.html` in your browser or serve it locally.

## Mobile App Features

- **My Schedule**: Nurses can view their personal schedule by entering their ID
- **Generate Schedule**: Create new schedules for all nurses
- **All Nurses**: View all registered nurses and their skills

## API Endpoints

- `GET /api/health` - Check server status
- `GET /api/nurses` - Get all nurses
- `POST /api/schedule` - Generate new schedule
- `GET /api/nurse/{id}/schedule` - Get specific nurse schedule

## Mobile Deployment Options

### Option 1: Progressive Web App (PWA)
Add to `mobile_app/index.html` head:
```html
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#2c3e50">
```

### Option 2: Cordova/PhoneGap
```bash
npm install -g cordova
cordova create NurseScheduler
# Copy mobile_app files to www/
cordova platform add android ios
cordova build
```

### Option 3: React Native (Advanced)
Convert HTML/CSS/JS to React Native components for native mobile apps.

## Production Deployment

### Backend (API)
- Deploy Flask app to Heroku, AWS, or similar
- Use production WSGI server (gunicorn)
- Set up proper database instead of JSON files

### Frontend
- Host on GitHub Pages, Netlify, or similar
- Update API_BASE URL in script.js

## Security Notes
- Add authentication for production
- Implement proper error handling
- Use HTTPS in production
- Validate all inputs