#!/usr/bin/env python3
"""
Test database setup
"""
import os
import sqlite3

def check_database(db_name):
    """Check if database exists and has tables"""
    db_path = os.path.join(os.path.dirname(__file__), db_name)
    
    if not os.path.exists(db_path):
        print(f"Database {db_name} does not exist")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Database {db_name} exists with tables: {[t[0] for t in tables]}")
        
        # Check specific tables
        if db_name == 'database.db':
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='smtp_servers';")
            if cursor.fetchone()[0] == 0:
                print("SMTP servers table not found")
                return False
                
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='proxies';")
            if cursor.fetchone()[0] == 0:
                print("Proxies table not found")
                return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error checking database {db_name}: {e}")
        return False

# Check both databases
check_database('database.db')
check_database('sender.db')

# Create database.db if it doesn't exist
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
if not os.path.exists(db_path):
    print("Creating database.db...")
    conn = sqlite3.connect(db_path)
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("database.db created successfully")

# Create sender.db if it doesn't exist
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

print("Database check complete")