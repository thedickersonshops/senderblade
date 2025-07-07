"""
Proxy API - Handles all proxy operations
"""
import sqlite3
import requests
from flask import Blueprint, request, jsonify, g

# Create blueprint
proxy_api = Blueprint('proxy_api', __name__)

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

# Proxy routes
@proxy_api.route('/proxies', methods=['GET'])
def get_proxies():
    proxies = query_db('SELECT * FROM proxies')
    result = []
    for proxy in proxies:
        result.append({
            'id': proxy['id'],
            'host': proxy['host'],
            'port': proxy['port'],
            'username': proxy['username'],
            'proxy_type': proxy['proxy_type'],
            'status': proxy['status'],
            'created_at': proxy['created_at']
        })
    return jsonify({'success': True, 'data': result})

@proxy_api.route('/proxies', methods=['POST'])
def add_proxy():
    data = request.json
    host = data.get('host')
    port = data.get('port')
    username = data.get('username', '')
    password = data.get('password', '')
    proxy_type = data.get('proxy_type', 'http')
    
    if not host or not port:
        return jsonify({'success': False, 'message': 'Host and port are required'}), 400
    
    # Test connection first
    test_result = test_proxy_connection(host, port, proxy_type, username, password)
    if not test_result['success']:
        return jsonify(test_result), 400
    
    proxy_id = execute_db(
        'INSERT INTO proxies (host, port, username, password, proxy_type) VALUES (?, ?, ?, ?, ?)',
        (host, port, username, password, proxy_type)
    )
    
    return jsonify({
        'success': True,
        'data': {
            'id': proxy_id,
            'host': host,
            'port': port,
            'username': username,
            'proxy_type': proxy_type,
            'status': 'active'
        },
        'message': 'Proxy added successfully'
    })

@proxy_api.route('/proxies/<int:proxy_id>', methods=['DELETE'])
def delete_proxy(proxy_id):
    # Check if proxy exists
    proxy = query_db('SELECT * FROM proxies WHERE id = ?', [proxy_id], one=True)
    if not proxy:
        return jsonify({'success': False, 'message': 'Proxy not found'}), 404
    
    # Delete proxy
    execute_db('DELETE FROM proxies WHERE id = ?', [proxy_id])
    
    return jsonify({'success': True, 'message': 'Proxy deleted successfully'})

@proxy_api.route('/proxy/test', methods=['POST'])
def test_proxy():
    data = request.json
    host = data.get('host')
    port = data.get('port')
    username = data.get('username', '')
    password = data.get('password', '')
    proxy_type = data.get('proxy_type', 'http')
    
    if not host or not port:
        return jsonify({'success': False, 'message': 'Host and port are required'}), 400
    
    result = test_proxy_connection(host, port, proxy_type, username, password)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

# Helper function to test proxy connection
def test_proxy_connection(host, port, proxy_type, username='', password=''):
    try:
        # Format proxy URL
        proxy_url = f"{proxy_type}://"
        if username and password:
            proxy_url += f"{username}:{password}@"
        proxy_url += f"{host}:{port}"
        
        # Set up proxies
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        # Test connection with a request to ipinfo.io
        response = requests.get('https://ipinfo.io/json', proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            ip = data.get('ip', 'Unknown')
            
            return {
                'success': True,
                'data': {
                    'status': 'success',
                    'message': 'Proxy connection successful',
                    'ip': ip
                }
            }
        else:
            return {
                'success': False,
                'message': f'Proxy connection failed: HTTP {response.status_code}'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Proxy connection failed: {str(e)}'
        }