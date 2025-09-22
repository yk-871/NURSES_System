const API_BASE = '/api';

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showError(message) {
    return `<div class="error">❌ ${message}</div>`;
}

function showSuccess(message) {
    return `<div class="success">✅ ${message}</div>`;
}

async function getMySchedule() {
    const nurseId = document.getElementById('nurseId').value;
    if (!nurseId) {
        document.getElementById('myScheduleResult').innerHTML = showError('Please enter your Nurse ID');
        return;
    }

    showLoading();
    try {
        const response = await fetch(`${API_BASE}/nurse/${nurseId}/schedule`);
        const data = await response.json();
        
        if (response.ok) {
            displayNurseSchedule(data);
        } else {
            document.getElementById('myScheduleResult').innerHTML = showError(data.error);
        }
    } catch (error) {
        document.getElementById('myScheduleResult').innerHTML = showError('Connection failed. Make sure the server is running.');
    }
    hideLoading();
}

function displayNurseSchedule(data) {
    let html = `<div class="schedule-card">
        <h3>📅 ${data.nurse_name}</h3>`;
    
    Object.entries(data.schedule).forEach(([day, status]) => {
        const isOnDuty = status.includes('On Duty');
        html += `<div class="schedule-day">
            <span class="day-label">${day}</span>
            <span class="shift-status ${isOnDuty ? 'on-duty' : 'off-duty'}">${status}</span>
        </div>`;
    });
    
    html += '</div>';
    document.getElementById('myScheduleResult').innerHTML = html;
}

async function generateSchedule() {
    const days = document.getElementById('days').value;
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/schedule`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({days: parseInt(days)})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayFullSchedule(data);
        } else {
            document.getElementById('generateResult').innerHTML = showError(data.error);
        }
    } catch (error) {
        document.getElementById('generateResult').innerHTML = showError('Connection failed. Make sure the server is running.');
    }
    hideLoading();
}

function displayFullSchedule(data) {
    let html = showSuccess(`Schedule generated for ${Object.keys(data.schedule).length} nurses`);
    
    html += '<div class="schedule-card"><h3>📊 Summary</h3>';
    data.summary.forEach(day => {
        html += `<div class="schedule-day">
            <span class="day-label">Day ${day.Day}</span>
            <span>ED: ${day.ED_assigned_total || 0} | GW: ${day.GW_assigned_total || 0} | ICU: ${day.ICU_assigned_total || 0}</span>
        </div>`;
    });
    html += '</div>';
    
    document.getElementById('generateResult').innerHTML = html;
}

async function loadNurses() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/nurses`);
        const data = await response.json();
        
        if (response.ok) {
            displayNurses(data.nurses);
        } else {
            document.getElementById('nursesResult').innerHTML = showError(data.error);
        }
    } catch (error) {
        document.getElementById('nursesResult').innerHTML = showError('Connection failed. Make sure the server is running.');
    }
    hideLoading();
}

function displayNurses(nurses) {
    let html = showSuccess(`Loaded ${nurses.length} nurses`);
    
    nurses.forEach(nurse => {
        html += `<div class="nurse-card">
            <div class="nurse-name">👩‍⚕️ ${nurse.name} (ID: ${nurse.id})</div>
            <div class="nurse-skills">Skills: ${nurse.skills ? nurse.skills.join(', ') : 'None listed'}</div>
        </div>`;
    });
    
    document.getElementById('nursesResult').innerHTML = html;
}