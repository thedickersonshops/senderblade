#!/usr/bin/env python3
"""
Test Admin System - Quick test
"""
from simple_admin import simple_admin

print("🔍 TESTING ADMIN SYSTEM")
print("-" * 30)

# Test 1: Check admin email
admin_email = simple_admin.get_admin_email()
print(f"✅ Admin Email: {admin_email}")

# Test 2: Generate OTP
otp = simple_admin.generate_otp()
print(f"✅ OTP Generated: {otp}")

# Test 3: Test database connection
try:
    import sqlite3
    conn = sqlite3.connect('sender.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_otp'")
    result = cursor.fetchone()
    if result:
        print("✅ Admin OTP table exists")
    else:
        print("❌ Admin OTP table missing")
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")

print("\n🎯 ADMIN LOGIN SHOULD BE:")
print("URL: http://localhost:5001/admin/login")
print(f"Email: {admin_email}")
print("Then enter OTP from email")