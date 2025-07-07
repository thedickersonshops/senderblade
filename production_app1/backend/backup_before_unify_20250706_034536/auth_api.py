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

# Import database helper functions
from simple_db import query_db as simple_query_db, execute_db as simple_execute_db

# Override to use sender.db
def query_db(query, args=(), one=False):
    return simple_query_db(query, args, one, 'sender.db')

def execute_db(query, args=()):
    return simple_execute_db(query, args, 'sender.db')

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
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    # Check if user exists
    existing = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if existing:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    # Create user
    hashed_password = hash_password(password)
    user_id = execute_db(
        'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
        (username, hashed_password, email or '')
    )
    
    return jsonify({'success': True, 'message': 'User registered successfully'})

@auth_api.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    # Get user
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if not user or not verify_password(password, user['password']):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    # Set session
    session['user_id'] = user['id']
    session['username'] = user['username']
    session.permanent = True
    
    print(f"Login successful for user {user['username']}, session: {dict(session)}")  # Debug
    
    response = make_response(jsonify({
        'success': True, 
        'message': 'Login successful',
        'user': {'id': user['id'], 'username': user['username'], 'email': user['email'] or ''}
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
    
    try:
        user = query_db('SELECT id, username, email FROM users WHERE id = ?', [session['user_id']], one=True)
        if not user:
            print(f"User {session['user_id']} not found in database")
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        response = make_response(jsonify({
            'success': True,
            'user': {'id': user['id'], 'username': user['username'], 'email': user['email'] or ''}
        }))
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
    except Exception as e:
        print(f"Error in get_current_user: {e}")
        return jsonify({'success': False, 'message': 'Database error'}), 500