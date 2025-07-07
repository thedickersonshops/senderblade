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

# Copy all the API endpoints from the original file but fix the campaign sending
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
                # Simple sender logic - no complex subdomain rotation for now
                from_email = smtp['from_email']
                from_name = smtp['from_name'] or smtp['from_email']
                to_email = contact['email']
                
                # Simple personalization
                subject = campaign['subject']
                body = campaign['body']
                
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
                context = ssl.create_default_context()
                with smtplib.SMTP(smtp['host'], smtp['port'], timeout=10) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(smtp['username'], smtp['password'])
                    
                    # Simple message
                    message = f"""From: {from_name} <{from_email}>
To: {to_email}
Subject: {subject}
MIME-Version: 1.0
Content-Type: text/html; charset=utf-8

{body}"""
                    
                    # Send email
                    server.sendmail(from_email, to_email, message.encode('utf-8'))
                    sent_count += 1
                    
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
    app.run(debug=True, host='0.0.0.0', port=5002)