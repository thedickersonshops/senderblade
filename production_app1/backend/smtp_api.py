"""
SMTP API - Handles all SMTP server operations
"""
import sqlite3
from flask import Blueprint, request, jsonify, g
import smtplib
import ssl

# Create blueprint
smtp_api = Blueprint('smtp_api', __name__)

# Database helper functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id

# SMTP routes
@smtp_api.route('/smtp', methods=['GET'])
def get_smtp_servers():
    servers = query_db('SELECT * FROM smtp_servers')
    result = []
    for server in servers:
        result.append({
            'id': server['id'],
            'name': server['name'],
            'host': server['host'],
            'port': server['port'],
            'username': server['username'],
            'from_email': server['from_email'],
            'from_name': server['from_name'],
            'max_emails_per_day': server['max_emails_per_day'],
            'current_count': server['current_count'],
            'status': server['status'],
            'created_at': server['created_at']
        })
    return jsonify({'success': True, 'data': result})

@smtp_api.route('/smtp', methods=['POST'])
def add_smtp_server():
    data = request.json
    name = data.get('name')
    host = data.get('host')
    port = data.get('port')
    username = data.get('username')
    password = data.get('password')
    from_email = data.get('from_email')
    from_name = data.get('from_name', '')
    max_emails_per_day = data.get('max_emails_per_day', 500)
    
    if not name or not host or not port or not username or not password or not from_email:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Test connection first
    test_result = test_smtp_connection(host, port, username, password)
    if not test_result['success']:
        return jsonify(test_result), 400
    
    server_id = execute_db(
        'INSERT INTO smtp_servers (name, host, port, username, password, from_email, from_name, max_emails_per_day) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (name, host, port, username, password, from_email, from_name, max_emails_per_day)
    )
    
    return jsonify({
        'success': True,
        'data': {
            'id': server_id,
            'name': name,
            'host': host,
            'port': port,
            'username': username,
            'from_email': from_email,
            'from_name': from_name,
            'max_emails_per_day': max_emails_per_day,
            'current_count': 0,
            'status': 'active'
        },
        'message': 'SMTP server added successfully'
    })

@smtp_api.route('/smtp/<int:server_id>', methods=['DELETE'])
def delete_smtp_server(server_id):
    # Check if server exists
    server = query_db('SELECT * FROM smtp_servers WHERE id = ?', [server_id], one=True)
    if not server:
        return jsonify({'success': False, 'message': 'SMTP server not found'}), 404
    
    # Delete server
    execute_db('DELETE FROM smtp_servers WHERE id = ?', [server_id])
    
    return jsonify({'success': True, 'message': 'SMTP server deleted successfully'})

@smtp_api.route('/smtp/test', methods=['POST'])
def test_smtp():
    data = request.json
    host = data.get('host')
    port = data.get('port')
    username = data.get('username')
    password = data.get('password')
    
    if not host or not port or not username or not password:
        return jsonify({'success': False, 'message': 'Host, port, username, and password are required'}), 400
    
    result = test_smtp_connection(host, port, username, password)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

# Helper function to test SMTP connection
def test_smtp_connection(host, port, username, password):
    try:
        # Create a secure SSL context
        context = ssl.create_default_context()
        
        # Try to connect to the SMTP server
        with smtplib.SMTP(host, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(username, password)
        
        return {
            'success': True,
            'data': {
                'status': 'success',
                'message': 'SMTP connection successful'
            }
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'SMTP connection failed: {str(e)}'
        }