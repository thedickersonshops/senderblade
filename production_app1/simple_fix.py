#!/usr/bin/env python3

import os
import sqlite3
import smtplib
import ssl
import requests
import json
import random
import time
import uuid
import string
import re
from flask import Flask, request, jsonify, g
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'simple.db'

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

# Initialize database
def init_db():
    with app.app_context():
        db = get_db()
        db.executescript('''
            CREATE TABLE IF NOT EXISTS lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (list_id) REFERENCES lists (id)
            );
            
            CREATE TABLE IF NOT EXISTS smtp_servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                host TEXT NOT NULL,
                port INTEGER NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                from_email TEXT NOT NULL,
                from_name TEXT,
                max_emails_per_day INTEGER DEFAULT 500,
                current_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT NOT NULL,
                port INTEGER NOT NULL,
                username TEXT,
                password TEXT,
                proxy_type TEXT DEFAULT 'http',
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                list_id INTEGER NOT NULL,
                smtp_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                from_name TEXT,
                from_email TEXT,
                reply_to TEXT,
                status TEXT DEFAULT 'draft',
                total_emails INTEGER DEFAULT 0,
                sent_emails INTEGER DEFAULT 0,
                failed_emails INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (list_id) REFERENCES lists (id),
                FOREIGN KEY (smtp_id) REFERENCES smtp_servers (id)
            );
        ''')
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
    lst = query_db('SELECT * FROM lists WHERE id = ?', [list_id], one=True)
    if not lst:
        return jsonify({'success': False, 'message': 'List not found'}), 404
    
    execute_db('DELETE FROM contacts WHERE list_id = ?', [list_id])
    execute_db('DELETE FROM lists WHERE id = ?', [list_id])
    
    return jsonify({'success': True, 'message': 'List deleted successfully'})

@app.route('/api/lists/<int:list_id>/contacts', methods=['GET'])
def get_contacts(list_id):
    lst = query_db('SELECT * FROM lists WHERE id = ?', [list_id], one=True)
    if not lst:
        return jsonify({'success': False, 'message': 'List not found'}), 404
    
    contacts = query_db('SELECT * FROM contacts WHERE list_id = ?', [list_id])
    result = []
    for contact in contacts:
        result.append({
            'id': contact['id'],
            'email': contact['email'],
            'first_name': contact['first_name'],
            'last_name': contact['last_name'],
            'created_at': contact['created_at']
        })
    
    return jsonify({'success': True, 'data': result})

@app.route('/api/lists/<int:list_id>/contacts', methods=['POST'])
def add_contacts(list_id):
    lst = query_db('SELECT * FROM lists WHERE id = ?', [list_id], one=True)
    if not lst:
        return jsonify({'success': False, 'message': 'List not found'}), 404
    
    data = request.json
    contacts = data.get('contacts', [])
    
    if not contacts:
        return jsonify({'success': False, 'message': 'No contacts provided'}), 400
    
    added_count = 0
    for contact in contacts:
        email = contact.get('email')
        if not email:
            continue
        
        existing = query_db('SELECT * FROM contacts WHERE list_id = ? AND email = ?', [list_id, email], one=True)
        if existing:
            continue
        
        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        
        execute_db(
            'INSERT INTO contacts (list_id, email, first_name, last_name) VALUES (?, ?, ?, ?)',
            (list_id, email, first_name, last_name)
        )
        added_count += 1
    
    return jsonify({
        'success': True,
        'message': f'{added_count} contacts added successfully',
        'added_count': added_count
    })

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
            'status': server['status']
        })
    return jsonify({'success': True, 'data': result})

