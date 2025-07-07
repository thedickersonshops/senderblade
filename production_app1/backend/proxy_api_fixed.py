"""
Proxy API - Handles all proxy operations
"""
import os
import sqlite3
import requests
from flask import Blueprint, request, jsonify, g

# Create blueprint
proxy_api = Blueprint('proxy_api', __name__)

# Import database helper functions
from simple_db import query_db as simple_query_db, execute_db as simple_execute_db

# Override to use sender.db (same as lists, campaigns, and SMTP)
def query_db(query, args=(), one=False):
    return simple_query_db(query, args, one, 'sender.db')

def execute_db(query, args=()):
    return simple_execute_db(query, args, 'sender.db')

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
    
    # Check for duplicates (same host, port, type, AND credentials)
    existing = query_db('SELECT * FROM proxies WHERE host = ? AND port = ? AND proxy_type = ? AND username = ? AND password = ?', 
                       [host, port, proxy_type, username or '', password or ''], one=True)
    if existing:
        return jsonify({'success': False, 'message': 'Proxy with same host, port, type, and credentials already exists'}), 400
    
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
    proxy_id = data.get('proxy_id')
    
    # If proxy_id is provided, get proxy details from database
    if proxy_id and not (host and port):
        proxy = query_db('SELECT * FROM proxies WHERE id = ?', [proxy_id], one=True)
        if not proxy:
            return jsonify({'success': False, 'message': 'Proxy not found'}), 404
        
        host = proxy['host']
        port = proxy['port']
        username = proxy['username'] or ''
        password = proxy['password'] or ''
        proxy_type = proxy['proxy_type']
    
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
        # Validate input
        if not host or not port:
            return {
                'success': False,
                'message': 'Host and port are required'
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
            
        # Validate proxy type
        if proxy_type not in ['http', 'socks4', 'socks5']:
            return {
                'success': False,
                'message': 'Invalid proxy type'
            }
            
        # Test real proxy connection
        try:
            # Format proxy URL
            if proxy_type == 'http':
                proxy_url = f"http://"
            else:
                proxy_url = f"{proxy_type}://"
                
            if username and password:
                proxy_url += f"{username}:{password}@"
            proxy_url += f"{host}:{port}"
            
            # Set up proxies
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            
            # Test connection with a request to httpbin.org
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                ip = data.get('origin', 'Unknown')
                
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
        except requests.exceptions.ProxyError:
            return {
                'success': False,
                'message': 'Proxy connection failed - invalid proxy or credentials'
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': 'Proxy connection timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Proxy connection failed: {str(e)}'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Proxy connection failed: {str(e)}'
        }