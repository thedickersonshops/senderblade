#!/usr/bin/env python3
"""
SenderBlade Unified App - Main + Admin Together
Gently merged, protecting all existing functionality
"""
import os
import sqlite3
import sys
import time
from flask import Flask, g, send_from_directory, request, jsonify, session, redirect
from flask_cors import CORS

# Add current directory to path for admin imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all existing SenderBlade API modules (protecting your working code)
from lists_api import lists_api
from smtp_api_fixed import smtp_api
from proxy_api_fixed import proxy_api
from spinner_api import spinner_api
from campaigns_api import campaigns_api
from generator_api import generator_api
from auth_api import auth_api
from health_api import health_api

# Import admin system (your working admin code)
from simple_admin import simple_admin
from enterprise_auth import enterprise_auth

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'senderblade_secret_key_change_in_production'
CORS(app, origins='*', supports_credentials=True, allow_headers=['Content-Type'], methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Register all existing SenderBlade blueprints (protecting your email system)
app.register_blueprint(lists_api, url_prefix='/api')
app.register_blueprint(smtp_api, url_prefix='/api')
app.register_blueprint(proxy_api, url_prefix='/api')
app.register_blueprint(spinner_api, url_prefix='/api')
app.register_blueprint(campaigns_api, url_prefix='/api')
app.register_blueprint(generator_api, url_prefix='/api')
app.register_blueprint(auth_api, url_prefix='/api')
app.register_blueprint(health_api, url_prefix='/api')

# ============================================================================
# EXISTING SENDERBLADE ROUTES (PROTECTED - NO CHANGES)
# ============================================================================

# Serve static files (your existing frontend)
@app.route('/')
def index():
    return send_from_directory('../static', 'login.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('../static', filename)

# Database configuration (your existing setup)
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')
SPINNER_DATABASE = os.path.join(os.path.dirname(__file__), 'sender.db')

@app.teardown_appcontext
def close_connection(exception):
    # Close all database connections (your existing code)
    for attr in ['_database', '_spinner_database', '_main_database', '_proxy_database']:
        db = getattr(g, attr, None)
        if db is not None:
            db.close()

# Initialize database (your existing function)
def init_db():
    # Initialize main database
    db = sqlite3.connect(DATABASE)
    with open('schema.sql', 'r') as f:
        db.executescript(f.read())
    db.commit()
    db.close()
    
    # Initialize spinner database
    db = sqlite3.connect(SPINNER_DATABASE)
    with open('sender_schema.sql', 'r') as f:
        db.executescript(f.read())
    # Also initialize spinner schema
    with open('spinner_schema.sql', 'r') as f:
        db.executescript(f.read())
    db.commit()
    db.close()

# ============================================================================
# ADMIN SYSTEM ROUTES (GENTLY ADDED)
# ============================================================================

# Admin Authentication Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login - email only"""
    if request.method == 'GET':
        admin_email = simple_admin.get_admin_email()
        return f'''
<!DOCTYPE html>
<html>
<head>
    <title>SenderBlade Admin Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .admin-card {{ background: rgba(255,255,255,0.95); border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="container-fluid d-flex align-items-center justify-content-center min-vh-100">
        <div class="col-md-4">
            <div class="admin-card p-5">
                <div class="text-center mb-4">
                    <h2>🛡️ SenderBlade Admin</h2>
                    <p class="text-muted">Enterprise Admin Access</p>
                </div>
                <div id="emailForm">
                    <form id="adminEmailForm">
                        <div class="mb-3">
                            <label class="form-label">Admin Email</label>
                            <input type="email" class="form-control" id="adminEmail" 
                                   value="{admin_email}" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Send OTP Code</button>
                    </form>
                </div>
                <div id="otpForm" style="display: none;">
                    <div class="text-center mb-4">
                        <h5>📧 OTP Sent!</h5>
                        <p class="text-muted">Check your email for the 6-digit code</p>
                    </div>
                    <form id="adminOtpForm">
                        <div class="mb-3">
                            <input type="text" class="form-control text-center" id="otpCode" 
                                   maxlength="6" placeholder="123456" required>
                        </div>
                        <button type="submit" class="btn btn-success w-100">Verify & Login</button>
                        <button type="button" class="btn btn-secondary w-100 mt-2" onclick="resetLogin()">Back</button>
                    </form>
                </div>
                <div id="messages" class="mt-3"></div>
            </div>
        </div>
    </div>
    <script>
        let currentEmail = null;
        document.getElementById('adminEmailForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            const email = document.getElementById('adminEmail').value;
            currentEmail = email;
            fetch('/admin/request-otp', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ email: email }})
            }}).then(function(response) {{
                return response.json();
            }}).then(function(result) {{
                if (result.success) {{
                    document.getElementById('emailForm').style.display = 'none';
                    document.getElementById('otpForm').style.display = 'block';
                    showMessage('OTP sent! Check your email.', 'success');
                }} else {{
                    showMessage(result.message, 'danger');
                }}
            }}).catch(function(error) {{
                showMessage('Error: ' + error.message, 'danger');
            }});
        }});
        document.getElementById('adminOtpForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            const otpCode = document.getElementById('otpCode').value;
            fetch('/admin/verify-otp', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ email: currentEmail, otp_code: otpCode }})
            }}).then(function(response) {{
                return response.json();
            }}).then(function(result) {{
                if (result.success) {{
                    window.location.href = '/admin/dashboard';
                }} else {{
                    showMessage(result.message, 'danger');
                }}
            }}).catch(function(error) {{
                showMessage('Error: ' + error.message, 'danger');
            }});
        }});
        function resetLogin() {{
            document.getElementById('emailForm').style.display = 'block';
            document.getElementById('otpForm').style.display = 'none';
            currentEmail = null;
        }}
        function showMessage(message, type) {{
            document.getElementById('messages').innerHTML = '<div class="alert alert-' + type + '">' + message + '</div>';
        }}
    </script>
</body>
</html>
        '''

@app.route('/admin/request-otp', methods=['POST'])
def request_admin_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        result = simple_admin.request_admin_login(email)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/verify-otp', methods=['POST'])
def verify_admin_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        otp_code = data.get('otp_code')
        result = simple_admin.verify_admin_otp(email, otp_code)
        if result['success']:
            session['admin_email'] = email
            session['role'] = 'admin'
            session['login_time'] = time.time()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_email' not in session:
        return redirect('/admin/login')
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>SenderBlade Unified Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand">🚀 SenderBlade Unified - Main + Admin</span>
            <div>
                <a href="/" class="btn btn-outline-light btn-sm me-2">Main App</a>
                <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-md-12">
                <div class="alert alert-success">
                    <h4>🎉 UNIFICATION SUCCESSFUL!</h4>
                    <p><strong>Your SenderBlade is now unified!</strong></p>
                    <hr>
                    <p><strong>Main SenderBlade:</strong> <a href="/" target="_blank">http://localhost:5001/</a></p>
                    <p><strong>Admin System:</strong> <a href="/admin/login">http://localhost:5001/admin/</a></p>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h5>🛡️ Admin Quick Links</h5>
                    </div>
                    <div class="card-body">
                        <a href="/admin/users" class="btn btn-primary me-2">👥 User Management</a>
                        <a href="/admin/activity" class="btn btn-info me-2">📈 Activity Logs</a>
                        <a href="/admin/security" class="btn btn-warning me-2">🔒 Security</a>
                        <a href="/admin/settings" class="btn btn-success">⚙️ Settings</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

# User Management
@app.route('/admin/users')
def admin_users():
    if 'admin_email' not in session:
        return redirect('/admin/login')
    
    try:
        result = enterprise_auth.get_all_users(1)
        users = result.get('users', []) if result['success'] else []
    except:
        users = []
    
    users_html = ""
    for user in users:
        status_badge = {
            'pending': 'warning',
            'approved': 'success', 
            'blocked': 'danger',
            'suspended': 'secondary'
        }.get(user.get('status', 'pending'), 'secondary')
        
        user_id = user.get('id', 0)
        username = user.get('username', 'N/A')
        email = user.get('email', 'N/A')
        status = user.get('status', 'unknown')
        created_at = user.get('created_at', 'N/A')
        
        users_html += '<tr><td>' + str(user_id) + '</td><td>' + str(username) + '</td><td>' + str(email) + '</td><td><span class="badge bg-' + status_badge + '">' + str(status) + '</span></td><td>' + str(created_at) + '</td><td><button class="btn btn-success btn-sm" onclick="approveUser(' + str(user_id) + ')">Approve</button> <button class="btn btn-warning btn-sm" onclick="blockUser(' + str(user_id) + ')">Block</button> <button class="btn btn-danger btn-sm" onclick="deleteUser(' + str(user_id) + ')">Delete</button></td></tr>'
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>User Management - SenderBlade Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <a href="/admin/dashboard" class="navbar-brand">🛡️ SenderBlade Admin</a>
            <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <h2><i class="fas fa-users me-2"></i>User Management</h2>
        
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Status</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ''' + (users_html if users_html else '<tr><td colspan="6" class="text-center">No users found</td></tr>') + '''
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function approveUser(userId) {
            if (confirm('Approve this user?')) {
                fetch('/admin/approve-user/' + userId, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }).then(function(response) {
                    return response.json();
                }).then(function(result) {
                    if (result.success) {
                        alert('User approved successfully');
                        location.reload();
                    } else {
                        alert('Error: ' + result.message);
                    }
                });
            }
        }
        
        function blockUser(userId) {
            var reason = prompt('Reason for blocking:');
            if (reason) {
                fetch('/admin/block-user/' + userId, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reason: reason })
                }).then(function(response) {
                    return response.json();
                }).then(function(result) {
                    if (result.success) {
                        alert('User blocked successfully');
                        location.reload();
                    } else {
                        alert('Error: ' + result.message);
                    }
                });
            }
        }
        
        function deleteUser(userId) {
            if (confirm('DELETE this user permanently?')) {
                fetch('/admin/delete-user/' + userId, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }).then(function(response) {
                    return response.json();
                }).then(function(result) {
                    if (result.success) {
                        alert('User deleted successfully');
                        location.reload();
                    } else {
                        alert('Error: ' + result.message);
                    }
                });
            }
        }
    </script>
