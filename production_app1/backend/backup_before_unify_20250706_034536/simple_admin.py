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
        
        self.otp_storage = {}  # Store OTP codes temporarily
    
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
        
        # Store OTP with expiration
        self.otp_storage[email] = {
            'otp': otp_code,
            'expires': time.time() + 600,  # 10 minutes
            'attempts': 0
        }
        
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
        if email.lower() not in self.otp_storage:
            return {'success': False, 'message': 'No OTP request found'}
        
        stored_data = self.otp_storage[email.lower()]
        
        # Check expiration
        if time.time() > stored_data['expires']:
            del self.otp_storage[email.lower()]
            return {'success': False, 'message': 'OTP expired'}
        
        # Check attempts
        if stored_data['attempts'] >= 3:
            del self.otp_storage[email.lower()]
            return {'success': False, 'message': 'Too many failed attempts'}
        
        # Verify OTP
        if otp_code == stored_data['otp']:
            del self.otp_storage[email.lower()]
            return {
                'success': True,
                'message': 'Admin login successful',
                'admin_email': email,
                'role': 'admin'
            }
        else:
            stored_data['attempts'] += 1
            return {'success': False, 'message': 'Invalid OTP code'}
    
    def get_admin_email(self):
        """Get current admin email"""
        return self.ADMIN_EMAIL
    
    def update_admin_email(self, new_email):
        """Update admin email"""
        self.ADMIN_EMAIL = new_email
        return {'success': True, 'message': f'Admin email updated to {new_email}'}

# Global admin instance
simple_admin = SimpleAdmin()