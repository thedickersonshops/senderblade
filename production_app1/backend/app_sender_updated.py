"""
Updated SenderBlade with Admin Integration
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import json
import time
from datetime import datetime
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import existing modules
from simple_db import execute_db, fetch_db
from enterprise_auth import enterprise_auth

app = Flask(__name__)
app.secret_key = 'senderblade_secret_key_change_in_production'
CORS(app)

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login with in-house OTP"""
    if request.method == 'GET':
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>SenderBlade Admin Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .admin-card { background: rgba(255,255,255,0.95); border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
        .otp-display { background: #f8f9fa; border: 2px dashed #28a745; border-radius: 10px; font-family: monospace; font-size: 24px; font-weight: bold; color: #28a745; }
    </style>
</head>
<body>
    <div class="container-fluid d-flex align-items-center justify-content-center min-vh-100">
        <div class="col-md-4">
            <div class="admin-card p-5">
                <div class="text-center mb-4">
                    <h2>🛡️ SenderBlade Admin</h2>
                    <p class="text-muted">Secure Admin Access</p>
                </div>

                <div id="loginForm">
                    <form id="adminLoginForm">
                        <div class="mb-3">
                            <label class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" value="admin" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" value="admin123" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Generate Admin OTP</button>
                    </form>
                </div>

                <div id="otpForm" style="display: none;">
                    <div class="text-center mb-4">
                        <h5>Admin OTP Generated</h5>
                        <div class="otp-display p-3 my-3" id="otpDisplay"></div>
                        <small class="text-muted">Enter the OTP above to complete login</small>
                    </div>
                    
                    <form id="adminOtpForm">
                        <div class="mb-3">
                            <label class="form-label">Enter OTP Code</label>
                            <input type="text" class="form-control text-center" id="otpCode" maxlength="8" required>
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
        let currentUserId = null;

        document.getElementById('adminLoginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/admin/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentUserId = result.user_id;
                    document.getElementById('otpDisplay').textContent = result.otp_code;
                    document.getElementById('loginForm').style.display = 'none';
                    document.getElementById('otpForm').style.display = 'block';
                    showMessage('OTP generated! Expires in ' + result.expires_in + ' minutes.', 'success');
                } else {
                    showMessage(result.message, 'danger');
                }
            } catch (error) {
                showMessage('Login error: ' + error.message, 'danger');
            }
        });

        document.getElementById('adminOtpForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const otpCode = document.getElementById('otpCode').value;
            
            try {
                const response = await fetch('/admin/verify-otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: currentUserId, otp_code: otpCode })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('Login successful! Redirecting...', 'success');
                    setTimeout(() => { window.location.href = '/admin/dashboard'; }, 1000);
                } else {
                    showMessage(result.message, 'danger');
                }
            } catch (error) {
                showMessage('OTP verification error: ' + error.message, 'danger');
            }
        });

        function resetLogin() {
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('otpForm').style.display = 'none';
            currentUserId = null;
        }

        function showMessage(message, type) {
            document.getElementById('messages').innerHTML = '<div class="alert alert-' + type + '">' + message + '</div>';
        }
    </script>
</body>
</html>
        '''
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        result = enterprise_auth.admin_login(username, password)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login error: {str(e)}'})

@app.route('/admin/verify-otp', methods=['POST'])
def verify_admin_otp():
    """Verify admin OTP"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        otp_code = data.get('otp_code')
        
        result = enterprise_auth.verify_admin_otp(user_id, otp_code)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'OTP verification error: {str(e)}'})

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'super_admin']:
        return redirect('/admin/login')
    
    try:
        users_result = enterprise_auth.get_all_users(session['user_id'])
        activity_result = enterprise_auth.get_user_activity(session['user_id'], limit=10)
        
        users = users_result.get('users', []) if users_result['success'] else []
        activities = activity_result.get('activities', []) if activity_result['success'] else []
        
        stats = {
            'total_users': len(users),
            'pending_users': len([u for u in users if u['status'] == 'pending']),
            'active_users': len([u for u in users if u['is_active']]),
            'blocked_users': len([u for u in users if u['status'] == 'blocked'])
        }
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <title>SenderBlade Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand">🛡️ SenderBlade Admin Dashboard</span>
            <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">👥 Total Users</h5>
                        <h2 class="text-primary">{stats['total_users']}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">⏳ Pending Approval</h5>
                        <h2 class="text-warning">{stats['pending_users']}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">✅ Active Users</h5>
                        <h2 class="text-success">{stats['active_users']}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">🚫 Blocked Users</h5>
                        <h2 class="text-danger">{stats['blocked_users']}</h2>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>👥 User Management</h5>
                    </div>
                    <div class="card-body">
                        <a href="/admin/users" class="btn btn-primary">Manage Users</a>
                        <a href="/admin/activity" class="btn btn-info">View Activity</a>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>📊 Recent Activity</h5>
                    </div>
                    <div class="card-body">
                        {"<br>".join([f"• {a.get('description', 'Activity')} ({a.get('username', 'Unknown')})" for a in activities[:5]])}
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        '''
        
    except Exception as e:
        return f"Dashboard error: {str(e)}"

