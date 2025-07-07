#!/usr/bin/env python3
"""
RDP Mail Server Setup
Turn your RDP server into a mail server
"""

import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_rdp_ports(rdp_ip):
    """Test which ports are open on RDP server"""
    print(f"🔍 Testing ports on RDP server: {rdp_ip}")
    
    ports_to_test = [25, 587, 465, 2525, 1025]
    open_ports = []
    
    for port in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((rdp_ip, port))
            sock.close()
            
            if result == 0:
                print(f"✅ Port {port}: OPEN")
                open_ports.append(port)
            else:
                print(f"❌ Port {port}: Closed/Filtered")
        except Exception as e:
            print(f"⚠️ Port {port}: Error - {e}")
    
    return open_ports

def create_python_smtp_server():
    """Create a Python-based SMTP server that runs on RDP"""
    
    server_code = '''
import smtpd
import asyncore
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

class CustomSMTPServer(smtpd.SMTPServer):
    """Custom SMTP server that allows any From address"""
    
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        print(f"📧 Sending email from {mailfrom} to {rcpttos}")
        
        # Parse the email data
        lines = data.decode().split('\\n')
        
        # Extract headers and body
        headers = {}
        body_start = 0
        
        for i, line in enumerate(lines):
            if line.strip() == '':
                body_start = i + 1
                break
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        body = '\\n'.join(lines[body_start:])
        
        # Send through external SMTP (Gmail as relay)
        try:
            # Use Gmail as relay but with custom From header
            msg = MIMEMultipart()
            msg['From'] = headers.get('from', mailfrom)
            msg['To'] = ', '.join(rcpttos)
            msg['Subject'] = headers.get('subject', 'No Subject')
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send through Gmail SMTP
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login('timothykeeton.tk@gmail.com', 'YOUR_APP_PASSWORD')
                server.send_message(msg)
            
            print(f"✅ Email sent successfully!")
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

def start_smtp_server():
    """Start the custom SMTP server"""
    print("🚀 Starting custom SMTP server on port 2525...")
    
    server = CustomSMTPServer(('0.0.0.0', 2525), None)
    print("✅ SMTP Server running on port 2525")
    print("📧 SMTP Settings:")
    print("Host: YOUR_RDP_IP")
    print("Port: 2525")
    print("Username: (none)")
    print("Password: (none)")
    print("From: ANY EMAIL ADDRESS")
    
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print("🛑 Server stopped")

if __name__ == "__main__":
    start_smtp_server()
'''
    
    return server_code

def main():
    print("🔥 RDP MAIL SERVER SETUP")
    print("=" * 40)
    
    rdp_ip = input("Enter your RDP server IP: ").strip()
    
    if not rdp_ip:
        print("❌ Please provide RDP IP address")
        return
    
    # Test ports
    open_ports = test_rdp_ports(rdp_ip)
    
    if not open_ports:
        print("⚠️ No standard mail ports open")
        print("💡 We'll use a custom port (2525)")
    
    # Generate Python SMTP server code
    server_code = create_python_smtp_server()
    
    # Save to file
    with open('rdp_smtp_server.py', 'w') as f:
        f.write(server_code)
    
    print("\n🎯 NEXT STEPS:")
    print("1. Copy 'rdp_smtp_server.py' to your RDP server")
    print("2. Install Python on RDP server")
    print("3. Run: python rdp_smtp_server.py")
    print("4. Use these SMTP settings in your app:")
    print(f"   Host: {rdp_ip}")
    print("   Port: 2525")
    print("   Username: (leave blank)")
    print("   Password: (leave blank)")
    print("   From: ANY EMAIL ADDRESS")
    
    print("\n🔥 This will allow UNLIMITED From address spoofing!")

if __name__ == "__main__":
    main()