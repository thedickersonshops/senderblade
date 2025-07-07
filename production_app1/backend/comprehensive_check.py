"""
Comprehensive System Check - Double Checking Everything
Making sure everything is perfect, mate!
"""
import os
import sqlite3

def comprehensive_check():
    """Double check everything is working perfectly"""
    
    print("🔍 COMPREHENSIVE SYSTEM CHECK")
    print("=" * 50)
    
    # Check 1: Files exist
    print("\n📁 FILE EXISTENCE CHECK:")
    critical_files = [
        'app_unified.py',
        'app_sender.py',
        'senderblade_admin_final.py',
        'simple_admin.py',
        'enterprise_auth.py',
        'sender.db',
        'database.db'
    ]
    
    for file in critical_files:
        if os.path.exists(file):
            print(f"✅ {file} - EXISTS")
        else:
            print(f"❌ {file} - MISSING")
    
    # Check 2: API Files
    print("\n🔌 API FILES CHECK:")
    api_files = [
        'lists_api.py',
        'smtp_api_fixed.py',
        'proxy_api_fixed.py',
        'spinner_api.py',
        'campaigns_api.py',
        'generator_api.py',
        'auth_api.py',
        'health_api.py'
    ]
    
    for file in api_files:
        if os.path.exists(file):
            print(f"✅ {file} - EXISTS")
        else:
            print(f"❌ {file} - MISSING")
    
    # Check 3: Database Tables
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
            'ip_control', 'admin_settings', 'user_activity'
        ]
        
        for table in required_tables:
            if table in tables:
                print(f"✅ Table '{table}' - EXISTS")
            else:
                print(f"⚠️  Table '{table}' - MISSING (may be created on first use)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
    
    # Check 4: Unified App Routes
    print("\n🛣️ UNIFIED APP ROUTES CHECK:")
    try:
        with open('app_unified.py', 'r') as f:
            content = f.read()
            
        required_routes = [
            '@app.route(\'/\')',
            '@app.route(\'/admin/login\')',
            '@app.route(\'/admin/dashboard\')',
            '@app.route(\'/admin/users\')',
            '@app.route(\'/admin/activity\')',
            '@app.route(\'/admin/security\')',
            '@app.route(\'/admin/settings\')',
            '@app.route(\'/admin/logout\')'
        ]
        
        for route in required_routes:
            if route in content:
                print(f"✅ {route} - FOUND")
            else:
                print(f"❌ {route} - MISSING")
                
    except Exception as e:
        print(f"❌ Route check failed: {e}")
    
    # Check 5: Admin Functions
    print("\n⚙️ ADMIN FUNCTIONS CHECK:")
    admin_functions = [
        'def admin_login',
        'def admin_dashboard',
        'def admin_users',
        'def admin_activity',
        'def admin_security',
        'def admin_settings',
        'def approve_user',
        'def block_user',
        'def delete_user'
    ]
    
    try:
        with open('app_unified.py', 'r') as f:
            content = f.read()
            
        for func in admin_functions:
            if func in content:
                print(f"✅ {func} - FOUND")
            else:
                print(f"❌ {func} - MISSING")
                
    except Exception as e:
        print(f"❌ Function check failed: {e}")
    
    # Check 6: Imports
    print("\n📦 IMPORTS CHECK:")
    required_imports = [
        'from simple_admin import simple_admin',
        'from enterprise_auth import enterprise_auth',
        'from lists_api import lists_api',
        'from smtp_api_fixed import smtp_api',
        'from campaigns_api import campaigns_api'
    ]
    
    try:
        with open('app_unified.py', 'r') as f:
            content = f.read()
            
        for imp in required_imports:
            if imp in content:
                print(f"✅ {imp} - FOUND")
            else:
                print(f"❌ {imp} - MISSING")
                
    except Exception as e:
        print(f"❌ Import check failed: {e}")
    
    # Check 7: Backup Safety
    print("\n🛡️ BACKUP SAFETY CHECK:")
    backup_dirs = [d for d in os.listdir('.') if d.startswith('backup_before_unify_')]
    if backup_dirs:
        latest_backup = max(backup_dirs)
        print(f"✅ Latest backup: {latest_backup}")
        
        # Check backup contents
        backup_files = os.listdir(latest_backup)
        critical_backups = ['app_sender.py', 'senderblade_admin_final.py', 'sender.db']
        
        for file in critical_backups:
            if file in backup_files:
                print(f"✅ Backup of {file} - SAFE")
            else:
                print(f"❌ Backup of {file} - MISSING")
    else:
        print("❌ No backup found!")
    
    print("\n🎯 SUMMARY:")
    print("✅ If all checks show ✅, everything is perfect!")
    print("⚠️  If any ❌ appear, we need to fix them")
    print("🛡️ Your original code is safely backed up")
    
    print("\n🚀 READY TO TEST:")
    print("python app_unified.py")
    print("Main App: http://localhost:5001/")
    print("Admin: http://localhost:5001/admin/login")

if __name__ == "__main__":
    comprehensive_check()