@app.route('/admin/users')
def admin_users():
    """User management"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'super_admin']:
        return redirect('/admin/login')
    
    try:
        result = enterprise_auth.get_all_users(session['user_id'])
        users = result.get('users', []) if result['success'] else []
        
        users_html = ""
        for user in users:
            status_badge = {
                'pending': 'warning',
                'approved': 'success', 
                'blocked': 'danger',
                'suspended': 'secondary'
            }.get(user['status'], 'secondary')
            
            users_html += f'''
            <tr>
                <td>{user['id']}</td>
                <td>{user['username']}</td>
                <td>{user['email']}</td>
                <td><span class="badge bg-{status_badge}">{user['status']}</span></td>
                <td>{user['created_at']}</td>
                <td>
                    <button class="btn btn-success btn-sm" onclick="approveUser({user['id']})">Approve</button>
                    <button class="btn btn-warning btn-sm" onclick="blockUser({user['id']})">Block</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteUser({user['id']})">Delete</button>
                </td>
            </tr>
            '''
        
        return f'''
<!DOCTYPE html>
<html>
<head>
    <title>User Management - SenderBlade Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <a href="/admin/dashboard" class="navbar-brand">🛡️ SenderBlade Admin</a>
            <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <h2>👥 User Management</h2>
        
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
                    {users_html}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        async function approveUser(userId) {{
            if (confirm('Approve this user?')) {{
                try {{
                    const response = await fetch('/admin/approve-user/' + userId, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    const result = await response.json();
                    if (result.success) {{
                        alert('User approved successfully');
                        location.reload();
                    }} else {{
                        alert('Error: ' + result.message);
                    }}
                }} catch (error) {{
                    alert('Error: ' + error.message);
                }}
            }}
        }}
        
        async function blockUser(userId) {{
            const reason = prompt('Reason for blocking:');
            if (reason) {{
                try {{
                    const response = await fetch('/admin/block-user/' + userId, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ reason: reason }})
                    }});
                    const result = await response.json();
                    if (result.success) {{
                        alert('User blocked successfully');
                        location.reload();
                    }} else {{
                        alert('Error: ' + result.message);
                    }}
                }} catch (error) {{
                    alert('Error: ' + error.message);
                }}
            }}
        }}
        
        async function deleteUser(userId) {{
            if (confirm('DELETE this user permanently? This cannot be undone!')) {{
                try {{
                    const response = await fetch('/admin/delete-user/' + userId, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }});
                    const result = await response.json();
                    if (result.success) {{
                        alert('User deleted successfully');
                        location.reload();
                    }} else {{
                        alert('Error: ' + result.message);
                    }}
                }} catch (error) {{
                    alert('Error: ' + error.message);
                }}
            }}
        }}
    </script>
</body>
</html>
        '''
        
    except Exception as e:
        return f"Users page error: {str(e)}"

@app.route('/admin/approve-user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    """Approve user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        result = enterprise_auth.approve_user(session['user_id'], user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/block-user/<int:user_id>', methods=['POST'])
def block_user(user_id):
    """Block user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Blocked by admin')
        result = enterprise_auth.block_user(session['user_id'], user_id, reason)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        result = enterprise_auth.delete_user(session['user_id'], user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect('/admin/login')

# Original SenderBlade routes
@app.route('/')
def index():
    return '''
    <h1>🔥 SenderBlade - Email Campaign Management</h1>
    <p><a href="/admin/login">🛡️ Admin Login</a></p>
    <p>Main SenderBlade interface coming soon...</p>
    '''

if __name__ == '__main__':
    print("🚀 Starting SenderBlade with Admin System...")
    print("🛡️ Admin Login: http://localhost:5001/admin/login")
    print("👤 Default Admin: admin / admin123")
    app.run(debug=True, host='0.0.0.0', port=5001)