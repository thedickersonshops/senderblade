"""
Simple Admin System - Email + OTP Only
Admin Email: emmanueldickerson757@icloud.com
"""
import smtplib
import random
import string
import time
import sqlite3
from email.mime.text import MIMEText

class SimpleAdmin:
    def __init__(self):
        # ADMIN EMAIL - CHANGE THIS TO UPDATE ADMIN EMAIL
        self.ADMIN_EMAIL = "emmanueldickerson757@icloud.com"
        
        # Gmail SMTP for sending OTP
        self.gmail_smtp = {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'timothykeeton.tk@gmail.com',
            'password': 'akda bgpw becv kbso'
        }
        
        # Use database instead of memory for OTP storage
        self.init_admin_db()
    
    def init_admin_db(self):
        """Initialize admin OTP table in database"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_otp (
                    email TEXT PRIMARY KEY,
                    otp_code TEXT,
                    expires INTEGER,
                    attempts INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Admin DB init error: {e}")
    
    def generate_otp(self):
        """Generate 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_otp_email(self, email, otp_code):
        """Send OTP via email"""
        try:
            subject = "SenderBlade Admin Login - OTP Code"
            body = f"""
Your SenderBlade Admin OTP Code: {otp_code}

This code expires in 10 minutes.

If you didn't request this, please ignore this email.

- SenderBlade Security Team
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
    
    def request_admin_login(self, email):
        """Request admin login - generates and sends OTP"""
        if email.lower() != self.ADMIN_EMAIL.lower():
            return {'success': False, 'message': 'Invalid admin email'}
        
        # Generate OTP
        otp_code = self.generate_otp()
        
        # Store OTP in database with expiration
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO admin_otp (email, otp_code, expires, attempts)
                VALUES (?, ?, ?, 0)
            ''', (email.lower(), otp_code, int(time.time() + 600)))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"OTP storage error: {e}")
            return {'success': False, 'message': 'Failed to store OTP'}
        
        # Send OTP email
        if self.send_otp_email(email, otp_code):
            return {
                'success': True,
                'message': 'OTP sent to your email',
                'expires_in': 10
            }
        else:
            return {'success': False, 'message': 'Failed to send OTP email'}
    
    def verify_admin_otp(self, email, otp_code):
        """Verify admin OTP"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Get stored OTP data
            cursor.execute('SELECT otp_code, expires, attempts FROM admin_otp WHERE email = ?', (email.lower(),))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return {'success': False, 'message': 'No OTP request found'}
            
            stored_otp, expires, attempts = result
            
            # Check expiration
            if time.time() > expires:
                cursor.execute('DELETE FROM admin_otp WHERE email = ?', (email.lower(),))
                conn.commit()
                conn.close()
                return {'success': False, 'message': 'OTP expired'}
            
            # Check attempts
            if attempts >= 3:
                cursor.execute('DELETE FROM admin_otp WHERE email = ?', (email.lower(),))
                conn.commit()
                conn.close()
                return {'success': False, 'message': 'Too many failed attempts'}
            
            # Verify OTP
            if otp_code == stored_otp:
                cursor.execute('DELETE FROM admin_otp WHERE email = ?', (email.lower(),))
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'Admin login successful',
                    'admin_email': email,
                    'role': 'admin'
                }
            else:
                cursor.execute('UPDATE admin_otp SET attempts = attempts + 1 WHERE email = ?', (email.lower(),))
                conn.commit()
                conn.close()
                return {'success': False, 'message': 'Invalid OTP code'}
                
        except Exception as e:
            print(f"OTP verification error: {e}")
            return {'success': False, 'message': 'Database error during OTP verification'}
    
    def get_admin_email(self):
        """Get current admin email"""
        return self.ADMIN_EMAIL
    
    def update_admin_email(self, new_email):
        """Update admin email"""
        self.ADMIN_EMAIL = new_email
        return {'success': True, 'message': f'Admin email updated to {new_email}'}

# Global admin instance
simple_admin = SimpleAdmin()