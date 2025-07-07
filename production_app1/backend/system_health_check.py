"""
Comprehensive System Health Check
Verify everything is working correctly
"""
import sqlite3
import os

def comprehensive_health_check():
    """Check all system components"""
    
    print("🔍 COMPREHENSIVE SYSTEM HEALTH CHECK")
    print("=" * 50)
    
    issues_found = []
    
    # Check 1: Database files exist
    print("\n📁 DATABASE FILES CHECK:")
    db_files = ['sender.db', 'database.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"✅ {db_file} - EXISTS")
        else:
            print(f"❌ {db_file} - MISSING")
            issues_found.append(f"Missing database file: {db_file}")
    
    # Check 2: Database tables
    print("\n🗄️ DATABASE TABLES CHECK:")
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        # Check for required tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'users', 'campaigns', 'lists', 'contacts', 
            'smtp_servers', 'proxies', 'activity_logs',
            'ip_control', 'admin_settings', 'user_activity',
            'delivery_tracking'
        ]
        
        for table in required_tables:
            if table in tables:
                print(f"✅ Table '{table}' - EXISTS")
            else:
                print(f"❌ Table '{table}' - MISSING")
                issues_found.append(f"Missing table: {table}")
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        
        required_user_columns = [
            'id', 'username', 'password', 'email', 'status', 
            'is_active', 'otp_code', 'otp_expires', 'otp_verified'
        ]
        
        print(f"\n👤 USERS TABLE COLUMNS:")
        for col in required_user_columns:
            if col in user_columns:
                print(f"✅ Column '{col}' - EXISTS")
            else:
                print(f"❌ Column '{col}' - MISSING")
                issues_found.append(f"Missing user column: {col}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        issues_found.append(f"Database error: {e}")
    
    # Check 3: Test user data
    print("\n👥 USER DATA CHECK:")
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Total users in database: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT username, email, status, is_active, otp_verified FROM users LIMIT 3")
            users = cursor.fetchall()
            print("📋 Sample users:")
            for user in users:
                print(f"   - {user[0]} ({user[1]}) - Status: {user[2]}, Active: {user[3]}, OTP: {user[4]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ User data check failed: {e}")
        issues_found.append(f"User data error: {e}")
    
    # Check 4: API files
    print("\n🔌 API FILES CHECK:")
    api_files = [
        'auth_api.py', 'lists_api.py', 'smtp_api_fixed.py',
        'campaigns_api.py', 'notification_system.py'
    ]
    
    for api_file in api_files:
        if os.path.exists(api_file):
            print(f"✅ {api_file} - EXISTS")
        else:
            print(f"❌ {api_file} - MISSING")
            issues_found.append(f"Missing API file: {api_file}")
    
    # Summary
    print(f"\n📊 HEALTH CHECK SUMMARY:")
    if not issues_found:
        print("✅ ALL CHECKS PASSED - System is healthy!")
        return True
    else:
        print(f"❌ {len(issues_found)} ISSUES FOUND:")
        for issue in issues_found:
            print(f"   • {issue}")
        return False

if __name__ == "__main__":
    comprehensive_health_check()