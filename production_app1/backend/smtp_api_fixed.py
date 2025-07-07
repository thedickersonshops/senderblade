"""
SMTP API - Handles all SMTP server operations
"""
import os
import sqlite3
from flask import Blueprint, request, jsonify, g
import smtplib
import ssl

# Create blueprint
smtp_api = Blueprint('smtp_api', __name__)

# Import database helper functions
from simple_db import query_db as simple_query_db, execute_db as simple_execute_db

# Override to use sender.db (same as lists and campaigns)
def query_db(query, args=(), one=False):
    return simple_query_db(query, args, one, 'sender.db')

def execute_db(query, args=()):
    return simple_execute_db(query, args, 'sender.db')

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
    
    require_auth = data.get('require_auth', True)
    
    if not name or not host or not port:
        return jsonify({'success': False, 'message': 'Name, host, and port are required'}), 400
    
    if require_auth and (not username or not password):
        return jsonify({'success': False, 'message': 'Username and password required when authentication is enabled'}), 400
    
    # Check for duplicates
    existing = query_db('SELECT * FROM smtp_servers WHERE host = ? AND port = ? AND username = ?', 
                       [host, port, username], one=True)
    if existing:
        return jsonify({'success': False, 'message': 'SMTP server with same host, port, and username already exists'}), 400
    
    # Test connection first
    test_result = test_smtp_connection(host, port, username, password, require_auth)
    if not test_result['success']:
        return jsonify(test_result), 400
    
    server_id = execute_db(
        'INSERT INTO smtp_servers (name, host, port, username, password, from_email, from_name, max_emails_per_day, require_auth) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (name, host, port, username, password, from_email, from_name, max_emails_per_day, require_auth)
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
    require_auth = data.get('require_auth', True)
    server_id = data.get('server_id')
    
    # If server_id is provided, get server details from database
    if server_id and not (host and port):
        server = query_db('SELECT * FROM smtp_servers WHERE id = ?', [server_id], one=True)
        if not server:
            return jsonify({'success': False, 'message': 'SMTP server not found'}), 404
        
        host = server['host']
        port = server['port']
        username = server['username']
        password = server['password']
        require_auth = server.get('require_auth', True)
    
    if not host or not port:
        return jsonify({'success': False, 'message': 'Host and port are required'}), 400
    
    if require_auth and (not username or not password):
        return jsonify({'success': False, 'message': 'Username and password required when authentication is enabled'}), 400
    
    result = test_smtp_connection(host, port, username, password, require_auth)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

# Helper function to test SMTP connection
def test_smtp_connection(host, port, username, password, require_auth=True):
    try:
        # Validate input
        if not host or not port:
            return {
                'success': False,
                'message': 'Host and port are required'
            }
        
        if require_auth and (not username or not password):
            return {
                'success': False,
                'message': 'Username and password required when authentication is enabled'
            }
            
        # Simple validation
        try:
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                return {
                    'success': False,
                    'message': 'Port must be between 1 and 65535'
                }
        except ValueError:
            return {
                'success': False,
                'message': 'Port must be a number'
            }
            
        # Test real SMTP connection
        try:
            # Create SSL context that doesn't verify certificates (for testing)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            if int(port) == 465:
                # SSL connection
                with smtplib.SMTP_SSL(host, port, context=context, timeout=10) as server:
                    # Always test basic connectivity
                    server.ehlo()
                    
                    # Test authentication if required
                    if require_auth:
                        server.login(username, password)
                        auth_status = "Authentication successful"
                    else:
                        auth_status = "No authentication required"
            else:
                # STARTTLS connection
                with smtplib.SMTP(host, port, timeout=10) as server:
                    # Always test basic connectivity
                    server.ehlo()
                    
                    # Setup encryption if available
                    if server.has_extn('STARTTLS'):
                        server.starttls(context=context)
                        server.ehlo()
                    
                    # Test authentication if required
                    if require_auth:
                        server.login(username, password)
                        auth_status = "Authentication successful"
                    else:
                        auth_status = "Server alive, no authentication required"
            
            return {
                'success': True,
                'data': {
                    'status': 'success',
                    'message': f'SMTP connection successful - {auth_status}',
                    'server_alive': True,
                    'authentication_tested': require_auth
                }
            }
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': 'Authentication failed - invalid username or password'
            }
        except smtplib.SMTPConnectError:
            return {
                'success': False,
                'message': 'Cannot connect to SMTP server'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'SMTP connection failed: {str(e)}'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'SMTP connection failed: {str(e)}'
        }