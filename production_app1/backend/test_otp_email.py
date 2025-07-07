"""
Test OTP Email Sending
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_admin import simple_admin

def test_otp_email():
    """Test OTP email sending"""
    print("📧 TESTING OTP EMAIL SENDING")
    print("=" * 40)
    
    admin_email = "emmanueldickerson757@icloud.com"
    
    print(f"📧 Admin Email: {admin_email}")
    print(f"📤 Sender Email: timothykeeton.tk@gmail.com")
    print()
    
    # Test OTP request
    print("1. Requesting OTP...")
    result = simple_admin.request_admin_login(admin_email)
    
    if result['success']:
        print("✅ OTP request successful!")
        print(f"📧 OTP email sent to: {admin_email}")
        print(f"⏰ Expires in: {result['expires_in']} minutes")
        print()
        print("📱 CHECK YOUR EMAIL FOR THE 6-DIGIT OTP CODE!")
        print()
        
        # Get OTP from user
        otp_code = input("Enter the OTP code from your email: ").strip()
        
        if otp_code:
            print(f"\n2. Verifying OTP: {otp_code}")
            verify_result = simple_admin.verify_admin_otp(admin_email, otp_code)
            
            if verify_result['success']:
                print("✅ OTP VERIFICATION SUCCESSFUL!")
                print("🎉 Admin login system working perfectly!")
            else:
                print(f"❌ OTP verification failed: {verify_result['message']}")
        else:
            print("❌ No OTP code entered")
    else:
        print(f"❌ OTP request failed: {result['message']}")
        print("Check Gmail credentials in simple_admin.py")

if __name__ == "__main__":
    test_otp_email()