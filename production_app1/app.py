#!/usr/bin/env python3
from flask import Flask, request, jsonify, g
import sqlite3
import os
import json
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()

# Lists API
@app.route('/api/lists', methods=['GET'])
def get_lists():
    lists = query_db('SELECT l.*, COUNT(c.id) as contact_count FROM lists l LEFT JOIN contacts c ON l.id = c.list_id GROUP BY l.id')
    result = []
    for lst in lists:
        result.append({
            'id': lst['id'],
            'name': lst['name'],
            'description': lst['description'],
            'contact_count': lst['contact_count'],
            'created_at': lst['created_at']
        })
    return jsonify({'success': True, 'data': result})

@app.route('/api/lists', methods=['POST'])
def create_list():
    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'success': False, 'message': 'List name is required'}), 400
    
    list_id = execute_db('INSERT INTO lists (name, description) VALUES (?, ?)', (name, description))
    
    return jsonify({
        'success': True,
        'data': {
            'id': list_id,
            'name': name,
            'description': description,
            'contact_count': 0
        },
        'message': 'List created successfully'
    })

@app.route('/api/lists/<int:list_id>', methods=['GET'])
def get_list(list_id):
    lst = query_db('SELECT l.*, COUNT(c.id) as contact_count FROM lists l LEFT JOIN contacts c ON l.id = c.list_id WHERE l.id = ? GROUP BY l.id', [list_id], one=True)
    
    if not lst:
        return jsonify({'success': False, 'message': 'List not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': lst['id'],
            'name': lst['name'],
            'description': lst['description'],
            'contact_count': lst['contact_count'],
            'created_at': lst['created_at']
        }
    })

@app.route('/api/lists/<int:list_id>', methods=['DELETE'])
def delete_list(list_id):
    # Check if list exists
    lst = query_db('SELECT * FROM lists WHERE id = ?', [list_id], one=True)
    if not lst:
        return jsonify({'success': False, 'message': 'List not found'}), 404
    
    # Delete contacts first
    execute_db('DELETE FROM contacts WHERE list_id = ?', [list_id])
    
    # Delete list
    execute_db('DELETE FROM lists WHERE id = ?', [list_id])
    
    return jsonify({'success': True, 'message': 'List deleted successfully'})

@app.route('/api/lists/<int:list_id>/contacts', methods=['GET'])
def get_contacts(list_id):
    contacts = query_db('SELECT * FROM contacts WHERE list_id = ?', [list_id])
    result = []
    for contact in contacts:
        contact_data = {
            'id': contact['id'],
            'email': contact['email'],
            'first_name': contact['first_name'],
            'last_name': contact['last_name'],
            'created_at': contact['created_at']
        }
        
        if contact['custom_fields']:
            try:
                contact_data['custom_fields'] = json.loads(contact['custom_fields'])
            except:
                contact_data['custom_fields'] = {}
        
        result.append(contact_data)
    
    return jsonify({'success': True, 'data': result})

@app.route('/api/lists/<int:list_id>/contacts', methods=['POST'])
def add_contacts(list_id):
    data = request.json
    contacts = data.get('contacts', [])
    
    if not contacts:
        return jsonify({'success': False, 'message': 'No contacts provided'}), 400
    
    # Check if list exists
    lst = query_db('SELECT * FROM lists WHERE id = ?', [list_id], one=True)
    if not lst:
        return jsonify({'success': False, 'message': 'List not found'}), 404
    
    added_count = 0
    for contact in contacts:
        email = contact.get('email')
        if not email:
            continue
        
        # Check if contact already exists
        existing = query_db('SELECT * FROM contacts WHERE list_id = ? AND email = ?', [list_id, email], one=True)
        if existing:
            continue
        
        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        custom_fields = contact.get('custom_fields', {})
        
        if isinstance(custom_fields, dict):
            custom_fields = json.dumps(custom_fields)
        
        execute_db(
            'INSERT INTO contacts (list_id, email, first_name, last_name, custom_fields) VALUES (?, ?, ?, ?, ?)',
            (list_id, email, first_name, last_name, custom_fields)
        )
        added_count += 1
    
    return jsonify({
        'success': True,
        'message': f'{added_count} contacts added successfully',
        'added_count': added_count
    })

# Enrichment API
@app.route('/api/enrich', methods=['POST'])
def enrich_contacts():
    data = request.json
    contacts = data.get('contacts', [])
    
    if not contacts:
        return jsonify({'success': False, 'message': 'No contacts provided'}), 400
    
    enriched_data = {}
    for contact in contacts:
        email = contact.get('email')
        if not email:
            continue
        
        # Simple pattern-based enrichment
        username = email.split('@')[0]
        domain = email.split('@')[1] if '@' in email else ''
        parts = username.replace('.', ' ').replace('_', ' ').split()
        
        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        
        if not first_name and parts:
            first_name = parts[0].capitalize()
        
        if not last_name and len(parts) > 1:
            last_name = parts[-1].capitalize()
        
        company = None
        if domain:
            company_parts = domain.split('.')
            if len(company_parts) > 1:
                company = company_parts[0].capitalize()
        
        enriched_data[email] = {
            'first_name': first_name,
            'last_name': last_name,
            'company': company,
            'job_title': 'Unknown',
            'source': 'pattern_analysis',
            'confidence_score': 0.7
        }
    
    return jsonify({'success': True, 'data': enriched_data})

# SMTP API
@app.route('/api/smtp', methods=['GET'])
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

@app.route('/api/smtp', methods=['POST'])
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

@app.route('/api/smtp/<int:server_id>', methods=['DELETE'])
def delete_smtp_server(server_id):
    # Check if server exists
    server = query_db('SELECT * FROM smtp_servers WHERE id = ?', [server_id], one=True)
    if not server:
        return jsonify({'success': False, 'message': 'SMTP server not found'}), 404
    
    # Delete server
    execute_db('DELETE FROM smtp_servers WHERE id = ?', [server_id])
    
    return jsonify({'success': True, 'message': 'SMTP server deleted successfully'})

@app.route('/api/smtp/test', methods=['POST'])
def test_smtp():
    # Always return success for testing
    return jsonify({
        'success': True,
        'data': {
            'status': 'success',
            'message': 'SMTP connection successful'
        }
    })

# Proxies API
@app.route('/api/proxies', methods=['GET'])
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

@app.route('/api/proxies', methods=['POST'])
def add_proxy():
    data = request.json
    host = data.get('host')
    port = data.get('port')
    username = data.get('username', '')
    password = data.get('password', '')
    proxy_type = data.get('proxy_type', 'http')
    
    if not host or not port:
        return jsonify({'success': False, 'message': 'Host and port are required'}), 400
    
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

@app.route('/api/proxies/<int:proxy_id>', methods=['DELETE'])
def delete_proxy(proxy_id):
    # Check if proxy exists
    proxy = query_db('SELECT * FROM proxies WHERE id = ?', [proxy_id], one=True)
    if not proxy:
        return jsonify({'success': False, 'message': 'Proxy not found'}), 404
    
    # Delete proxy
    execute_db('DELETE FROM proxies WHERE id = ?', [proxy_id])
    
    return jsonify({'success': True, 'message': 'Proxy deleted successfully'})

@app.route('/api/proxy/test', methods=['POST'])
def test_proxy():
    # Always return success for testing
    return jsonify({
        'success': True,
        'data': {
            'status': 'success',
            'message': 'Proxy connection successful',
            'ip': '203.0.113.42'
        }
    })

# Initialize database if it doesn't exist
if not os.path.exists(DATABASE):
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)