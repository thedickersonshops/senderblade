"""
NUCLEAR SECURITY AUTH API - ZERO BYPASS POSSIBLE
"""
import os
import sqlite3
import hashlib
import secrets
from flask import Blueprint, request, jsonify, session, make_response

# Create blueprint
auth_api = Blueprint('auth_api', __name__)

# Database functions
def query_db(query, args=(), one=False):
    try:
        conn = sqlite3.connect('sender.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, args)
        
        if one:
            result = cursor.fetchone()
            conn.close()
            return dict(result) if result else None
        else:
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
    except Exception as e:
        print(f"Database query error: {e}")
        return None if one else []

def execute_db(query, args=()):
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        cursor.execute(query, args)
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_id
    except Exception as e:
        print(f"Database execute error: {e}")
        return None

def hash_password(password):
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password, stored_hash):
    try:
        salt, hashed = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except:
        return False

@auth_api.route('/login', methods=['POST'])
def login():
    """NUCLEAR SECURITY - ZERO BYPASS LOGIN"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    otp_code = data.get('otp_code')
    
    print(f"\n=== LOGIN ATTEMPT START ===")
    print(f"Username: {username}")
    print(f"Password provided: {bool(password)}")
    print(f"OTP provided: {otp_code}")
    
    if not username or not password:
        print("BLOCKED: Missing credentials")
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    # Get user
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if not user or not verify_password(password, user['password']):
        print("BLOCKED: Invalid credentials")
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    print(f"User found: {user['username']}, Status: {user['status']}")
    
    # Check user status
    if not user.get('otp_verified', 0):
        print("BLOCKED: Email not verified")
        return jsonify({
            'success': False, 
            'message': 'Please verify your email first. Check your email for OTP code.',
            'requires_otp': True,
            'user_id': user['id']
        }), 403
    
    if user['status'] != 'approved':
        print(f"BLOCKED: User status is {user['status']}")
        status_messages = {
            'pending': 'Your account is pending admin approval. Please wait for approval.',
            'blocked': 'Your account has been blocked. Please contact administrator.',
            'suspended': 'Your account has been suspended. Please contact administrator.'
        }
        return jsonify({
            'success': False, 
            'message': status_messages.get(user['status'], 'Account not approved for login.')
        }), 403
    
    if not user.get('is_active', 0):
        print("BLOCKED: User not active")
        return jsonify({'success': False, 'message': 'Account is not active. Please contact administrator.'}), 403
    
    # NUCLEAR OPTION: NEVER ALLOW LOGIN WITHOUT OTP - PERIOD!
    if not otp_code or otp_code.strip() == '':
        print("\n=== GENERATING OTP - NO BYPASS POSSIBLE ===")
        
        # Generate fresh OTP
        import random
        import time
        login_otp = str(random.randint(100000, 999999))
        otp_expires = int(time.time()) + 300  # 5 minutes
        
        print(f"Generated OTP: {login_otp}")
        
        # Store in database
        execute_db(
            'UPDATE users SET login_otp = ?, login_otp_expires = ? WHERE id = ?',
            (login_otp, otp_expires, user['id'])
        )
        
        # Send OTP email
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "timothykeeton.tk@gmail.com"
            sender_password = "akda bgpw becv kbso"
            
            subject = "SenderBlade - Login Verification Code"
            body = f"""
Hello {user['username']},

Your login verification code is: {login_otp}

This code will expire in 5 minutes.

If you didn't request this login, please secure your account immediately.

Best regards,
SenderBlade Security Team
            """
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = user['email']
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            print(f"OTP EMAIL SENT to {user['email']}")
            
        except Exception as e:
            print(f"OTP EMAIL FAILED: {e}")
            return jsonify({'success': False, 'message': 'Failed to send login OTP'}), 500
        
        print("BLOCKING LOGIN - OTP REQUIRED")
        print("=== LOGIN ATTEMPT BLOCKED ===")
        
        # ABSOLUTELY NO SUCCESS WITHOUT OTP
        return jsonify({
            'success': False,
            'otp_required': True,
            'message': f'🔐 Security verification required! OTP sent to {user["email"][:3]}***@{user["email"].split("@")[1]}. Please enter the 6-digit code.',
            'user_id': user['id']
        }), 403  # Forbidden - must provide OTP
    
    # OTP provided - validate it
    print(f"\n=== VALIDATING OTP: {otp_code} ===")
    
    import time
    current_time = int(time.time())
    
    # Get fresh user data
    user_fresh = query_db('SELECT * FROM users WHERE id = ?', [user['id']], one=True)
    stored_otp = user_fresh.get('login_otp')
    otp_expires = user_fresh.get('login_otp_expires', 0)
    
    print(f"Stored OTP: {stored_otp}")
    print(f"Provided OTP: {otp_code}")
    print(f"Expires: {otp_expires}, Current: {current_time}")
    
    if not stored_otp:
        print("BLOCKED: No OTP in database")
        return jsonify({'success': False, 'message': 'No OTP found. Please request a new login code.'}), 400
    
    if str(stored_otp) != str(otp_code):
        print(f"BLOCKED: OTP mismatch - Expected: {stored_otp}, Got: {otp_code}")
        return jsonify({'success': False, 'message': 'Invalid OTP code. Please check your email and try again.'}), 400
    
    if current_time > otp_expires:
        print("BLOCKED: OTP expired")
        execute_db('UPDATE users SET login_otp = NULL, login_otp_expires = NULL WHERE id = ?', (user['id'],))
        return jsonify({'success': False, 'message': 'OTP has expired. Please login again to get a new code.'}), 400
    
    print("OTP VALIDATION SUCCESS!")
    
    # Clear OTP and create session
    execute_db(
        'UPDATE users SET login_otp = NULL, login_otp_expires = NULL WHERE id = ?',
        (user['id'],)
    )
    
    # Set session
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['login_time'] = current_time
    session.permanent = True
    
    # Log successful login
    try:
        execute_db(
            '''INSERT INTO user_activity (user_id, username, activity_type, description, ip_address, created_at)
               VALUES (?, ?, 'login', 'User logged in with OTP verification', ?, datetime('now'))''',
            (user['id'], user['username'], request.remote_addr or 'unknown')
        )
    except Exception as e:
        print(f"Activity log error: {e}")
    
    print(f"LOGIN SUCCESS: User {user['username']} logged in with OTP")
    print("=== LOGIN ATTEMPT COMPLETED ===")
    
    response = make_response(jsonify({
        'success': True, 
        'message': 'Login successful with OTP verification',
        'user': {'id': user['id'], 'username': user['username'], 'email': user['email'] or ''},
        'session_timeout': 1800
    }))
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# Copy other routes from original auth_api
@auth_api.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_api.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    import time
    current_time = int(time.time())
    login_time = session.get('login_time', 0)
    session_timeout = 1800  # 30 minutes
    
    if current_time - login_time > session_timeout:
        session.clear()
        return jsonify({
            'success': False, 
            'message': 'Session expired due to inactivity. Please login again.',
            'session_expired': True
        }), 401
    
    try:
        user = query_db('SELECT id, username, email FROM users WHERE id = ?', [session['user_id']], one=True)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        session['last_activity'] = current_time
        
        response = make_response(jsonify({
            'success': True,
            'user': {'id': user['id'], 'username': user['username'], 'email': user['email'] or ''},
            'session_remaining': session_timeout - (current_time - login_time)
        }))
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    except Exception as e:
        return jsonify({'success': False, 'message': 'Database error'}), 500