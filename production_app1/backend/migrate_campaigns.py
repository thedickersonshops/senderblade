#!/usr/bin/env python3
"""
Migration script to add new columns to campaigns table
"""
import sqlite3
import os

def migrate_campaigns_table():
    """Add new columns to campaigns table"""
    db_path = 'sender.db'
    
    if not os.path.exists(db_path):
        print("Database not found. Creating new database...")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(campaigns)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns
        new_columns = [
            ('from_name', 'TEXT DEFAULT ""'),
            ('from_email', 'TEXT DEFAULT ""'),
            ('reply_to', 'TEXT DEFAULT ""'),
            ('priority', 'TEXT DEFAULT "normal"'),
            ('enable_ip_rotation', 'BOOLEAN DEFAULT 0'),
            ('delivery_mode', 'TEXT DEFAULT "normal"')
        ]
        
        for column_name, column_def in new_columns:
            if column_name not in columns:
                cursor.execute(f'ALTER TABLE campaigns ADD COLUMN {column_name} {column_def}')
                print(f"Added column: {column_name}")
            else:
                print(f"Column already exists: {column_name}")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_campaigns_table()