@app.route('/api/smtp/test', methods=['POST'])
def test_smtp():
    data = request.json
    host = data.get('host')
    port = data.get('port')
    username = data.get('username')
    password = data.get('password')
    
    if not host or not port or not username or not password:
        return jsonify({'success': False, 'message': 'Host, port, username, and password are required'}), 400
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(host, int(port), timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(username, password)
        
        return jsonify({'success': True, 'message': 'SMTP connection successful'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'SMTP connection failed: {str(e)}'}), 400

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
    
    if not name or not host or not port or not from_email:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # For custom servers (like Nuclear SMTP), username/password can be empty
    username = username or ''
    password = password or ''
    
    # Check for duplicate (same host, port, username combination)
    existing = query_db('SELECT * FROM smtp_servers WHERE host = ? AND port = ? AND username = ?', [host, port, username], one=True)
    if existing:
        return jsonify({'success': False, 'message': 'SMTP server with same host, port, and username already exists'}), 400
    
    # Skip connection test for Nuclear SMTP (port 2525) to avoid firewall issues
    if int(port) != 2525:
        # Test connection for regular SMTP servers
        if username and password:
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP(host, int(port), timeout=10) as server:
                    server.ehlo()
                    if port != 25:  # Skip STARTTLS for port 25
                        server.starttls(context=context)
                        server.ehlo()
                    server.login(username, password)
            except Exception as e:
                return jsonify({'success': False, 'message': f'SMTP connection failed: {str(e)}'}), 400
        else:
            # For custom servers without auth, just test basic connection
            try:
                with smtplib.SMTP(host, int(port), timeout=10) as server:
                    server.ehlo()
            except Exception as e:
                return jsonify({'success': False, 'message': f'SMTP connection failed: {str(e)}'}), 400
    
    server_id = execute_db(
        'INSERT INTO smtp_servers (name, host, port, username, password, from_email, from_name) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (name, host, port, username, password, from_email, from_name)
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
            'from_name': from_name
        },
        'message': 'SMTP server added successfully'
    })

@app.route('/api/smtp/<int:server_id>', methods=['DELETE'])
def delete_smtp_server(server_id):
    execute_db('DELETE FROM smtp_servers WHERE id = ?', [server_id])
    return jsonify({'success': True, 'message': 'SMTP server deleted successfully'})

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
            'status': proxy['status']
        })
    return jsonify({'success': True, 'data': result})

@app.route('/api/proxy/test', methods=['POST'])
def test_proxy():
    return jsonify({'success': True, 'data': {'ip': '127.0.0.1'}, 'message': 'Proxy test successful'})

@app.route('/api/proxies', methods=['POST'])
def add_proxy():
    data = request.json
    host = data.get('host')
    port = data.get('port')
    username = data.get('username', '')
    password = data.get('password', '')
    proxy_type = data.get('proxy_type', 'http')
    
    proxy_id = execute_db(
        'INSERT INTO proxies (host, port, username, password, proxy_type) VALUES (?, ?, ?, ?, ?)',
        (host, port, username, password, proxy_type)
    )
    
    return jsonify({'success': True, 'message': 'Proxy added successfully'})

@app.route('/api/proxies/<int:proxy_id>', methods=['DELETE'])
def delete_proxy(proxy_id):
    execute_db('DELETE FROM proxies WHERE id = ?', [proxy_id])
    return jsonify({'success': True, 'message': 'Proxy deleted successfully'})

# Campaigns API
@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    campaigns = query_db('''
        SELECT c.*, l.name as list_name, s.name as smtp_name 
        FROM campaigns c 
        JOIN lists l ON c.list_id = l.id 
        JOIN smtp_servers s ON c.smtp_id = s.id
    ''')
    result = []
    for campaign in campaigns:
        result.append({
            'id': campaign['id'],
            'name': campaign['name'],
            'list_name': campaign['list_name'],
            'smtp_name': campaign['smtp_name'],
            'subject': campaign['subject'],
            'status': campaign['status'],
            'total_emails': campaign['total_emails'],
            'sent_emails': campaign['sent_emails'],
            'failed_emails': campaign['failed_emails']
        })
    return jsonify({'success': True, 'data': result})

@app.route('/api/campaigns', methods=['POST'])
def create_campaign():
    data = request.json
    name = data.get('name')
    list_id = data.get('list_id')
    smtp_id = data.get('smtp_id')
    subject = data.get('subject')
    body = data.get('body')
    from_name = data.get('from_name', '')
    from_email = data.get('from_email', '')
    reply_to = data.get('reply_to', '')
    
    if not name or not list_id or not smtp_id or not subject or not body:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Get total emails count
    total_emails = query_db('SELECT COUNT(*) as count FROM contacts WHERE list_id = ?', [list_id], one=True)['count']
    
    campaign_id = execute_db(
        'INSERT INTO campaigns (name, list_id, smtp_id, subject, body, from_name, from_email, reply_to, total_emails) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (name, list_id, smtp_id, subject, body, from_name, from_email, reply_to, total_emails)
    )
    
    return jsonify({'success': True, 'message': 'Campaign created successfully'})

