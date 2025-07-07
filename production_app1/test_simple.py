#!/usr/bin/env python3

# Simple test to check if basic campaign sending works
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_campaign():
    try:
        # Connect to database
        conn = sqlite3.connect('simple.db')
        cursor = conn.cursor()
        
        # Get a test campaign
        cursor.execute('''
            SELECT c.*, l.name as list_name, s.name as smtp_name, s.host, s.port, s.username, s.password, s.from_email, s.from_name
            FROM campaigns c
            JOIN lists l ON c.list_id = l.id
            JOIN smtp_servers s ON c.smtp_id = s.id
            WHERE c.status = 'draft'
            LIMIT 1
        ''')
        
        campaign = cursor.fetchone()
        if not campaign:
            print("No draft campaigns found")
            return
            
        print(f"Found campaign: {campaign}")
        
        # Get contacts for this campaign
        cursor.execute('SELECT email, first_name, last_name FROM contacts WHERE list_id = ?', (campaign[2],))
        contacts = cursor.fetchall()
        
        print(f"Found {len(contacts)} contacts")
        
        if contacts:
            contact = contacts[0]  # Test with first contact
            print(f"Testing with contact: {contact}")
            
            # Simple email sending test
            subject = campaign[4]  # subject
            body = campaign[5]     # body
            
            # Replace variables
            if contact[1]:  # first_name
                subject = subject.replace('{first_name}', contact[1])
                body = body.replace('{first_name}', contact[1])
            if contact[2]:  # last_name
                subject = subject.replace('{last_name}', contact[2])
                body = body.replace('{last_name}', contact[2])
            
            subject = subject.replace('{email}', contact[0])
            body = body.replace('{email}', contact[0])
            
            print(f"Final subject: {subject}")
            print(f"Final body: {body[:100]}...")
            
            print("Basic processing works!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    test_campaign()