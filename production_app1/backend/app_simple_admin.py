"""
SenderBlade with Simple Email-Only Admin
"""
from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
import sqlite3
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_admin import simple_admin

app = Flask(__name__)
app.secret_key = 'senderblade_secret_key_change_in_production'
CORS(app)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login - email only"""
    if request.method == 'GET':
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
                    <p class="text-muted">Email-Only Admin Access</p>
                </div>

                <div id="emailForm">
                    <form id="adminEmailForm">
                        <div class="mb-3">
                            <label class="form-label">Admin Email</label>
                            <input type="email" class="form-control" id="adminEmail" 
                                   value="{simple_admin.get_admin_email()}" required>
                            <small class="text-muted">OTP will be sent to this email</small>
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
                            <label class="form-label">Enter OTP Code</label>
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

        document.getElementById('adminEmailForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const email = document.getElementById('adminEmail').value;
            currentEmail = email;
            
            showMessage('Sending OTP to ' + email + '...', 'info');
            
            try {{
                const response = await fetch('/admin/request-otp', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ email: email }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    document.getElementById('emailForm').style.display = 'none';
                    document.getElementById('otpForm').style.display = 'block';
                    showMessage('OTP sent! Check your email. Expires in ' + result.expires_in + ' minutes.', 'success');
                }} else {{
                    showMessage(result.message, 'danger');
                }}
            }} catch (error) {{
                showMessage('Error: ' + error.message, 'danger');
            }}
        }});

        document.getElementById('adminOtpForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const otpCode = document.getElementById('otpCode').value;
            
            if (!currentEmail) {{
                showMessage('Session expired. Please start over.', 'danger');
                resetLogin();
                return;
            }}
            
            showMessage('Verifying OTP...', 'info');
            
            try {{
                const response = await fetch('/admin/verify-otp', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ email: currentEmail, otp_code: otpCode }})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    showMessage('Login successful! Redirecting...', 'success');
                    setTimeout(() => {{ window.location.href = '/admin/dashboard'; }}, 1000);
                }} else {{
                    showMessage(result.message, 'danger');
                }}
            }} catch (error) {{
                showMessage('Error: ' + error.message, 'danger');
            }}
        }});

        function resetLogin() {{
            document.getElementById('emailForm').style.display = 'block';
            document.getElementById('otpForm').style.display = 'none';
            document.getElementById('adminEmailForm').reset();
            document.getElementById('adminOtpForm').reset();
            currentEmail = null;
            clearMessages();
        }}

        function showMessage(message, type) {{
            document.getElementById('messages').innerHTML = '<div class="alert alert-' + type + '">' + message + '</div>';
        }}

        function clearMessages() {{
            document.getElementById('messages').innerHTML = '';
        }}
    </script>
</body>
</html>
        '''
    
@app.route('/admin/request-otp', methods=['POST'])
def request_admin_otp():
    """Request admin OTP"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        result = simple_admin.request_admin_login(email)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({{'success': False, 'message': f'Error: {{str(e)}}'})

@app.route('/admin/verify-otp', methods=['POST'])
def verify_admin_otp():
    """Verify admin OTP"""
    try:
        data = request.get_json()
        email = data.get('email')
        otp_code = data.get('otp_code')
        
        result = simple_admin.verify_admin_otp(email, otp_code)
        
        if result['success']:
            # Set session
            session['admin_email'] = email
            session['role'] = 'admin'
            session['login_time'] = time.time()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({{'success': False, 'message': f'Error: {{str(e)}}'})

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'admin_email' not in session:
        return redirect('/admin/login')
    
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
            <div>
                <span class="text-light me-3">👤 {{session['admin_email']}}</span>
                <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>🎉 Welcome to SenderBlade Admin!</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Admin Email:</strong> {{session['admin_email']}}</p>
                        <p><strong>Login Time:</strong> {{time.ctime(session['login_time'])}}</p>
                        
                        <hr>
                        
                        <h6>📧 Admin Email Management:</h6>
                        <p><strong>Current Admin Email:</strong> {{simple_admin.get_admin_email()}}</p>
                        
                        <div class="mt-3">
                            <h6>🔧 Quick Actions:</h6>
                            <button class="btn btn-primary" onclick="alert('SenderBlade features coming soon!')">
                                📊 View Campaigns
                            </button>
                            <button class="btn btn-info" onclick="alert('User management coming soon!')">
                                👥 Manage Users
                            </button>
                            <button class="btn btn-warning" onclick="showEmailUpdate()">
                                ✏️ Update Admin Email
                            </button>
                        </div>
                        
                        <div id="emailUpdateForm" style="display: none;" class="mt-4">
                            <div class="card">
                                <div class="card-header">Update Admin Email</div>
                                <div class="card-body">
                                    <div class="mb-3">
                                        <label class="form-label">New Admin Email</label>
                                        <input type="email" class="form-control" id="newAdminEmail" 
                                               placeholder="new-admin@example.com">
                                    </div>
                                    <button class="btn btn-success" onclick="updateAdminEmail()">Update Email</button>
                                    <button class="btn btn-secondary" onclick="hideEmailUpdate()">Cancel</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showEmailUpdate() {{
            document.getElementById('emailUpdateForm').style.display = 'block';
        }}
        
        function hideEmailUpdate() {{
            document.getElementById('emailUpdateForm').style.display = 'none';
        }}
        
        function updateAdminEmail() {{
            const newEmail = document.getElementById('newAdminEmail').value;
            if (newEmail) {{
                alert('Admin email update feature will be implemented in backend.');
                // This would call an API to update the admin email
            }} else {{
                alert('Please enter a valid email address.');
            }}
        }}
    </script>
</body>
</html>
    '''

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect('/admin/login')

@app.route('/')
def index():
    return '''
    <h1>🔥 SenderBlade - Email Campaign Management</h1>
    <p><a href="/admin/login">🛡️ Admin Login (Email + OTP)</a></p>
    <p>Main SenderBlade interface coming soon...</p>
    '''

if __name__ == '__main__':
    print("🚀 Starting SenderBlade with Email-Only Admin...")
    print("🛡️ Admin Login: http://localhost:5001/admin/login")
    print(f"📧 Admin Email: {{simple_admin.get_admin_email()}}")
    print("⚠️  Configure Gmail SMTP in simple_admin.py to send OTP emails")
    app.run(debug=True, host='0.0.0.0', port=5001)