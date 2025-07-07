"""
Fix Database Schema - Add missing columns
"""
import sqlite3
import os

def fix_database():
    """Fix database schema issues"""
    print("🔧 Fixing database schema...")
    
    db_path = os.path.join(os.path.dirname(__file__), 'sender.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists and add missing columns
        print("1. Checking users table...")
        
        # Get current table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"   Current columns: {columns}")
        
        # Add missing columns if they don't exist
        missing_columns = [
            ('role', 'TEXT DEFAULT "user"'),
            ('status', 'TEXT DEFAULT "pending"'),
            ('full_name', 'TEXT'),
            ('phone', 'TEXT'),
            ('approved_at', 'TIMESTAMP'),
            ('approved_by', 'INTEGER'),
            ('last_login', 'TIMESTAMP'),
            ('login_count', 'INTEGER DEFAULT 0'),
            ('failed_login_attempts', 'INTEGER DEFAULT 0'),
            ('last_failed_login', 'TIMESTAMP'),
            ('is_active', 'BOOLEAN DEFAULT 0'),
            ('email_verified', 'BOOLEAN DEFAULT 0'),
            ('phone_verified', 'BOOLEAN DEFAULT 0'),
            ('two_factor_enabled', 'BOOLEAN DEFAULT 1'),
            ('profile_data', 'TEXT'),
            ('notes', 'TEXT')
        ]
        
        for column_name, column_def in missing_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_def}')
                    print(f"   ✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        print(f"   ❌ Error adding {column_name}: {e}")
        
        # Update existing admin user
        print("2. Setting up admin user...")
        cursor.execute('''
            UPDATE users SET role = 'admin', status = 'approved', is_active = 1 
            WHERE username = 'admin'
        ''')
        
        if cursor.rowcount == 0:
            # Create admin user if doesn't exist
            import hashlib
            password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, status, is_active, email_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin@senderblade.com', password_hash, 'admin', 'approved', True, True))
            print("   ✅ Created admin user")
        else:
            print("   ✅ Updated existing admin user")
        
        conn.commit()
        conn.close()
        
        print("✅ Database schema fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database fix error: {e}")
        return False

if __name__ == "__main__":
    fix_database()