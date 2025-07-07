"""
Admin Email Configuration Tool
How to change admin email and configure OTP sending
"""

def update_admin_email():
    """Update admin email in the system"""
    print("📧 ADMIN EMAIL CONFIGURATION")
    print("=" * 40)
    
    print("\n🔧 HOW TO CHANGE ADMIN EMAIL:")
    print("1. Open: simple_admin.py")
    print("2. Find line: self.ADMIN_EMAIL = \"emmanueldickerson757@icloud.com\"")
    print("3. Change to: self.ADMIN_EMAIL = \"your-new-email@example.com\"")
    print("4. Save file and restart application")
    
    print("\n📧 HOW TO CONFIGURE OTP EMAIL SENDING:")
    print("1. Open: simple_admin.py")
    print("2. Find the gmail_smtp section:")
    print("   'username': 'YOUR_GMAIL@gmail.com'")
    print("   'password': 'YOUR_APP_PASSWORD'")
    print("3. Replace with your Gmail credentials")
    print("4. Enable 2FA on Gmail and generate App Password")
    
    print("\n🔑 GMAIL APP PASSWORD SETUP:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Factor Authentication")
    print("3. Go to: App passwords")
    print("4. Generate password for 'Mail'")
    print("5. Use this password in simple_admin.py")
    
    print("\n⚡ QUICK TEST:")
    print("1. Run: python app_simple_admin.py")
    print("2. Go to: http://localhost:5001/admin/login")
    print("3. Enter admin email")
    print("4. Check email for OTP code")
    print("5. Enter OTP to login")
    
    print(f"\n📧 CURRENT ADMIN EMAIL: emmanueldickerson757@icloud.com")
    print("✏️  Change this in simple_admin.py file")

def generate_test_otp():
    """Generate test OTP for testing"""
    import random
    import string
    
    otp = ''.join(random.choices(string.digits, k=6))
    print(f"\n🔢 TEST OTP GENERATED: {otp}")
    print("Use this for testing if email sending is not configured yet")
    
    return otp

if __name__ == "__main__":
    update_admin_email()
    generate_test_otp()