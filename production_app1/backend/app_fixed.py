#!/usr/bin/env python3
"""
Main application file - Combines all API modules
"""
import os
import sqlite3
from flask import Flask, g
from flask_cors import CORS

# Import API modules
from lists_api import lists_api
from smtp_api_fixed import smtp_api
from proxy_api_fixed import proxy_api
from enrichment_api import enrichment_api

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(lists_api, url_prefix='/api')
app.register_blueprint(smtp_api, url_prefix='/api')
app.register_blueprint(proxy_api, url_prefix='/api')
app.register_blueprint(enrichment_api, url_prefix='/api')

# Database configuration
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize database
def init_db():
    with app.app_context():
        db = sqlite3.connect(DATABASE)
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()
        db.close()

# Initialize database if it doesn't exist
if not os.path.exists(DATABASE):
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)