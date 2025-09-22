const API_BASE = '/api';
let currentUser = null;

// Panel Navigation
function showPanel(panelName) {
    // Hide all panels
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Remove active from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected panel
    document.getElementById(panelName).classList.add('active');
    
    // Add active to clicked nav button
    event.target.closest('.nav-btn').classList.add('active');
    
    // Load panel-specific data
    loadPanelData(panelName);
}

function loadPanelData(panelName) {
    switch(panelName) {
        case 'home':
            loadStatus();
            break;
        case 'schedule':
            loadMySchedule();
            break;
        case 'emergency':
            loadEmergencyStatus();
            break;
        case 'dashboard':
            loadDashboardStats();
            break;
    }
}

// Utility Functions
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

// Authentication & Status
async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data;
            
            document.getElementById('nurseName').textContent = data.nurse_name;
            
            if (data.is_admin) {
                document.getElementById('adminPanel').classList.remove('hidden');
            }
            
            updateStatusDisplay(data);
        } else {
            window.location.href = 'login.html';
        }
    } catch (error) {
        document.getElementById('currentStatus').innerHTML = showError('Connection failed');
    }
}

function updateStatusDisplay(data) {
    const status = data.status;
    const today = data.today;
    const todaySchedule = data.today_schedule || 'No schedule available';
    const currentWeekSchedule = data.current_week_schedule || 'No schedule available';
    let statusHtml = '';

    if (status === 'checked_in') {
        statusHtml = `<div class="status-active">✅ Checked In at ${today.checkin}</div>`;
        document.getElementById('checkinBtn').disabled = true;
        document.getElementById('checkoutBtn').disabled = false;
    } else if (status === 'checked_out') {
        statusHtml = `
            <div class="status-complete">
                ✅ Checked In: ${today.checkin}<br>
                🏃 Checked Out: ${today.checkout}<br>
                ⏱️ Hours: ${today.hours_worked}h
            </div>
        `;
        document.getElementById('checkinBtn').disabled = true;
        document.getElementById('checkoutBtn').disabled = true;
    } else {
        statusHtml = `<div class="status-pending">⏳ Not checked in today</div>`;
        document.getElementById('checkinBtn').disabled = false;
        document.getElementById('checkoutBtn').disabled = true;
    }

    document.getElementById('currentStatus').innerHTML = statusHtml;
    

    
    // Store current week schedule for dashboard
    if (currentUser) {
        currentUser.current_week_schedule = currentWeekSchedule;
    }
}

// Check-in/Check-out
async function checkin() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/checkin`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadStatus();
            showNotification('✅ Checked in successfully!');
        } else {
            showNotification('❌ ' + data.error);
        }
    } catch (error) {
        showNotification('❌ Connection failed');
    }
    hideLoading();
}

async function checkout() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/checkout`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadStatus();
            showNotification(`✅ Checked out! Hours: ${data.hours_worked}h`);
        } else {
            showNotification('❌ ' + data.error);
        }
    } catch (error) {
        showNotification('❌ Connection failed');
    }
    hideLoading();
}

// Chatbot
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addChatMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator
    addChatMessage('🤖 Typing...', 'bot', true);
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({message: message})
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        const messages = document.getElementById('chatMessages');
        const lastMessage = messages.lastElementChild;
        if (lastMessage && lastMessage.textContent.includes('Typing...')) {
            lastMessage.remove();
        }
        
        if (response.ok) {
            addChatMessage(data.response, 'bot');
        } else {
            addChatMessage('Sorry, I\'m having trouble right now. Please try again.', 'bot');
        }
    } catch (error) {
        // Remove typing indicator
        const messages = document.getElementById('chatMessages');
        const lastMessage = messages.lastElementChild;
        if (lastMessage && lastMessage.textContent.includes('Typing...')) {
            lastMessage.remove();
        }
        
        addChatMessage('Connection error. Please check your internet connection.', 'bot');
    }
}

function addChatMessage(message, sender, isTemporary = false) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'user' ? 'user-message' : 'bot-message';
    if (isTemporary) messageDiv.classList.add('temporary');
    messageDiv.innerHTML = message;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Removed - now using AI chatbot API

