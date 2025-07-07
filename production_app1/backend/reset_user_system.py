"""
Reset User System - Clean Slate for Testing
"""
import sqlite3

def reset_user_system():
    """Reset user system for fresh testing"""
    
    print("🔄 RESETTING USER SYSTEM FOR FRESH TEST")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        # Show current users
        cursor.execute("SELECT id, username, email, status, otp_verified FROM users")
        users = cursor.fetchall()
        
        print(f"\n📋 CURRENT USERS ({len(users)}):")
        for user in users:
            print(f"   ID: {user[0]} | {user[1]} | {user[2]} | Status: {user[3]} | OTP: {user[4]}")
        
        # Clear all users
        cursor.execute("DELETE FROM users")
        deleted_users = cursor.rowcount
        
        # Clear user activity
        cursor.execute("DELETE FROM user_activity")
        deleted_activity = cursor.rowcount
        
        # Clear delivery tracking
        cursor.execute("DELETE FROM delivery_tracking")
        deleted_tracking = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ RESET COMPLETE:")
        print(f"   • Deleted {deleted_users} users")
        print(f"   • Deleted {deleted_activity} activity logs")
        print(f"   • Deleted {deleted_tracking} delivery records")
        
        print(f"\n🎯 SYSTEM READY FOR FRESH TESTING:")
        print("   • Clean user database")
        print("   • No stuck OTP codes")
        print("   • Fresh registration flow")
        print("   • Ready for new test user")
        
        return True
        
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        return False

def verify_reset():
    """Verify the reset worked"""
    
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_activity")
        activity_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"\n🔍 VERIFICATION:")
        print(f"   • Users: {user_count}")
        print(f"   • Activity logs: {activity_count}")
        
        if user_count == 0:
            print("✅ Reset successful - Ready for fresh testing!")
            return True
        else:
            print("⚠️ Some data remains")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("⚠️ This will delete ALL users and start fresh!")
    print("Are you sure? (y/N): ", end="")
    
    confirm = input().lower()
    if confirm == 'y':
        if reset_user_system():
            verify_reset()
            print("\n🚀 READY FOR FRESH REGISTRATION TEST!")
            print("Now you can test registration with a clean system.")
        else:
            print("❌ Reset failed - check errors above")
    else:
        print("❌ Reset cancelled")