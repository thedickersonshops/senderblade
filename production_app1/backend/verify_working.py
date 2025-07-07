#!/usr/bin/env python3
"""
Verify that basic functionality is working
"""
import requests
import json

BASE_URL = 'http://localhost:5001/api'

def test_dashboard():
    """Test dashboard endpoints"""
    endpoints = ['/lists', '/smtp', '/proxies', '/campaigns']
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{BASE_URL}{endpoint}')
            print(f"GET {endpoint}: {response.status_code} - {'OK' if response.status_code == 200 else 'FAILED'}")
        except Exception as e:
            print(f"GET {endpoint}: FAILED - {e}")

def test_list_creation():
    """Test creating a list"""
    data = {
        'name': 'Test List',
        'description': 'Test description'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/lists', json=data)
        print(f"Create List: {response.status_code} - {'OK' if response.status_code == 200 else 'FAILED'}")
        if response.status_code == 200:
            return response.json().get('data', {}).get('id')
    except Exception as e:
        print(f"Create List: FAILED - {e}")
    return None

def test_spinner():
    """Test spinner functionality"""
    data = {
        'content': 'Hello {first_name}, this is a test message.',
        'count': 1
    }
    
    try:
        response = requests.post(f'{BASE_URL}/spinner/process', json=data)
        print(f"Spinner Process: {response.status_code} - {'OK' if response.status_code == 200 else 'FAILED'}")
    except Exception as e:
        print(f"Spinner Process: FAILED - {e}")

if __name__ == '__main__':
    print("Verifying basic functionality...")
    print("Make sure the server is running on localhost:5001")
    print()
    
    try:
        test_dashboard()
        print()
        list_id = test_list_creation()
        print()
        test_spinner()
        print()
        print("Basic functionality test complete")
    except Exception as e:
        print(f"Verification failed: {e}")
        print("Make sure the server is running: python app_sender.py")