// QR Scanner
function simulateQRScan() {
    showLoading();
    
    setTimeout(() => {
        hideLoading();
        
        // Simulate successful QR scan
        const isCheckedIn = !document.getElementById('checkinBtn').disabled;
        
        if (isCheckedIn) {
            checkin();
        } else {
            checkout();
        }
        
        document.getElementById('scanResult').innerHTML = showSuccess('QR Code scanned successfully!');
    }, 2000);
}

function toggleFlashlight() {
    const btn = event.target;
    if (btn.textContent.includes('💡')) {
        btn.textContent = '🔦 Flash On';
        btn.style.background = '#ffd600';
    } else {
        btn.textContent = '💡 Toggle Flash';
        btn.style.background = '#ffd600';
    }
}

// Schedule
async function loadMySchedule() {
    if (!currentUser) return;
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({message: 'my schedule'})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (data.response.includes('No schedule found')) {
                document.getElementById('fullSchedule').innerHTML = `
                    <div class="pending-state">
                        <div class="pending-icon">⏳</div>
                        <h4>Schedule Pending</h4>
                        <p>No schedule data available yet. Please contact admin to generate schedules.</p>
                    </div>
                `;
            } else {
                const scheduleText = data.response;
                const prettySchedule = formatPrettySchedule(scheduleText);
                document.getElementById('fullSchedule').innerHTML = prettySchedule;
            }
        } else {
            document.getElementById('fullSchedule').innerHTML = `
                <div class="pending-state">
                    <div class="pending-icon">❌</div>
                    <h4>Error Loading Schedule</h4>
                    <p>Failed to load schedule. Please try again later.</p>
                </div>
            `;
        }
    } catch (error) {
        document.getElementById('fullSchedule').innerHTML = `
            <div class="pending-state">
                <div class="pending-icon">❌</div>
                <h4>Connection Error</h4>
                <p>Unable to connect to server. Please check your connection.</p>
            </div>
        `;
    }
    hideLoading();
}

function formatPrettySchedule(scheduleText) {
    const lines = scheduleText.split('\n');
    let html = '<div class="my-schedule-list">';
    
    const headerLine = lines[0];
    if (headerLine.includes('Schedule for')) {
        const nameMatch = headerLine.match(/Schedule for (.+) \(ID: (.+)\)/);
        if (nameMatch) {
            const nurseName = nameMatch[1];
            const nurseId = nameMatch[2];
            html += `<h4>📅 My Schedule</h4>`;
            html += `
                <div class="my-schedule-item">
                    <div class="my-schedule-header">
                        <strong class="my-nurse-name">${nurseName}</strong>
                        <span class="my-nurse-badge">${nurseId}</span>
                    </div>
                    <div class="my-schedule-details">
            `;
        }
    }
    
    // Group shifts by day
    const dayShifts = {};
    for (let i = 2; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.includes(':')) {
            // Handle format: "Monday 2024-01-15 Morning: On Duty - GW"
            const dayMatch = line.match(/(\w+)\s+(\d{4}-\d{2}-\d{2})\s+(\w+):\s*(.+)/);
            if (dayMatch) {
                const dayName = dayMatch[1];
                const date = dayMatch[2];
                const shift = dayMatch[3];
                const assignment = dayMatch[4];
                
                const dayKey = `${dayName} ${date}`;
                if (!dayShifts[dayKey]) {
                    dayShifts[dayKey] = [];
                }
                if (assignment !== 'Off') {
                    dayShifts[dayKey].push(`${shift}: ${assignment.replace('On Duty - ', '')}`);
                }
            } else {
                // Fallback for other formats
                const simpleMatch = line.match(/(.+?):\s*(.+)/);
                if (simpleMatch) {
                    const dayInfo = simpleMatch[1];
                    const assignment = simpleMatch[2];
                    if (assignment !== 'Off') {
                        html += `<div class="my-schedule-day"><strong>${dayInfo}:</strong> ${assignment}</div>`;
                    }
                }
            }
        }
    }
    
    // Display grouped shifts in chronological order with week separation
    const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const sortedDays = Object.keys(dayShifts).sort((a, b) => {
        const dayA = dayOrder.indexOf(a.split(' ')[0]);
        const dayB = dayOrder.indexOf(b.split(' ')[0]);
        return dayA - dayB;
    });
    
    // Separate current week and next week
    const today = new Date();
    // Get Monday of current week
    const currentWeekStart = new Date(today);
    const dayOfWeek = today.getDay(); // 0=Sunday, 1=Monday, ..., 6=Saturday
    const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    currentWeekStart.setDate(today.getDate() + daysToMonday);
    
    const nextWeekStart = new Date(currentWeekStart);
    nextWeekStart.setDate(currentWeekStart.getDate() + 7);
    
    const currentWeekDays = [];
    const nextWeekDays = [];
    
    sortedDays.forEach(dayInfo => {
        const dateMatch = dayInfo.match(/\d{4}-\d{2}-\d{2}/);
        if (dateMatch) {
            const dayDate = new Date(dateMatch[0]);
            const currentWeekEnd = new Date(nextWeekStart);
            currentWeekEnd.setDate(nextWeekStart.getDate() - 1);
            
            if (dayDate >= currentWeekStart && dayDate < nextWeekStart) {
                currentWeekDays.push(dayInfo);
            } else if (dayDate >= nextWeekStart) {
                nextWeekDays.push(dayInfo);
            }
        }
    });
    
    // Show only next week schedule
    for (const dayInfo of sortedDays) {
        const shifts = dayShifts[dayInfo];
        const shiftsText = shifts.length > 0 ? shifts.join(', ') : 'Off';
        html += `<div class="my-schedule-day"><strong>${dayInfo}:</strong> ${shiftsText}</div>`;
    }
    
    html += '</div></div></div>';
    return html;
}

