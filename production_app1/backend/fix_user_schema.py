"""
Fix User Database Schema - Add Missing Columns Safely
"""
import sqlite3
import os

def fix_user_schema():
    """Add missing columns to users table safely"""
    
    print("🔧 FIXING USER DATABASE SCHEMA...")
    
    db_path = 'sender.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add missing columns if they don't exist
        missing_columns = [
            ('full_name', 'TEXT DEFAULT ""'),
            ('phone', 'TEXT DEFAULT ""'),
            ('status', 'TEXT DEFAULT "pending"'),
            ('is_active', 'INTEGER DEFAULT 0'),
            ('otp_code', 'TEXT'),
            ('otp_expires', 'INTEGER'),
            ('otp_verified', 'INTEGER DEFAULT 0'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        for column_name, column_def in missing_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_def}')
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    print(f"⚠️  Column {column_name} might already exist: {e}")
        
        # Ensure user_activity table exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                activity_type TEXT,
                description TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ user_activity table ready")
        
        conn.commit()
        conn.close()
        
        print("✅ DATABASE SCHEMA FIXED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        return False

if __name__ == "__main__":
    fix_user_schema()