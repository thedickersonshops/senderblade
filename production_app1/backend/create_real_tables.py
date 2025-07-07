"""
Create Real Database Tables - No Demo Data
"""
import sqlite3
import os

def create_real_tables():
    """Create all required tables for real data"""
    print("🔧 Creating real database tables...")
    
    db_path = os.path.join(os.path.dirname(__file__), 'sender.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create IP control table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ip_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL UNIQUE,
                ip_type TEXT NOT NULL CHECK(ip_type IN ('whitelist', 'blacklist', 'suspicious')),
                reason TEXT,
                added_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create user activity table
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
        
        # Create admin settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT NOT NULL UNIQUE,
                setting_value TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default admin settings
        default_settings = [
            ('max_login_attempts', '3', 'Maximum failed login attempts'),
            ('session_timeout', '30', 'Session timeout in minutes'),
            ('otp_expiry', '10', 'OTP expiry time in minutes'),
            ('rate_limit', '100', 'Requests per minute per IP'),
            ('system_name', 'SenderBlade', 'System name'),
            ('admin_email', 'emmanueldickerson757@icloud.com', 'Current admin email')
        ]
        
        for key, value, desc in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO admin_settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            ''', (key, value, desc))
        
        conn.commit()
        conn.close()
        
        print("✅ Real database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database creation error: {e}")
        return False

if __name__ == "__main__":
    create_real_tables()