function getMyShiftClass(shift) {
    if (shift.includes('ED')) return 'my-shift my-shift-ed';
    if (shift.includes('ICU')) return 'my-shift my-shift-icu';
    if (shift.includes('GW')) return 'my-shift my-shift-gw';
    return 'my-shift';
}

function getShiftIcon(shift) {
    if (shift.includes('Morning')) return '🌅';
    if (shift.includes('Evening')) return '🌆';
    if (shift.includes('Night')) return '🌙';
    return '⏰';
}

// Attendance
async function loadMyAttendance() {
    if (!currentUser) return;
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/status`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            displayAttendanceHistory(data);
        } else {
            document.getElementById('attendanceHistory').innerHTML = `
                <div class="pending-state">
                    <div class="pending-icon">❌</div>
                    <h4>Error Loading Attendance</h4>
                    <p>Failed to load attendance records.</p>
                </div>
            `;
        }
    } catch (error) {
        document.getElementById('attendanceHistory').innerHTML = `
            <div class="pending-state">
                <div class="pending-icon">❌</div>
                <h4>Connection Error</h4>
                <p>Unable to load attendance data.</p>
            </div>
        `;
    }
    hideLoading();
}

function displayAttendanceHistory(data) {
    const today = data.today;
    let html = '';
    
    if (Object.keys(today).length === 0) {
        html = `
            <div class="pending-state">
                <div class="pending-icon">📋</div>
                <h4>No Attendance Records</h4>
                <p>No attendance data found. Start by checking in today!</p>
            </div>
        `;
    } else {
        const status = data.status;
        const isComplete = status === 'checked_out';
        
        html = `
            <div class="attendance-record ${isComplete ? '' : 'incomplete'}">
                <div class="attendance-date">Today - ${new Date().toLocaleDateString()}</div>
                <div class="attendance-times">
                    <span>Check-in: ${today.checkin || 'Not checked in'}</span>
                    <span>Check-out: ${today.checkout || 'Not checked out'}</span>
                </div>
                ${today.hours_worked ? `<div class="attendance-hours">Hours: ${today.hours_worked}h</div>` : ''}
            </div>
        `;
    }
    
    document.getElementById('attendanceHistory').innerHTML = html;
}

// Dashboard
function loadDashboardStats() {
    // Mock statistics
    document.getElementById('weekHours').textContent = '32h';
    document.getElementById('monthShifts').textContent = '18';
    document.getElementById('attendance').textContent = '95%';
}

async function generateSchedule() {
    // Show file upload form
    const uploadForm = `
        <div class="upload-form">
            <h4>📊 Upload Admission Data</h4>
            <form id="uploadForm">
                <div class="form-group">
                    <label>Upload CSV/Excel File:</label>
                    <input type="file" id="admissionFile" accept=".csv,.xlsx,.xls" required>
                    <small>Upload a CSV or Excel file with admission data</small>
                </div>
                <div class="form-buttons">
                    <button type="button" onclick="submitFileUpload()" class="submit-btn">Generate Schedule</button>
                    <button type="button" onclick="cancelScheduleGeneration()" class="cancel-btn">Cancel</button>
                </div>
            </form>
        </div>
    `;
    
    document.getElementById('adminResults').innerHTML = uploadForm;
}

async function restoreFromS3() {
    if (!confirm('This will restore all data from the latest S3 backup. Continue?')) {
        return;
    }
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/s3/restore`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('adminResults').innerHTML = showSuccess(data.message);
            showNotification('✅ Data restored from S3!');
            // Reload page to reflect restored data
            setTimeout(() => window.location.reload(), 2000);
        } else {
            document.getElementById('adminResults').innerHTML = showError(data.error);
        }
    } catch (error) {
        document.getElementById('adminResults').innerHTML = showError('Connection failed');
    }
    hideLoading();
}

