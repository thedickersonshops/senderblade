#!/usr/bin/env python3
"""
Test SMTP and Proxy validation
"""
import requests
import json

BASE_URL = 'http://localhost:5001/api'

def test_smtp_invalid():
    """Test SMTP with invalid credentials"""
    data = {
        'name': 'Test SMTP',
        'host': 'smtp.gmail.com',
        'port': 587,
        'username': 'invalid@gmail.com',
        'password': 'wrongpassword',
        'from_email': 'invalid@gmail.com'
    }
    
    response = requests.post(f'{BASE_URL}/smtp', json=data)
    print(f"SMTP Invalid Test: {response.status_code} - {response.json()}")

def test_proxy_invalid():
    """Test proxy with invalid credentials"""
    data = {
        'host': '1.2.3.4',
        'port': 8080,
        'proxy_type': 'http',
        'username': 'invalid',
        'password': 'wrongpassword'
    }
    
    response = requests.post(f'{BASE_URL}/proxies', json=data)
    print(f"Proxy Invalid Test: {response.status_code} - {response.json()}")

def test_duplicate_smtp():
    """Test duplicate SMTP detection"""
    data = {
        'name': 'Test SMTP 1',
        'host': 'smtp.example.com',
        'port': 587,
        'username': 'test@example.com',
        'password': 'testpass123',
        'from_email': 'test@example.com'
    }
    
    # Try to add the same SMTP twice
    response1 = requests.post(f'{BASE_URL}/smtp', json=data)
    print(f"First SMTP Add: {response1.status_code} - {response1.json()}")
    
    data['name'] = 'Test SMTP 2'  # Different name, same connection details
    response2 = requests.post(f'{BASE_URL}/smtp', json=data)
    print(f"Duplicate SMTP Test: {response2.status_code} - {response2.json()}")

if __name__ == '__main__':
    print("Testing SMTP and Proxy validation...")
    print("Make sure the server is running on localhost:5001")
    print()
    
    try:
        test_smtp_invalid()
        print()
        test_proxy_invalid()
        print()
        test_duplicate_smtp()
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure the server is running: python app_sender.py")