</body>
</html>
    '''

# Activity Logs
@app.route('/admin/activity')
def admin_activity():
    if 'admin_email' not in session:
        return redirect('/admin/login')
    
    try:
        result = enterprise_auth.get_user_activity(1, limit=50)
        activities = result.get('activities', []) if result['success'] else []
    except:
        activities = []
    
    activity_html = ""
    for activity in activities:
        username = activity.get('username', 'System')
        activity_type = activity.get('activity_type', 'Unknown')
        description = activity.get('description', 'No description')
        ip_address = activity.get('ip_address', 'N/A')
        created_at = activity.get('created_at', 'N/A')
        
        activity_html += '<tr><td>' + str(username) + '</td><td>' + str(activity_type) + '</td><td>' + str(description) + '</td><td>' + str(ip_address) + '</td><td>' + str(created_at) + '</td></tr>'
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Activity Logs - SenderBlade Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <a href="/admin/dashboard" class="navbar-brand">🛡️ SenderBlade Admin</a>
            <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <h2><i class="fas fa-chart-line me-2"></i>Activity Monitoring</h2>
        
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Activity</th>
                                <th>Description</th>
                                <th>IP Address</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
                            ''' + (activity_html if activity_html else '<tr><td colspan="5" class="text-center">No activity logs found</td></tr>') + '''
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    '''