async function backupToS3() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/s3/backup`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('adminResults').innerHTML = showSuccess(data.message);
            showNotification('✅ Manual backup completed!');
        } else {
            document.getElementById('adminResults').innerHTML = showError(data.error);
        }
    } catch (error) {
        document.getElementById('adminResults').innerHTML = showError('Connection failed');
    }
    hideLoading();
}

async function submitFileUpload() {
    const fileInput = document.getElementById('admissionFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('❌ Please select a file');
        return;
    }
    
    showLoading();
    try {
        const formData = new FormData();
        formData.append('admission_file', file);
        
        const response = await fetch(`${API_BASE}/schedule/upload`, {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const message = data.message || 'AI-optimized schedule generated successfully!';
            document.getElementById('scheduleResults').innerHTML = showSuccess(message);
            showNotification('✅ Schedule generated and backed up!');
        } else {
            document.getElementById('scheduleResults').innerHTML = showError(data.error);
        }
    } catch (error) {
        document.getElementById('adminResults').innerHTML = showError('Connection failed');
    }
    hideLoading();
}

function cancelScheduleGeneration() {
    document.getElementById('adminResults').innerHTML = '';
}

async function viewFullSchedule() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/schedule/full`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayFullScheduleTable(data.schedule);
        } else {
            document.getElementById('adminResults').innerHTML = showError(data.error);
        }
    } catch (error) {
        document.getElementById('adminResults').innerHTML = showError('Connection failed');
    }
    hideLoading();
}

