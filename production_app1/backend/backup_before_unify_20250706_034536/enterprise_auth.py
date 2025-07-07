"""
Enterprise Authentication System for SenderBlade
- User management with admin approval
- OTP verification (Gmail for users, in-house for admin)
- IP whitelisting and rate limiting
- Activity tracking and monitoring
"""
import sqlite3
import hashlib
import secrets
import time
import smtplib
import random
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from flask import request, session, jsonify
import json

class EnterpriseAuth:
    def __init__(self, db_path='sender.db'):
        self.db_path = db_path
        self.gmail_smtp = {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'timothykeeton.tk@gmail.com',
            'password': 'akda bgpw becv kbso'
        }
        self.init_database()
    
    def init_database(self):
        """Initialize enterprise security database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table with enterprise features
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                phone TEXT,
                status TEXT DEFAULT 'pending',  -- pending, approved, blocked, suspended
                role TEXT DEFAULT 'user',       -- user, admin, super_admin
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_at TIMESTAMP,
                approved_by INTEGER,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                failed_login_attempts INTEGER DEFAULT 0,
                last_failed_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 0,
                email_verified BOOLEAN DEFAULT 0,
                phone_verified BOOLEAN DEFAULT 0,
                two_factor_enabled BOOLEAN DEFAULT 1,
                profile_data TEXT,  -- JSON data
                notes TEXT          -- Admin notes
            )
        ''')
        
        # OTP codes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otp_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                email TEXT,
                otp_code TEXT NOT NULL,
                otp_type TEXT NOT NULL,  -- registration, login, admin_login
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                used_at TIMESTAMP,
                is_used BOOLEAN DEFAULT 0,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # IP whitelist/blacklist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ip_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                ip_type TEXT NOT NULL,     -- whitelist, blacklist, suspicious
                reason TEXT,
                added_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (added_by) REFERENCES users (id)
            )
        ''')
        
        # Activity logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT NOT NULL,  -- login, logout, campaign_create, etc.
                description TEXT,
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                additional_data TEXT,  -- JSON data
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Rate limiting
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT NOT NULL,  -- IP or user_id
                identifier_type TEXT NOT NULL,  -- ip, user
                action_type TEXT NOT NULL,  -- login, api_call, email_send
                attempt_count INTEGER DEFAULT 1,
                first_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                blocked_until TIMESTAMP,
                is_blocked BOOLEAN DEFAULT 0
            )
        ''')
        
        # Admin settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                description TEXT,
                updated_by INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (updated_by) REFERENCES users (id)
            )
        ''')
        
        # Insert default admin settings
        default_settings = [
            ('max_login_attempts', '5', 'Maximum failed login attempts before block'),
            ('login_block_duration', '30', 'Login block duration in minutes'),
            ('otp_expiry_minutes', '10', 'OTP code expiry time in minutes'),
            ('require_admin_approval', 'true', 'Require admin approval for new users'),
            ('enable_ip_whitelist', 'false', 'Enable IP whitelist restriction'),
            ('max_api_calls_per_hour', '1000', 'Maximum API calls per hour per user'),
            ('session_timeout_minutes', '120', 'Session timeout in minutes'),
            ('enable_two_factor', 'true', 'Require 2FA for all users'),
        ]
        
        for setting in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO admin_settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            ''', setting)
        
        conn.commit()
        conn.close()
    
    def register_user(self, username, email, password, full_name, phone=None):
        """Register new user (requires admin approval)"""
        try:
            # Check if user exists
            if self.user_exists(username, email):
                return {'success': False, 'message': 'User already exists'}
            
            # Generate OTP for email verification
            otp_code = self.generate_otp()
            
            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert user (pending approval)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, phone, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            ''', (username, email, password_hash, full_name, phone))
            
            user_id = cursor.lastrowid
            
            # Insert OTP code
            expires_at = datetime.now() + timedelta(minutes=10)
            cursor.execute('''
                INSERT INTO otp_codes (user_id, email, otp_code, otp_type, expires_at, ip_address)
                VALUES (?, ?, ?, 'registration', ?, ?)
            ''', (user_id, email, otp_code, expires_at, request.remote_addr if request else ''))
            
            conn.commit()
            conn.close()
            
            # Send OTP via Gmail
            if self.send_user_otp(email, otp_code, 'registration'):
                # Log activity
                self.log_activity(user_id, 'user_registration', f'User {username} registered, pending approval')
                
                return {
                    'success': True, 
                    'message': 'Registration successful. Please verify your email with the OTP sent.',
                    'user_id': user_id,
                    'requires_approval': True
                }
            else:
                return {'success': False, 'message': 'Failed to send verification email'}
                
        except Exception as e:
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
    
    def verify_registration_otp(self, email, otp_code):
        """Verify OTP for user registration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check OTP
            cursor.execute('''
                SELECT o.id, o.user_id, u.username FROM otp_codes o
                JOIN users u ON o.user_id = u.id
                WHERE o.email = ? AND o.otp_code = ? AND o.otp_type = 'registration'
                AND o.is_used = 0 AND o.expires_at > datetime('now')
            ''', (email, otp_code))
            
            result = cursor.fetchone()
            if not result:
                return {'success': False, 'message': 'Invalid or expired OTP'}
            
            otp_id, user_id, username = result
            
            # Mark OTP as used
            cursor.execute('''
                UPDATE otp_codes SET is_used = 1, used_at = datetime('now')
                WHERE id = ?
            ''', (otp_id,))
            
            # Mark email as verified
            cursor.execute('''
                UPDATE users SET email_verified = 1 WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            # Log activity
            self.log_activity(user_id, 'email_verification', f'Email verified for {username}')
            
            return {
                'success': True, 
                'message': 'Email verified successfully. Your account is pending admin approval.',
                'user_id': user_id
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Verification failed: {str(e)}'}
    
    def admin_login(self, username, password):
        """Admin login with in-house OTP"""
        try:
            # Check credentials
            user = self.authenticate_user(username, password)
            if not user or user['role'] not in ['admin', 'super_admin']:
                return {'success': False, 'message': 'Invalid admin credentials'}
            
            # Generate in-house OTP (no external email)
            admin_otp = self.generate_admin_otp()
            
            # Store OTP in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(minutes=5)  # 5 min for admin
            cursor.execute('''
                INSERT INTO otp_codes (user_id, email, otp_code, otp_type, expires_at, ip_address)
                VALUES (?, ?, ?, 'admin_login', ?, ?)
            ''', (user['id'], user['email'], admin_otp, expires_at, request.remote_addr if request else ''))
            
            conn.commit()
            conn.close()
            
            # Log activity
            self.log_activity(user['id'], 'admin_login_attempt', f'Admin {username} requested login OTP')
            
            return {
                'success': True,
                'message': f'Admin OTP generated: {admin_otp}',
                'otp_code': admin_otp,  # Show directly (in-house)
                'user_id': user['id'],
                'expires_in': 5
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Admin login failed: {str(e)}'}
    
    def verify_admin_otp(self, user_id, otp_code):
        """Verify admin OTP and complete login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check admin OTP
            cursor.execute('''
                SELECT o.id, u.username, u.role FROM otp_codes o
                JOIN users u ON o.user_id = u.id
                WHERE o.user_id = ? AND o.otp_code = ? AND o.otp_type = 'admin_login'
                AND o.is_used = 0 AND o.expires_at > datetime('now')
            ''', (user_id, otp_code))
            
            result = cursor.fetchone()
            if not result:
                return {'success': False, 'message': 'Invalid or expired admin OTP'}
            
            otp_id, username, role = result
            
            # Mark OTP as used
            cursor.execute('''
                UPDATE otp_codes SET is_used = 1, used_at = datetime('now')
                WHERE id = ?
            ''', (otp_id,))
            
            # Update user login info
            cursor.execute('''
                UPDATE users SET last_login = datetime('now'), login_count = login_count + 1
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            # Create admin session
            session_token = secrets.token_urlsafe(32)
            session['user_id'] = user_id
            session['username'] = username
            session['role'] = role
            session['session_token'] = session_token
            session['login_time'] = time.time()
            
            # Log successful admin login
            self.log_activity(user_id, 'admin_login_success', f'Admin {username} logged in successfully')
            
            return {
                'success': True,
                'message': 'Admin login successful',
                'user_id': user_id,
                'username': username,
                'role': role,
                'session_token': session_token
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Admin OTP verification failed: {str(e)}'}
    
    def get_all_users(self, admin_user_id):
        """Get all users for admin dashboard"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, full_name, phone, status, role, created_at,
                       last_login, login_count, email_verified, is_active, notes
                FROM users ORDER BY created_at DESC
            ''')
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'full_name': row[3],
                    'phone': row[4],
                    'status': row[5],
                    'role': row[6],
                    'created_at': row[7],
                    'last_login': row[8],
                    'login_count': row[9],
                    'email_verified': row[10],
                    'is_active': row[11],
                    'notes': row[12]
                })
            
            conn.close()
            
            # Log admin activity
            self.log_activity(admin_user_id, 'view_all_users', 'Admin viewed all users')
            
            return {'success': True, 'users': users}
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get users: {str(e)}'}
    
    def approve_user(self, admin_user_id, user_id, notes=None):
        """Admin approve user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update user status
            cursor.execute('''
                UPDATE users SET status = 'approved', is_active = 1, 
                       approved_at = datetime('now'), approved_by = ?, notes = ?
                WHERE id = ? AND status = 'pending'
            ''', (admin_user_id, notes, user_id))
            
            if cursor.rowcount == 0:
                return {'success': False, 'message': 'User not found or already processed'}
            
            # Get user info
            cursor.execute('SELECT username, email FROM users WHERE id = ?', (user_id,))
            user_info = cursor.fetchone()
            
            conn.commit()
            conn.close()
            
            if user_info:
                username, email = user_info
                
                # Send approval email
                self.send_approval_email(email, username)
                
                # Log activity
                self.log_activity(admin_user_id, 'user_approval', f'Approved user {username} (ID: {user_id})')
                
                return {'success': True, 'message': f'User {username} approved successfully'}
            
            return {'success': False, 'message': 'User not found'}
            
        except Exception as e:
            return {'success': False, 'message': f'Approval failed: {str(e)}'}
    
    def block_user(self, admin_user_id, user_id, reason=None):
        """Admin block user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update user status
            cursor.execute('''
                UPDATE users SET status = 'blocked', is_active = 0, notes = ?
                WHERE id = ?
            ''', (reason, user_id))
            
            # Get user info
            cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            
            conn.commit()
            conn.close()
            
            if result:
                username = result[0]
                
                # Log activity
                self.log_activity(admin_user_id, 'user_blocked', f'Blocked user {username} (ID: {user_id}). Reason: {reason}')
                
                return {'success': True, 'message': f'User {username} blocked successfully'}
            
            return {'success': False, 'message': 'User not found'}
            
        except Exception as e:
            return {'success': False, 'message': f'Block failed: {str(e)}'}
    
    def delete_user(self, admin_user_id, user_id):
        """Admin delete user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user info before deletion
            cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return {'success': False, 'message': 'User not found'}
            
            username = result[0]
            
            # Delete user and related data
            cursor.execute('DELETE FROM otp_codes WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM user_activity WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            # Log activity
            self.log_activity(admin_user_id, 'user_deleted', f'Deleted user {username} (ID: {user_id})')
            
            return {'success': True, 'message': f'User {username} deleted successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Deletion failed: {str(e)}'}
    
    def get_user_activity(self, admin_user_id, user_id=None, limit=100):
        """Get user activity logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT ua.*, u.username FROM user_activity ua
                    JOIN users u ON ua.user_id = u.id
                    WHERE ua.user_id = ?
                    ORDER BY ua.created_at DESC LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT ua.*, u.username FROM user_activity ua
                    JOIN users u ON ua.user_id = u.id
                    ORDER BY ua.created_at DESC LIMIT ?
                ''', (limit,))
            
            activities = []
            for row in cursor.fetchall():
                activities.append({
                    'id': row[0],
                    'user_id': row[1],
                    'activity_type': row[2],
                    'description': row[3],
                    'ip_address': row[4],
                    'user_agent': row[5],
                    'session_id': row[6],
                    'additional_data': row[7],
                    'created_at': row[8],
                    'username': row[9]
                })
            
            conn.close()
            
            # Log admin activity
            self.log_activity(admin_user_id, 'view_user_activity', f'Admin viewed user activity logs')
            
            return {'success': True, 'activities': activities}
            
        except Exception as e:
            return {'success': False, 'message': f'Failed to get activity: {str(e)}'}
    
    def generate_otp(self):
        """Generate 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    def generate_admin_otp(self):
        """Generate 8-digit admin OTP"""
        return ''.join(random.choices(string.digits, k=8))
    
    def send_user_otp(self, email, otp_code, otp_type):
        """Send OTP via Gmail"""
        try:
            subject = f"SenderBlade - Your OTP Code"
            
            if otp_type == 'registration':
                body = f"""
Welcome to SenderBlade!

Your verification code is: {otp_code}

This code will expire in 10 minutes.

Please enter this code to verify your email address.

Best regards,
SenderBlade Team
"""
            else:
                body = f"""
Your SenderBlade login code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
SenderBlade Team
"""
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.gmail_smtp['username']
            msg['To'] = email
            
            with smtplib.SMTP(self.gmail_smtp['host'], self.gmail_smtp['port']) as server:
                server.starttls()
                server.login(self.gmail_smtp['username'], self.gmail_smtp['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send OTP email: {e}")
            return False
    
    def send_approval_email(self, email, username):
        """Send account approval email"""
        try:
            subject = "SenderBlade - Account Approved!"
            body = f"""
Hello {username},

Great news! Your SenderBlade account has been approved by our admin team.

You can now log in and start using all features of SenderBlade.

Login at: https://your-domain.com/login

Best regards,
SenderBlade Team
"""
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.gmail_smtp['username']
            msg['To'] = email
            
            with smtplib.SMTP(self.gmail_smtp['host'], self.gmail_smtp['port']) as server:
                server.starttls()
                server.login(self.gmail_smtp['username'], self.gmail_smtp['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send approval email: {e}")
            return False
    
    def user_exists(self, username, email):
        """Check if user already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM users WHERE username = ? OR email = ?
        ''', (username, email))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, role, status, is_active
            FROM users WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'role': result[3],
                'status': result[4],
                'is_active': result[5]
            }
        
        return None
    
    def log_activity(self, user_id, activity_type, description, additional_data=None):
        """Log user activity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_activity (user_id, activity_type, description, 
                                         ip_address, user_agent, additional_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id, 
                activity_type, 
                description,
                request.remote_addr if request else '',
                request.headers.get('User-Agent', '') if request else '',
                json.dumps(additional_data) if additional_data else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to log activity: {e}")

# Global auth instance
enterprise_auth = EnterpriseAuth()