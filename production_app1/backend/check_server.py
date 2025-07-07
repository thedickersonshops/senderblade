#!/usr/bin/env python3
"""
Quick server status check
"""
import requests
import sys

def check_server():
    try:
        response = requests.get('http://localhost:5001/api/lists', timeout=5)
        print("✅ Server is running and responding")
        print(f"Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        print("Start server with: python app_sender.py")
        return False
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

if __name__ == '__main__':
    if check_server():
        sys.exit(0)
    else:
        sys.exit(1)