"""
Admin Routes for SenderBlade - Complete Admin System
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from enterprise_auth import enterprise_auth
import time

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login with in-house OTP"""
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Attempt admin login
        result = enterprise_auth.admin_login(username, password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'otp_code': result['otp_code'],
                'user_id': result['user_id'],
                'expires_in': result['expires_in']
            })
        else:
            return jsonify({'success': False, 'message': result['message']})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login error: {str(e)}'})

@admin_bp.route('/verify-otp', methods=['POST'])
def verify_admin_otp():
    """Verify admin OTP and complete login"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        otp_code = data.get('otp_code')
        
        result = enterprise_auth.verify_admin_otp(user_id, otp_code)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Admin login successful',
                'redirect': '/admin/dashboard'
            })
        else:
            return jsonify({'success': False, 'message': result['message']})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'OTP verification error: {str(e)}'})

@admin_bp.route('/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'super_admin']:
        return redirect('/admin/login')
    
    try:
        # Get dashboard stats
        users_result = enterprise_auth.get_all_users(session['user_id'])
        activity_result = enterprise_auth.get_user_activity(session['user_id'], limit=50)
        
        stats = {
            'total_users': len(users_result.get('users', [])) if users_result['success'] else 0,
            'pending_users': len([u for u in users_result.get('users', []) if u['status'] == 'pending']) if users_result['success'] else 0,
            'active_users': len([u for u in users_result.get('users', []) if u['is_active']]) if users_result['success'] else 0,
            'recent_activities': activity_result.get('activities', [])[:10] if activity_result['success'] else []
        }
        
        return render_template('admin_dashboard.html', stats=stats)
        
    except Exception as e:
        return f"Dashboard error: {str(e)}"

@admin_bp.route('/users')
def admin_users():
    """User management page"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'super_admin']:
        return redirect('/admin/login')
    
    try:
        result = enterprise_auth.get_all_users(session['user_id'])
        
        if result['success']:
            return render_template('admin_users.html', users=result['users'])
        else:
            return f"Error loading users: {result['message']}"
            
    except Exception as e:
        return f"Users page error: {str(e)}"

@admin_bp.route('/approve-user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    """Approve user account"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'super_admin']:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json() or {}
        notes = data.get('notes', '')
        
        result = enterprise_auth.approve_user(session['user_id'], user_id, notes)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Approval error: {str(e)}'})

@admin_bp.route('/block-user/<int:user_id>', methods=['POST'])
def block_user(user_id):
    """Block user account"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'super_admin']:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Blocked by admin')
        
        result = enterprise_auth.block_user(session['user_id'], user_id, reason)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Block error: {str(e)}'})

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete user account"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'super_admin']:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        result = enterprise_auth.delete_user(session['user_id'], user_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Delete error: {str(e)}'})

@admin_bp.route('/activity')
def admin_activity():
    """Activity monitoring page"""
    if 'user_id' not in session or session.get('role') not in ['admin', 'super_admin']:
        return redirect('/admin/login')
    
    try:
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', 100, type=int)
        
        result = enterprise_auth.get_user_activity(session['user_id'], user_id, limit)
        
        if result['success']:
            return render_template('admin_activity.html', activities=result['activities'])
        else:
            return f"Error loading activity: {result['message']}"
            
    except Exception as e:
        return f"Activity page error: {str(e)}"

@admin_bp.route('/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect('/admin/login')