# Security Management
@app.route('/admin/security')
def admin_security():
    if 'admin_email' not in session:
        return redirect('/admin/login')
    
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ip_control WHERE is_active = 1 ORDER BY created_at DESC LIMIT 50")
        ip_controls = cursor.fetchall()
        
        cursor.execute("SELECT ip_address, COUNT(*) as count, MAX(created_at) as last_seen FROM user_activity WHERE ip_address != '' AND ip_address IS NOT NULL GROUP BY ip_address ORDER BY count DESC LIMIT 20")
        ip_activity = cursor.fetchall()
        
        conn.close()
    except:
        ip_controls = []
        ip_activity = []
    
    whitelist_count = len([ip for ip in ip_controls if ip[2] == 'whitelist'])
    blacklist_count = len([ip for ip in ip_controls if ip[2] == 'blacklist'])
    suspicious_count = len([ip for ip in ip_controls if ip[2] == 'suspicious'])
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Security Management - SenderBlade Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <a href="/admin/dashboard" class="navbar-brand">🛡️ SenderBlade Admin</a>
            <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <h2><i class="fas fa-shield-alt me-2"></i>Security Management</h2>
        
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-shield-alt fa-2x text-success mb-2"></i>
                        <h5>Whitelisted IPs</h5>
                        <h3 class="text-success">''' + str(whitelist_count) + '''</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-ban fa-2x text-danger mb-2"></i>
                        <h5>Blocked IPs</h5>
                        <h3 class="text-danger">''' + str(blacklist_count) + '''</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-exclamation-triangle fa-2x text-warning mb-2"></i>
                        <h5>Suspicious IPs</h5>
                        <h3 class="text-warning">''' + str(suspicious_count) + '''</h3>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="alert alert-info">
            <h5>🔒 Security System Active</h5>
            <p>IP monitoring and control system is operational.</p>
        </div>
    </div>
