"""
Quick Test - Fix and Test Everything
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_test():
    """Quick test of all components"""
    print("🚀 QUICK TEST - FIXING AND TESTING EVERYTHING")
    print("=" * 50)
    
    # Step 1: Fix database
    print("1. Fixing database schema...")
    try:
        from fix_database import fix_database
        if fix_database():
            print("✅ Database fixed!")
        else:
            print("❌ Database fix failed!")
            return False
    except Exception as e:
        print(f"❌ Database fix error: {e}")
        return False
    
    # Step 2: Test enterprise auth
    print("\n2. Testing enterprise auth...")
    try:
        from enterprise_auth import enterprise_auth
        
        # Test admin login
        result = enterprise_auth.admin_login('admin', 'admin123')
        if result['success']:
            print(f"✅ Admin OTP: {result['otp_code']}")
            
            # Test OTP verification
            otp_result = enterprise_auth.verify_admin_otp(result['user_id'], result['otp_code'])
            if otp_result['success']:
                print("✅ Admin login working!")
            else:
                print(f"❌ OTP verification failed: {otp_result['message']}")
                return False
        else:
            print(f"❌ Admin login failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Enterprise auth error: {e}")
        return False
    
    # Step 3: Test imports
    print("\n3. Testing imports...")
    try:
        from simple_db import execute_db, fetch_db
        print("✅ simple_db imports working!")
        
        # Test database connection
        result = fetch_db("SELECT COUNT(*) as count FROM users")
        if result:
            print(f"✅ Database connection working! Found {result[0]['count']} users")
        else:
            print("❌ Database query failed!")
            return False
            
    except Exception as e:
        print(f"❌ Import/database error: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("🚀 Ready to start SenderBlade!")
    print("\nNext steps:")
    print("1. Run: python app_sender_updated.py")
    print("2. Go to: http://localhost:5001/admin/login")
    print("3. Login: admin / admin123")
    
    return True

if __name__ == "__main__":
    quick_test()