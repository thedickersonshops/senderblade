#!/usr/bin/env python3
"""
Test Delivery Monitoring System
"""
import sqlite3
import time
import random
from smart_delivery_tracker import smart_tracker

def add_test_delivery_data():
    """Add sample delivery data for testing"""
    print("🧪 Adding test delivery data...")
    
    # Sample test data
    test_deliveries = [
        {'email': 'test1@example.com', 'smtp_code': 250, 'response': 'Message accepted', 'status': 'delivered'},
        {'email': 'test2@example.com', 'smtp_code': 550, 'response': 'Mailbox not found', 'status': 'rejected'},
        {'email': 'test3@example.com', 'smtp_code': 250, 'response': 'Queued for delivery', 'status': 'delivered'},
        {'email': 'test4@example.com', 'smtp_code': 421, 'response': 'Service temporarily unavailable', 'status': 'deferred'},
        {'email': 'test5@example.com', 'smtp_code': 250, 'response': 'Message accepted for delivery', 'status': 'delivered'},
    ]
    
    for delivery in test_deliveries:
        delivery_time = random.uniform(0.5, 3.0)  # Random delivery time
        result = smart_tracker.track_delivery(
            campaign_id=1,
            email=delivery['email'],
            smtp_server='test-smtp.example.com',
            smtp_code=delivery['smtp_code'],
            smtp_response=delivery['response'],
            delivery_time=delivery_time
        )
        print(f"✅ Added: {delivery['email']} - {result}")
        time.sleep(0.1)  # Small delay
    
    print("🎯 Test data added! Check your Enhanced Activity page.")

if __name__ == '__main__':
    add_test_delivery_data()