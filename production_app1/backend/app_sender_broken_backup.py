#!/usr/bin/env python3
"""
Sender App - Main application file
"""
import os
import sqlite3
from flask import Flask, g, send_from_directory, session
from flask_cors import CORS

# Import API modules
from lists_api import lists_api
from smtp_api_fixed import smtp_api
from proxy_api_fixed import proxy_api
from spinner_api import spinner_api
from campaigns_api import campaigns_api
from generator_api import generator_api
from auth_api import auth_api
from health_api import health_api
from admin_api import admin_api

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'senderblade_secret_key_change_in_production'
CORS(app, origins='*', supports_credentials=True, allow_headers=['Content-Type'], methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Register blueprints
app.register_blueprint(lists_api, url_prefix='/api')
app.register_blueprint(smtp_api, url_prefix='/api')
app.register_blueprint(proxy_api, url_prefix='/api')
app.register_blueprint(spinner_api, url_prefix='/api')
app.register_blueprint(campaigns_api, url_prefix='/api')
app.register_blueprint(generator_api, url_prefix='/api')
app.register_blueprint(auth_api, url_prefix='/api')
app.register_blueprint(health_api, url_prefix='/api')
app.register_blueprint(admin_api, url_prefix='/api')

# Serve static files
@app.route('/')
def index():
    return send_from_directory('../static', 'login.html')

@app.route('/login')
def login_page():
    return send_from_directory('../static', 'login.html')

@app.route('/dashboard')
def dashboard_page():
    return send_from_directory('../static', 'blade_scissor_feint.html')

@app.route('/admin/login')
def admin_login_page():
    return send_from_directory('../static', 'admin_login.html')

# Import and run your existing admin system
import subprocess
import sys

@app.route('/admin/dashboard')
def admin_dashboard_route():
    # Run your existing admin system
    try:
        from senderblade_admin_final import admin_dashboard
        return admin_dashboard()
    except:
        # Fallback to regular dashboard if admin system not available
        return send_from_directory('../static', 'blade_scissor_feint.html')



@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('../static', filename)

# Database configuration
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')
SPINNER_DATABASE = os.path.join(os.path.dirname(__file__), 'sender.db')

@app.teardown_appcontext
def close_connection(exception):
    # Close all database connections
    for attr in ['_database', '_spinner_database', '_main_database', '_proxy_database']:
        db = getattr(g, attr, None)
        if db is not None:
            db.close()

# Initialize database
def init_db():
    # Initialize main database
    db = sqlite3.connect(DATABASE)
    with open('schema.sql', 'r') as f:
        db.executescript(f.read())
    db.commit()
    db.close()
    
    # Initialize spinner database
    db = sqlite3.connect(SPINNER_DATABASE)
    with open('sender_schema.sql', 'r') as f:
        db.executescript(f.read())
    # Also initialize spinner schema
    with open('spinner_schema.sql', 'r') as f:
        db.executescript(f.read())
    db.commit()
    db.close()

# Always initialize databases to ensure they're up to date
init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)