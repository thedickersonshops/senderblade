"""
Admin API - Handles admin authentication via OTP
"""
from flask import Blueprint, request, jsonify, session
from simple_admin import simple_admin
import time

# Create blueprint
admin_api = Blueprint('admin_api', __name__)

@admin_api.route('/admin/request-otp', methods=['POST'])
def request_admin_otp():
    """Request OTP for admin login"""
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    
    result = simple_admin.request_admin_login(email)
    return jsonify(result)

@admin_api.route('/admin/verify-otp', methods=['POST'])
def verify_admin_otp():
    """Verify admin OTP"""
    data = request.json
    email = data.get('email')
    otp_code = data.get('otp_code')
    
    if not email or not otp_code:
        return jsonify({'success': False, 'message': 'Email and OTP code are required'}), 400
    
    result = simple_admin.verify_admin_otp(email, otp_code)
    if result['success']:
        # Set admin session
        session['admin_email'] = email
        session['role'] = 'admin'
        session['login_time'] = time.time()
    return jsonify(result)

@admin_api.route('/admin/info', methods=['GET'])
def get_admin_info():
    """Get admin information"""
    return jsonify({
        'success': True,
        'admin_email': simple_admin.get_admin_email()
    })