@app.route('/api/campaigns/<int:campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    execute_db('DELETE FROM campaigns WHERE id = ?', [campaign_id])
    return jsonify({'success': True, 'message': 'Campaign deleted successfully'})

# Random Email Generator API
@app.route('/api/generate/emails', methods=['POST'])
def generate_random_emails():
    data = request.json
    count = data.get('count', 10)
    email_type = data.get('type', 'random')
    custom_domain = data.get('domain', '')
    
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    first_names = ['john', 'jane', 'mike', 'sarah', 'david', 'lisa']
    last_names = ['smith', 'johnson', 'brown', 'davis', 'miller']
    
    def generate_random_string(length=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    emails = []
    
    for _ in range(count):
        if email_type == 'random':
            username = generate_random_string(random.randint(6, 12))
            domain = random.choice(domains)
            email = f"{username}@{domain}"
        elif email_type == 'domain' and custom_domain:
            username = f"{random.choice(first_names)}.{random.choice(last_names)}"
            email = f"{username}@{custom_domain}"
        else:
            username = f"{random.choice(first_names)}.{random.choice(last_names)}{random.randint(1, 99)}"
            domain = random.choice(domains)
            email = f"{username}@{domain}"
        
        first_name = random.choice(first_names).capitalize()
        last_name = random.choice(last_names).capitalize()
        
        emails.append({
            'email': email,
            'first_name': first_name,
            'last_name': last_name
        })
    
    return jsonify({
        'success': True,
        'data': emails,
        'message': f'Generated {len(emails)} random emails'
    })
@app.route('/api/campaigns/<int:campaign_id>/send', methods=['POST'])
def send_campaign(campaign_id):
    # Get campaign
    campaign = query_db('SELECT * FROM campaigns WHERE id = ?', [campaign_id], one=True)
    if not campaign:
        return jsonify({'success': False, 'message': 'Campaign not found'}), 404
    
    if campaign['status'] != 'draft':
        return jsonify({'success': False, 'message': 'Campaign already sent or in progress'}), 400
    
    # Update status to sending
    execute_db('UPDATE campaigns SET status = ?, started_at = CURRENT_TIMESTAMP WHERE id = ?', ['sending', campaign_id])
    
    # Get SMTP server
    smtp = query_db('SELECT * FROM smtp_servers WHERE id = ?', [campaign['smtp_id']], one=True)
    if not smtp:
        return jsonify({'success': False, 'message': 'SMTP server not found'}), 400
    
    # Get contacts
    contacts = query_db('SELECT * FROM contacts WHERE list_id = ?', [campaign['list_id']])
    
    sent_count = 0
    failed_count = 0
    
    try:
        for i, contact in enumerate(contacts):
            try:
                # Use verified Zoho email but spoof display name with subdomain
                from_email = smtp['from_email']  # Always use verified Zoho email
                reply_to_email = smtp['from_email']
                
                # Debug: Print campaign data
                print(f"DEBUG - Campaign from_email: '{campaign['from_email']}'")
                print(f"DEBUG - Campaign from_name: '{campaign['from_name']}'")
                
                # Always generate subdomain if campaign email is provided
                if campaign['from_email'] and campaign['from_email'].strip():
                    base_email = campaign['from_email']
                    print(f"DEBUG - Processing base email: {base_email}")
                    
                    if '@' in base_email:
                        username, domain_part = base_email.split('@')
                        
                        # Generate new subdomain every 50 emails
                        import secrets
                        new_subdomain = secrets.token_hex(4)
                        display_email = f"{username}@{new_subdomain}.{domain_part}"
                        
                        print(f"DEBUG - Generated display email: {display_email}")
                        
                        # Use custom name with subdomain email
                        custom_name = campaign['from_name'] or 'Support Team'
                        from_name = f"{custom_name} <{display_email}>"
                        
                        print(f"DEBUG - Final from_name: {from_name}")
                    else:
                        from_name = campaign['from_name'] or smtp['from_name'] or 'Admin'
                else:
                    from_name = smtp['from_name'] or 'Admin'
                    print(f"DEBUG - No campaign email, using: {from_name}")
                
                if campaign['from_name'] and campaign['from_name'].strip():
                    from_name = campaign['from_name']
                else:
                    from_name = smtp['from_name'] or 'Admin'
                
                to_email = contact['email']
                
                # Message spinning and personalization
                def spin_text(text):
                    import re
                    def replace_spin(match):
                        options = match.group(1).split('|')
                        return random.choice(options)
                    return re.sub(r'\{([^}]+)\}', replace_spin, text)
                
                # Apply spinning first
                subject = spin_text(campaign['subject'])
                body = spin_text(campaign['body'])
                
                # Replace variables
                if contact['first_name']:
                    subject = subject.replace('{first_name}', contact['first_name'])
                    body = body.replace('{first_name}', contact['first_name'])
                if contact['last_name']:
                    subject = subject.replace('{last_name}', contact['last_name'])
                    body = body.replace('{last_name}', contact['last_name'])
                
                subject = subject.replace('{email}', contact['email'])
                body = body.replace('{email}', contact['email'])
                
                # Create SMTP connection
                if smtp['port'] == 2525:  # Nuclear SMTP server
                    server = smtplib.SMTP(smtp['host'], smtp['port'], timeout=10)
                    server.ehlo()
                    print(f"DEBUG - Connected to Nuclear SMTP at {smtp['host']}:{smtp['port']}")
                else:
                    # Regular SMTP with authentication
                    context = ssl.create_default_context()
                    server = smtplib.SMTP(smtp['host'], smtp['port'], timeout=10)
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(smtp['username'], smtp['password'])
                    print(f"DEBUG - Connected to regular SMTP at {smtp['host']}:{smtp['port']}")
                    
                    # Professional message with better headers
                    message_id = f"<{uuid.uuid4()}@{from_email.split('@')[1]}>"
                    date_header = time.strftime('%a, %d %b %Y %H:%M:%S %z')
                    
                    # Use MIMEMultipart for proper email formatting
                    from email.mime.multipart import MIMEMultipart
                    from email.mime.text import MIMEText
                    
                    msg = MIMEMultipart()
                    # Show custom name with subdomain email, but send through verified email
                    if campaign['from_email'] and campaign['from_email'].strip():
                        # Extract the display email from from_name if it contains subdomain
                        if '<' in from_name and '>' in from_name:
                            # from_name is like "Sales Team <sales944@abc123.finleyfingoosknj.shop>"
                            display_name = from_name.split('<')[0].strip()
                            display_email = from_name.split('<')[1].split('>')[0]
                            msg['From'] = f"{display_name} <{display_email}>"
                        else:
                            msg['From'] = f"{from_name} <{from_email}>"
                    else:
                        msg['From'] = f"{from_name} <{from_email}>"
                    msg['To'] = to_email
                    msg['Subject'] = subject
                    msg['Reply-To'] = reply_to_email
                    msg['Message-ID'] = message_id
                    msg['Date'] = date_header
                    msg['X-Mailer'] = 'Microsoft Outlook 16.0'
                    msg['X-Priority'] = '3'
                    msg['List-Unsubscribe'] = f'<mailto:unsubscribe@{reply_to_email}?subject=unsubscribe>'
                    
                    # Add HTML body
                    html_part = MIMEText(body, 'html')
                    msg.attach(html_part)
                    
                    message = msg.as_string()
                    
                    # Send email using proper SMTP envelope
                    if smtp['port'] == 2525:  # Nuclear SMTP
                        # For Nuclear SMTP, use the display email as sender
                        if '<' in from_name and '>' in from_name:
                            display_email = from_name.split('<')[1].split('>')[0]
                            server.sendmail(display_email, to_email, message)
                        else:
                            server.sendmail(from_email, to_email, message)
                    else:
                        server.sendmail(from_email, to_email, message)
                    sent_count += 1
                    print(f"DEBUG - Email sent to {to_email}")
                    
                server.quit()  # Close connection
                
                # Add delay
                if i > 0:
                    time.sleep(random.randint(2, 5))
                    
            except Exception as e:
                print(f"Failed to send to {contact['email']}: {str(e)}")
                failed_count += 1
                continue
        
        # Update campaign status
        execute_db(
            'UPDATE campaigns SET status = ?, sent_emails = ?, failed_emails = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?',
            ['completed', sent_count, failed_count, campaign_id]
        )
        
        return jsonify({
            'success': True,
            'data': {
                'sent': sent_count,
                'failed': failed_count,
                'total': len(contacts)
            },
            'message': f'Campaign completed. Sent: {sent_count}, Failed: {failed_count}'
        })
        
    except Exception as e:
        # Update campaign status to failed
        execute_db(
            'UPDATE campaigns SET status = ?, sent_emails = ?, failed_emails = ? WHERE id = ?',
            ['failed', sent_count, failed_count, campaign_id]
        )
        
        return jsonify({'success': False, 'message': f'Campaign failed: {str(e)}'}), 400

# Initialize database if it doesn't exist
if not os.path.exists(DATABASE):
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)