function displayFullScheduleTable(scheduleData) {
    if (!scheduleData || scheduleData.length === 0) {
        document.getElementById('adminResults').innerHTML = showError('No schedule data available');
        return;
    }
    
    let html = `<div class="schedule-list"><h4>📅 Full Schedule (${scheduleData.length} nurses)</h4>`;
    
    scheduleData.forEach(nurse => {
        const nurseName = nurse.Name || 'Unknown';
        const nurseId = nurse.Nurse_ID || 'N/A';
        
        html += `
            <div class="schedule-item">
                <div class="schedule-header">
                    <strong class="nurse-name">${nurseName}</strong>
                    <span class="nurse-badge">${nurseId}</span>
                </div>
                <div class="schedule-details">
        `;
        
        // Group shifts by day and date
        const dayShifts = {};
        Object.keys(nurse).forEach(col => {
            // Skip non-schedule columns
            if (col === 'Nurse_ID' || col === 'Name') return;
            
            const dayMatch = col.match(/(\w+)\s+(\d{4}-\d{2}-\d{2})\s+(\w+)/);
            if (dayMatch) {
                const dayName = dayMatch[1];
                const date = dayMatch[2];
                const shift = dayMatch[3];
                const value = nurse[col];
                
                const dayKey = `${dayName} ${date}`;
                if (!dayShifts[dayKey]) {
                    dayShifts[dayKey] = [];
                }
                
                if (value && value !== 'Off') {
                    let shiftCode = '';
                    if (shift === 'Morning') shiftCode = 'M';
                    else if (shift === 'Evening') shiftCode = 'E';
                    else if (shift === 'Night') shiftCode = 'N';
                    dayShifts[dayKey].push(`${shiftCode}: ${value.replace('On Duty - ', '')}`);
                }
            }
        });
        
            // Display grouped shifts in chronological order
        const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        const sortedDays = Object.keys(dayShifts).sort((a, b) => {
            const dayA = dayOrder.indexOf(a.split(' ')[0]);
            const dayB = dayOrder.indexOf(b.split(' ')[0]);
            return dayA - dayB;
        });
        
        if (sortedDays.length === 0) {
            html += `<div class="schedule-day"><strong>No schedule data available</strong></div>`;
        } else {
            // Separate current week and next week
            const today = new Date();
            // Get Monday of current week
            const currentWeekStart = new Date(today);
            const dayOfWeek = today.getDay(); // 0=Sunday, 1=Monday, ..., 6=Saturday
            const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
            currentWeekStart.setDate(today.getDate() + daysToMonday);
            
            const nextWeekStart = new Date(currentWeekStart);
            nextWeekStart.setDate(currentWeekStart.getDate() + 7);
            
            const currentWeekDays = [];
            const nextWeekDays = [];
            
            sortedDays.forEach(dayKey => {
                const dateMatch = dayKey.match(/\d{4}-\d{2}-\d{2}/);
                if (dateMatch) {
                    const dayDate = new Date(dateMatch[0]);
                    const currentWeekEnd = new Date(nextWeekStart);
                    currentWeekEnd.setDate(nextWeekStart.getDate() - 1);
                    
                    if (dayDate >= currentWeekStart && dayDate < nextWeekStart) {
                        currentWeekDays.push(dayKey);
                    } else if (dayDate >= nextWeekStart) {
                        nextWeekDays.push(dayKey);
                    }
                }
            });
            
            // Show only next week schedule
            sortedDays.forEach(dayKey => {
                const shifts = dayShifts[dayKey];
                const shiftsText = shifts.length > 0 ? shifts.join(', ') : 'Off';
                html += `<div class="schedule-day"><strong>${dayKey}:</strong> ${shiftsText}</div>`;
            });
        }
        
        html += `
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    document.getElementById('adminResults').innerHTML = html;
}

async function viewEmergencyCalls() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/emergency/list`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (data.count === 0) {
                document.getElementById('adminResults').innerHTML = `
                    <div class="success">✅ No active emergency calls</div>
                `;
            } else {
                let html = `<div class="emergency-calls-list"><h4>🚨 Active Emergency Calls (${data.count})</h4>`;
                data.emergency_calls.forEach(call => {
                    const time = new Date(call.timestamp).toLocaleString();
                    const ward = call.ward || 'Unknown';
                    const role = call.role || 'Nurse';
                    html += `
                        <div class="emergency-call-item">
                            <div class="emergency-header">
                                <strong class="emergency-type">${call.emergency_type.toUpperCase()}</strong>
                                <span class="emergency-ward">${ward} Ward</span>
                            </div>
                            <div class="emergency-nurse">
                                👩‍⚕️ ${call.nurse_name} (${call.nurse_id}) - ${role}
                            </div>
                            <div class="emergency-details">
                                <small>📍 ${call.location} | ⏰ ${time}</small>
                            </div>
                            <div class="emergency-message">
                                <em>${call.message}</em>
                            </div>
                            <div class="emergency-actions">
                                <button onclick="solveEmergencyCall('${call.id}')" class="solve-btn">✅ Solved</button>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                document.getElementById('adminResults').innerHTML = html;
            }
        } else {
            document.getElementById('adminResults').innerHTML = showError(data.error);
        }
    } catch (error) {
        document.getElementById('adminResults').innerHTML = showError('Connection failed');
    }
    hideLoading();
}

async function logout() {
    try {
        await fetch(`${API_BASE}/logout`, {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.log('Logout error:', error);
    }
    
    window.location.href = 'login.html';
}

// Notifications
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: #262626;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 1000;
        font-size: 14px;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Chat input enter key
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Load initial data
    loadStatus();
});

// MC Submission
async function submitMC() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const reason = document.getElementById('reason').value;
    const documentation = document.getElementById('documentation').value;
    
    if (!startDate || !endDate || !reason || !documentation) {
        showNotification('❌ Please fill in all fields');
        return;
    }
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/mc/submit`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({
                start_date: startDate,
                end_date: endDate,
                reason: reason,
                documentation: documentation
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addChatMessage('✅ MC request submitted successfully! Request ID: ' + data.request_id, 'bot');
            document.getElementById('mcForm').reset();
        } else {
            addChatMessage('❌ Error: ' + data.error, 'bot');
        }
    } catch (error) {
        addChatMessage('❌ Connection error. Please try again.', 'bot');
    }
    hideLoading();
}

// Emergency Call Functions
async function sendEmergencyCall(type) {
    if (!currentUser) return;
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/emergency/call`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({
                emergency_type: type,
                location: 'Ward', // Could be enhanced to get actual location
                message: `${type.toUpperCase()} emergency called by ${currentUser.nurse_name}`
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('emergencyStatus').innerHTML = `
                <div class="success">
                    ✅ Emergency call sent successfully!<br>
                    Call ID: ${data.call_id}<br>
                    Admin has been notified.
                </div>
            `;
            showNotification('🚨 Emergency call sent to admin!');
        } else {
            document.getElementById('emergencyStatus').innerHTML = `
                <div class="error">❌ Failed to send emergency call: ${data.error}</div>
            `;
        }
    } catch (error) {
        document.getElementById('emergencyStatus').innerHTML = `
            <div class="error">❌ Connection error. Please try again.</div>
        `;
    }
    hideLoading();
}

function loadEmergencyStatus() {
    document.getElementById('emergencyStatus').innerHTML = `
        <div class="emergency-info">
            <h4>Emergency Contacts:</h4>
            <p>• Medical: Call 2222</p>
            <p>• Security: Call 4444</p>
            <p>• Fire: Call 3333</p>
            <p>• Admin will be notified of all emergency calls</p>
        </div>
    `;
}

// Shift Swap Submission
async function submitSwapRequest() {
    const currentShift = document.getElementById('currentShift').value;
    const desiredShift = document.getElementById('desiredShift').value;
    const reason = document.getElementById('swapReason').value;
    
    if (!currentShift || !desiredShift || !reason) {
        showNotification('❌ Please fill in all fields');
        return;
    }
    
    if (currentShift === desiredShift) {
        showNotification('❌ Current and desired shifts cannot be the same');
        return;
    }
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/swap/submit`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({
                current_shift: currentShift,
                desired_shift: desiredShift,
                reason: reason
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addChatMessage('✅ Shift swap request submitted successfully! Request ID: ' + data.request_id, 'bot');
            document.getElementById('swapForm').reset();
        } else {
            addChatMessage('❌ Error: ' + data.error, 'bot');
        }
    } catch (error) {
        addChatMessage('❌ Connection error. Please try again.', 'bot');
    }
    hideLoading();
}

// Solve Emergency Call
async function solveEmergencyCall(callId) {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/emergency/solve`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({call_id: callId})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('✅ Emergency call marked as solved');
            viewEmergencyCalls(); // Refresh the list
        } else {
            showNotification('❌ ' + data.error);
        }
    } catch (error) {
        showNotification('❌ Connection failed');
    }
    hideLoading();
}

async function generateSchedule() {
    document.getElementById('uploadSection').classList.remove('hidden');
    document.getElementById('adminResults').innerHTML = '';
    document.getElementById('scheduleResults').innerHTML = '';
}

function cancelScheduleGeneration() {
    document.getElementById('uploadSection').classList.add('hidden');
    document.getElementById('admissionFile').value = '';
    document.getElementById('scheduleResults').innerHTML = '';
}

async function resetData() {
    if (!confirm('This will clear all attendance records and emergency calls. Continue?')) {
        return;
    }
    
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/admin/reset`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('adminResults').innerHTML = showSuccess(data.message);
            showNotification('✅ Data reset completed!');
            // Reload page to reflect reset data
            setTimeout(() => window.location.reload(), 2000);
        } else {
            document.getElementById('adminResults').innerHTML = showError(data.error);
        }
    } catch (error) {
        document.getElementById('adminResults').innerHTML = showError('Connection failed');
    }
    hideLoading();
}

// Initialize app
window.onload = function() {
    loadStatus();
};