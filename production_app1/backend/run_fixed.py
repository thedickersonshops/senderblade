#!/usr/bin/env python3
"""
Run the server with database initialization
"""
import os
import sqlite3
import subprocess

# Initialize database.db
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
if not os.path.exists(db_path):
    print("Creating database.db...")
    conn = sqlite3.connect(db_path)
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("database.db created successfully")
else:
    print("database.db already exists")

# Initialize sender.db
db_path = os.path.join(os.path.dirname(__file__), 'sender.db')
if not os.path.exists(db_path):
    print("Creating sender.db...")
    conn = sqlite3.connect(db_path)
    with open('sender_schema.sql', 'r') as f:
        conn.executescript(f.read())
    with open('spinner_schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("sender.db created successfully")
else:
    print("sender.db already exists")

# Run the server
print("Starting server...")
subprocess.run(["python", "app_sender.py"])