# N.U.R.S.E.S.
**Nurse Unified Roster and Scheduling Efficiency System**

A comprehensive AI-powered nurse scheduling and management system with mobile interface, emergency protocols, and cloud backup.

## 🚀 Features

### 📱 Mobile-First Interface
- Instagram-style responsive design
- 5-panel navigation (Home, Chat, Emergency, Schedule, Dashboard)
- Professional login system with role-based access

### 🤖 AI-Powered Scheduling
- OR-Tools optimization engine
- Machine learning demand prediction
- Calendar-based scheduling (Monday-Sunday format)
- Automatic weekly advancement

### 💬 Intelligent Chatbot
- Google Gemini AI integration
- Schedule queries and MC submissions
- Emergency procedures and ward protocols
- Natural language processing

### 🚨 Emergency Management
- Real-time emergency call system
- Ward-specific alerts (ICU, ED, GW)
- Admin notification and resolution tracking

### ☁️ Cloud Integration
- AWS S3 automatic backups
- Data restoration capabilities
- Secure credential management

### 👑 Admin Features
- Schedule generation with file upload
- Full schedule viewing and management
- Emergency call monitoring
- Data reset and backup controls

## 🛠️ Technology Stack

- **Backend**: Python Flask, OR-Tools, Scikit-learn
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI**: Google Gemini API
- **Cloud**: AWS S3
- **Data**: JSON, CSV, Excel support

## 📋 Installation

1. **Clone Repository**
   ```bash
   git clone <your-repo-url>
   cd "Nurse Roaster demo"
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS (Optional)**
   - Update `s3_operations.py` with your AWS credentials
   - Create S3 bucket: `nurse-scheduler-backup`

4. **Run Application**
   ```bash
   python app.py
   ```

5. **Access System**
   - Open: `http://localhost:5000`
   - Admin Login: N1001_Hack, N1015_Hack
   - User Login: N1000_Hack (any nurse ID + _Hack)

## 🏥 System Architecture

### Database Structure
- `csv/nurse_database.json` - 30 nurses with roles and departments
- `data/attendance.json` - Check-in/out records
- `data/emergency_calls.json` - Emergency alerts
- `data/mc_requests.json` - Medical certificate requests
- `data/shift_swaps.json` - Shift exchange requests

### AI Components
- `scheduling_ai.py` - Main scheduling algorithm
- `ML.py` - Machine learning model training
- `dataset/covid_dataset.csv` - Historical admission data

### Mobile Interface
- `mobile_app/main.html` - Main application interface
- `mobile_app/login.html` - Authentication page
- `mobile_app/instagram-style.css` - Responsive styling
- `mobile_app/instagram-app.js` - Frontend logic

## 🔐 Security Features

- Password-based authentication (ID_Hack format)
- Role-based access control (Admin/User)
- Session management
- Secure API endpoints

## 📊 Admin Capabilities

- **Schedule Generation**: Upload CSV/Excel → AI optimization → Auto-backup
- **Emergency Management**: View active calls → Resolve incidents
- **Data Management**: S3 backup/restore → Reset system data
- **Full Visibility**: Complete schedule overview → Attendance reports

## 🌐 Deployment Options

- **Local**: Direct Python execution
- **Cloud**: AWS ECS, Railway, Heroku, DigitalOcean
- **Container**: Docker support included

## 📞 Support

- **Admin Users**: N1001 (Arun Raj), N1015 (Nur Syuhada)
- **System**: 30 nurses across ICU, ED, GW departments
- **Emergency**: Built-in emergency protocols and contacts

## 📈 Future Enhancements

- Real-time notifications
- Mobile app (React Native)
- Advanced analytics dashboard
- Integration with hospital systems
- Multi-language support

---

**N.U.R.S.E.S.** - Streamlining healthcare workforce management with AI-powered efficiency.