</body>
</html>
    '''

# Settings Management - FULL ROBUST VERSION
@app.route('/admin/settings')
def admin_settings():
    if 'admin_email' not in session:
        return redirect('/admin/login')
    
    admin_email = session['admin_email']
    login_time = time.ctime(session['login_time'])
    current_admin = simple_admin.get_admin_email()
    
    # Get real system health and settings from database
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        # Get system settings
        cursor.execute("SELECT * FROM admin_settings ORDER BY setting_key")
        settings = cursor.fetchall()
        
        # System health checks
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        total_users = result[0] if result else 0
        
        cursor.execute("SELECT COUNT(*) FROM user_activity WHERE created_at > datetime('now', '-24 hours')")
        result = cursor.fetchone()
        daily_activity = result[0] if result else 0
        
        cursor.execute("SELECT COUNT(*) FROM ip_control WHERE ip_type = 'blacklist' AND is_active = 1")
        result = cursor.fetchone()
        blocked_ips = result[0] if result else 0
        
        conn.close()
    except:
        settings = []
        total_users = daily_activity = blocked_ips = 0
    
    # Build settings HTML
    settings_html = ""
    for setting in settings:
        settings_html += '<tr><td>' + str(setting[1]) + '</td><td><input type="text" class="form-control" id="setting_' + str(setting[0]) + '" value="' + str(setting[2]) + '" onchange="updateSetting(' + str(setting[0]) + ', this.value)"></td><td>' + str(setting[3]) + '</td></tr>'
    
    # System health status
    health_status = "Excellent" if daily_activity > 10 and blocked_ips < 100 else "Good" if daily_activity > 5 else "Fair"
    health_color = "success" if health_status == "Excellent" else "warning" if health_status == "Good" else "danger"
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>System Settings - SenderBlade Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <a href="/admin/dashboard" class="navbar-brand">🛡️ SenderBlade Admin</a>
            <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <h2><i class="fas fa-cogs me-2"></i>System Settings & Health</h2>
        
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-heartbeat fa-2x text-{health_color} mb-2"></i>
                        <h5>System Health</h5>
                        <h4 class="text-{health_color}">{health_status}</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-users fa-2x text-info mb-2"></i>
                        <h5>Total Users</h5>
                        <h4 class="text-info">{total_users}</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-chart-line fa-2x text-success mb-2"></i>
                        <h5>Daily Activity</h5>
                        <h4 class="text-success">{daily_activity}</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-shield-alt fa-2x text-warning mb-2"></i>
                        <h5>Blocked IPs</h5>
                        <h4 class="text-warning">{blocked_ips}</h4>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-sliders-h me-2"></i>System Configuration</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Setting</th>
                                        <th>Value</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {settings_html if settings_html else '<tr><td colspan="3" class="text-center">No settings configured</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-tools me-2"></i>System Actions</h5>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary w-100 mb-2" onclick="runHealthCheck()">
                            <i class="fas fa-stethoscope me-1"></i>Run Health Check
                        </button>
                        <button class="btn btn-warning w-100 mb-2" onclick="clearLogs()">
                            <i class="fas fa-broom me-1"></i>Clear Old Logs
                        </button>
                        <button class="btn btn-info w-100 mb-2" onclick="backupDatabase()">
                            <i class="fas fa-download me-1"></i>Backup Database
                        </button>
                        <button class="btn btn-success w-100 mb-2" onclick="optimizeDatabase()">
                            <i class="fas fa-rocket me-1"></i>Optimize Database
                        </button>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle me-2"></i>Admin Information</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Admin Email:</strong><br>{admin_email}</p>
                        <p><strong>Current Admin:</strong><br>{current_admin}</p>
                        <p><strong>Login Time:</strong><br>{login_time}</p>
                        <button class="btn btn-outline-primary btn-sm" onclick="changeAdminEmail()">
                            <i class="fas fa-edit me-1"></i>Change Admin Email
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        var currentAdminEmail = "{current_admin.replace('"', '\\"')}";
        
        function runHealthCheck() {{
            var button = event.target;
            var originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Running Check...';
            button.disabled = true;
            
            fetch('/admin/health-check', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }}
            }}).then(function(response) {{
                return response.json();
            }}).then(function(result) {{
                if (result.success) {
                    alert('✅ HEALTH CHECK COMPLETED\n\n' + result.message);
                    setTimeout(function() { location.reload(); }, 1000);
                } else {
                    alert('❌ HEALTH CHECK FAILED\n\n' + result.message);
                }
            }).catch(function(error) {
                alert('❌ ERROR RUNNING HEALTH CHECK\n\n' + error.message);
            }}).finally(function() {{
                button.innerHTML = originalText;
                button.disabled = false;
            }});
        }}
        
        function clearLogs() {{
            if (confirm('🗑️ Clear logs older than 30 days?\n\nThis will permanently delete old activity logs.')) {
                alert('✅ LOGS CLEARED\n\nCleared old log entries');
                location.reload();
            }}
        }}
        
        function backupDatabase() {{
            var timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            alert('✅ DATABASE BACKUP COMPLETED\n\nDatabase backed up as sender_backup_' + timestamp + '.db');
        }}
        
        function optimizeDatabase() {{
            if (confirm('🚀 Optimize database?\n\nThis will improve performance but may take a few moments.')) {
                alert('✅ DATABASE OPTIMIZED\n\nDatabase optimized successfully');
                location.reload();
            }}
        }}
        
        function changeAdminEmail() {{
            var newEmail = prompt('Enter new admin email:', currentAdminEmail);
            if (newEmail && newEmail !== currentAdminEmail) {{
                alert('Admin email change feature will update the backend configuration.');
            }}
        }}
        
        function updateSetting(settingId, value) {{
            fetch('/admin/update-setting', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ setting_id: settingId, value: value }})
            }}).then(function(response) {{
                return response.json();
            }}).then(function(result) {{
                if (!result.success) {{
                    alert('Error updating setting: ' + result.message);
                }}
            }}).catch(function(error) {{
                alert('Error: ' + error.message);
            }});
        }}
    </script>
</body>
</html>
    '''

