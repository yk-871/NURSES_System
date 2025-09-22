@echo off
echo 🏥 Starting Nurse Attendance App...
echo.
echo Installing dependencies...
pip install flask flask-cors pandas joblib openpyxl ortools
echo.
echo 👑 Admin IDs: admin, 1001
echo 📱 Open http://localhost:5000 in your browser
echo.
echo Starting server...
python app.py
pause