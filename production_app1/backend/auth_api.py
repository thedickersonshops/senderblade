"""
Authentication API - Handles user login, registration, and session management
"""
import os
import sqlite3
import hashlib
import secrets
from flask import Blueprint, request, jsonify, session, make_response
from functools import wraps

# Create blueprint
auth_api = Blueprint('auth_api', __name__)

# Database functions for sender.db
def query_db(query, args=(), one=False):
    """Query database and return results"""
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
    """Execute database query and return last row id"""
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

# Hash password
def hash_password(password):
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"

# Verify password
def verify_password(password, stored_hash):
    try:
        salt, hashed = stored_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except:
        return False

@auth_api.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    full_name = data.get('full_name', '')
    phone = data.get('phone', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required for OTP verification'}), 400
    
    # Check if user exists
    existing = query_db('SELECT * FROM users WHERE username = ? OR email = ?', [username, email], one=True)
    if existing:
        return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
    
    # Generate OTP
    import random
    otp_code = str(random.randint(100000, 999999))
    
    # Send OTP email using working admin email system
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        # Use the working Gmail credentials from simple_admin
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "timothykeeton.tk@gmail.com"
        sender_password = "akda bgpw becv kbso"  # Working password from simple_admin
        
        # Create email message
        subject = "SenderBlade - Email Verification Code"
        body = f"""
Welcome to SenderBlade, {username}!

Your email verification code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
SenderBlade Team
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = email
        
        # Send email using working credentials
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"OTP email sent successfully to {email}")
        
    except Exception as e:
        print(f"OTP send error: {e}")
        return jsonify({'success': False, 'message': f'Failed to send OTP email: {str(e)}'}), 500
    
    # Create user with pending status and store OTP
    hashed_password = hash_password(password)
    import time
    otp_expires = int(time.time()) + 600  # 10 minutes
    
    user_id = execute_db(
        '''INSERT INTO users (username, password, email, full_name, phone, status, is_active, otp_code, otp_expires, created_at) 
           VALUES (?, ?, ?, ?, ?, 'pending', 0, ?, ?, datetime('now'))''',
        (username, hashed_password, email, full_name, phone, otp_code, otp_expires)
    )
    
    # Log the registration
    try:
        execute_db(
            '''INSERT INTO user_activity (user_id, username, activity_type, description, ip_address, created_at)
               VALUES (?, ?, 'registration', 'User registered - awaiting OTP verification', ?, datetime('now'))''',
            (user_id, username, request.remote_addr or 'unknown')
        )
    except Exception as e:
        print(f"Activity log error: {e}")
    
    return jsonify({
        'success': True, 
        'message': 'Registration successful! Please check your email for OTP verification code.',
        'requires_otp': True,
        'user_id': user_id
    })

@auth_api.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    user_id = data.get('user_id')
    otp_code = data.get('otp_code')
    
    if not user_id or not otp_code:
        return jsonify({'success': False, 'message': 'User ID and OTP code required'}), 400
    
    # Get user and verify OTP
    user = query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    import time
    current_time = int(time.time())
    
    if user['otp_code'] != otp_code:
        return jsonify({'success': False, 'message': 'Invalid OTP code'}), 400
    
    if current_time > user['otp_expires']:
        return jsonify({'success': False, 'message': 'OTP code has expired. Please register again.'}), 400
    
    # Mark OTP as verified, but keep user pending for admin approval
    execute_db(
        'UPDATE users SET otp_verified = 1, otp_code = NULL, otp_expires = NULL WHERE id = ?',
        (user_id,)
    )
    
    # Log OTP verification
    try:
        execute_db(
            '''INSERT INTO user_activity (user_id, username, activity_type, description, ip_address, created_at)
               VALUES (?, ?, 'otp_verified', 'User verified OTP - awaiting admin approval', ?, datetime('now'))''',
            (user_id, user['username'], request.remote_addr or 'unknown')
        )
    except Exception as e:
        print(f"Activity log error: {e}")
    
    # Send notifications
    try:
        from notification_system import notification_system
        
        # Notify admin of new user
        notification_system.notify_admin_new_user(user['username'], user['email'])
        
        # Notify user about pending approval
        notification_system.notify_user_pending_approval(user['username'], user['email'])
        
    except Exception as e:
        print(f"Notification error: {e}")
    
    return jsonify({
        'success': True, 
        'message': 'OTP verified successfully! Your account is now pending admin approval. You will be notified once approved.',
        'status': 'pending_approval'
    })

@auth_api.route('/login-step1', methods=['POST'])
def login_step1():
    """Step 1: Validate credentials and send OTP"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    # Get user
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if not user or not verify_password(password, user['password']):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    # Check if user is verified and approved
    if not user.get('otp_verified', 0):
        return jsonify({
            'success': False, 
            'message': 'Please verify your email first. Check your email for OTP code.',
            'requires_otp': True,
            'user_id': user['id']
        }), 403
    
    if user['status'] != 'approved':
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
        return jsonify({'success': False, 'message': 'Account is not active. Please contact administrator.'}), 403
    
    # ALWAYS generate and send OTP - NO BYPASS POSSIBLE
    import random
    import time
    login_otp = str(random.randint(100000, 999999))
    otp_expires = int(time.time()) + 300  # 5 minutes
    
    # Store OTP in database
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
        
        print(f"Login OTP sent to {user['email']}")
        
    except Exception as e:
        print(f"Login OTP send error: {e}")
        return jsonify({'success': False, 'message': 'Failed to send login OTP'}), 500
    
    return jsonify({
        'success': False,  # NOT success - need OTP
        'step': 'otp_required',
        'message': f'🔐 Security verification required! OTP sent to {user["email"][:3]}***@{user["email"].split("@")[1]}. Please enter the 6-digit code.',
        'user_id': user['id']
    })

@auth_api.route('/login-step2', methods=['POST'])
def login_step2():
    """Step 2: Verify OTP and complete login"""
    data = request.json
    user_id = data.get('user_id')
    otp_code = data.get('otp_code')
    
    if not user_id or not otp_code:
        return jsonify({'success': False, 'message': 'User ID and OTP code required'}), 400
    
    # Get user
    user = query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Verify OTP
    import time
    current_time = int(time.time())
    
    if not user.get('login_otp'):
        return jsonify({'success': False, 'message': 'No OTP found. Please start login process again.'}), 400
    
    if user['login_otp'] != otp_code:
        return jsonify({'success': False, 'message': 'Invalid OTP code. Please check your email and try again.'}), 400
    
    if current_time > user.get('login_otp_expires', 0):
        execute_db('UPDATE users SET login_otp = NULL, login_otp_expires = NULL WHERE id = ?', (user['id'],))
        return jsonify({'success': False, 'message': 'OTP has expired. Please start login process again.'}), 400
    
    # Clear OTP after successful verification
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
    
    print(f"Login successful for user {user['username']} with OTP verification")
    
    response = make_response(jsonify({
        'success': True, 
        'message': 'Login successful with OTP verification',
        'user': {'id': user['id'], 'username': user['username'], 'email': user['email'] or ''},
        'session_timeout': 1800
    }))
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@auth_api.route('/login', methods=['POST'])
def login():
    """Simplified single-step login with MANDATORY OTP"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    otp_code = data.get('otp_code')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    # Get user
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if not user or not verify_password(password, user['password']):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    # Check user status
    if not user.get('otp_verified', 0):
        return jsonify({
            'success': False, 
            'message': 'Please verify your email first. Check your email for OTP code.',
            'requires_otp': True,
            'user_id': user['id']
        }), 403
    
    if user['status'] != 'approved':
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
        return jsonify({'success': False, 'message': 'Account is not active. Please contact administrator.'}), 403
    
    # MANDATORY OTP CHECK - NO BYPASS
    if not otp_code:
        # Generate fresh OTP every time
        import random
        import time
        login_otp = str(random.randint(100000, 999999))
        otp_expires = int(time.time()) + 300  # 5 minutes
        
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
            
            print(f"Login OTP sent to {user['email']}")
            
        except Exception as e:
            print(f"Login OTP send error: {e}")
            return jsonify({'success': False, 'message': 'Failed to send login OTP'}), 500
        
        # NEVER return success without OTP
        return jsonify({
            'success': False,
            'otp_required': True,
            'message': f'🔐 Security verification required! OTP sent to {user["email"][:3]}***@{user["email"].split("@")[1]}. Please enter the 6-digit code.',
            'user_id': user['id']
        })
    
    # Verify OTP - STRICT VALIDATION
    import time
    current_time = int(time.time())
    
    # Get fresh user data
    user = query_db('SELECT * FROM users WHERE id = ?', [user['id']], one=True)
    
    if not user.get('login_otp'):
        return jsonify({'success': False, 'message': 'No OTP found. Please request a new login code.'}), 400
    
    if user['login_otp'] != otp_code:
        return jsonify({'success': False, 'message': 'Invalid OTP code. Please check your email and try again.'}), 400
    
    if current_time > user.get('login_otp_expires', 0):
        execute_db('UPDATE users SET login_otp = NULL, login_otp_expires = NULL WHERE id = ?', (user['id'],))
        return jsonify({'success': False, 'message': 'OTP has expired. Please login again to get a new code.'}), 400
    
    print(f"OTP VALIDATION SUCCESS for user {user['username']}")
    
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
    
    print(f"LOGIN COMPLETED: User {user['username']} successfully logged in with OTP verification")
    
    response = make_response(jsonify({
        'success': True, 
        'message': 'Login successful with OTP verification',
        'user': {'id': user['id'], 'username': user['username'], 'email': user['email'] or ''},
        'session_timeout': 1800
    }))
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@auth_api.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_api.route('/me', methods=['GET'])
def get_current_user():
    print(f"Session data: {dict(session)}")  # Debug logging
    
    if 'user_id' not in session:
        print("No user_id in session")
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    # Check session timeout (30 minutes)
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
            print(f"User {session['user_id']} not found in database")
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Update last activity time
        session['last_activity'] = current_time
        
        response = make_response(jsonify({
            'success': True,
            'user': {'id': user['id'], 'username': user['username'], 'email': user['email'] or ''},
            'session_remaining': session_timeout - (current_time - login_time)
        }))
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    except Exception as e:
        print(f"Error in get_current_user: {e}")
        return jsonify({'success': False, 'message': 'Database error'}), 500