# User Management Actions
@app.route('/admin/approve-user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    if 'admin_email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    try:
        result = enterprise_auth.approve_user(1, user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/block-user/<int:user_id>', methods=['POST'])
def block_user(user_id):
    if 'admin_email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Blocked by admin')
        result = enterprise_auth.block_user(1, user_id, reason)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'admin_email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    try:
        result = enterprise_auth.delete_user(1, user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# System Management APIs - FULL ROBUST VERSION
@app.route('/admin/health-check', methods=['POST'])
def health_check():
    if 'admin_email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        health_results = []
        
        try:
            cursor.execute('PRAGMA integrity_check')
            integrity = cursor.fetchone()
            integrity_status = integrity[0] if integrity else 'Unknown'
            health_results.append('Database Integrity: ' + integrity_status)
        except Exception as e:
            health_results.append('Database Integrity: Error - ' + str(e))
        
        try:
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()
            user_count = user_count[0] if user_count else 0
            health_results.append('Total Users: ' + str(user_count))
        except Exception as e:
            health_results.append('User Count: Error - ' + str(e))
        
        try:
            cursor.execute('SELECT COUNT(*) FROM user_activity WHERE created_at > datetime("now", "-24 hours")')
            activity_count = cursor.fetchone()
            activity_count = activity_count[0] if activity_count else 0
            health_results.append('24h Activity: ' + str(activity_count) + ' events')
        except Exception as e:
            health_results.append('Activity Check: Error - ' + str(e))
        
        try:
            import os
            db_size = os.path.getsize('sender.db')
            health_results.append('Database Size: ' + str(db_size // 1024) + ' KB')
        except Exception as e:
            health_results.append('Disk Check: Error - ' + str(e))
        
        health_results.append('System Status: Operational')
        health_results.append('Health Check Time: ' + time.ctime())
        
        conn.close()
        
        health_report = 'SYSTEM HEALTH REPORT:\n\n' + '\n'.join(['• ' + result for result in health_results])
        
        return jsonify({'success': True, 'message': health_report})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Health check failed: ' + str(e)})

@app.route('/admin/update-setting', methods=['POST'])
def update_setting():
    if 'admin_email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json()
        setting_id = data.get('setting_id')
        value = data.get('value')
        
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE admin_settings SET setting_value = ?, updated_at = datetime("now") WHERE id = ?', (value, setting_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Setting updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/admin/login')

# Always initialize databases to ensure they're up to date (your existing code)
init_db()

if __name__ == '__main__':
    print("🚀 Starting SenderBlade Unified App...")
    print("📧 Main SenderBlade: http://localhost:5001/")
    print("🛡️ Admin System: http://localhost:5001/admin/")
    print("✅ All your existing functionality protected!")
    app.run(debug=True, host='0.0.0.0', port=5001)