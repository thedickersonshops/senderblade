#!/usr/bin/env python3
"""
NUCLEAR SMTP SERVER
Custom SMTP server that runs on ANY port and allows UNLIMITED spoofing
Deploy this on ANY RDP/VPS - no port 25 needed!
"""

import socket
import threading
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import time
import secrets

class NuclearSMTPServer:
    def __init__(self, host='0.0.0.0', port=2525):
        self.host = host
        self.port = port
        self.running = False
        
        # Gmail relay settings (change these)
        self.relay_host = 'smtp.gmail.com'
        self.relay_port = 587
        self.relay_user = 'timothykeeton.tk@gmail.com'
        self.relay_pass = 'YOUR_APP_PASSWORD'  # Change this!
        
    def start_server(self):
        """Start the nuclear SMTP server"""
        self.running = True
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"🔥 NUCLEAR SMTP SERVER STARTED!")
        print(f"📧 Host: {self.host}")
        print(f"🔌 Port: {self.port}")
        print(f"🚀 Ready for UNLIMITED spoofing!")
        print("-" * 50)
        
        while self.running:
            try:
                client_socket, address = server_socket.accept()
                print(f"📨 New connection from {address}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                print(f"❌ Server error: {e}")
                break
        
        server_socket.close()
    
    def handle_client(self, client_socket, address):
        """Handle SMTP client connection"""
        try:
            # Send SMTP greeting
            self.send_response(client_socket, "220 Nuclear SMTP Server Ready")
            
            mail_from = None
            rcpt_to = []
            data = ""
            in_data_mode = False
            
            while True:
                try:
                    request = client_socket.recv(1024).decode('utf-8').strip()
                    if not request:
                        break
                    
                    print(f"📥 {address}: {request}")
                    
                    # Handle SMTP commands
                    if request.upper().startswith('HELO') or request.upper().startswith('EHLO'):
                        self.send_response(client_socket, "250 Hello, ready for spoofing!")
                    
                    elif request.upper().startswith('MAIL FROM:'):
                        mail_from = self.extract_email(request)
                        self.send_response(client_socket, "250 OK")
                    
                    elif request.upper().startswith('RCPT TO:'):
                        rcpt_email = self.extract_email(request)
                        rcpt_to.append(rcpt_email)
                        self.send_response(client_socket, "250 OK")
                    
                    elif request.upper() == 'DATA':
                        self.send_response(client_socket, "354 Start mail input; end with <CRLF>.<CRLF>")
                        in_data_mode = True
                    
                    elif in_data_mode:
                        if request == '.':
                            # End of data - send the email!
                            success = self.send_spoofed_email(mail_from, rcpt_to, data)
                            if success:
                                self.send_response(client_socket, "250 OK: Message sent with spoofed sender!")
                            else:
                                self.send_response(client_socket, "550 Failed to send")
                            
                            # Reset for next email
                            mail_from = None
                            rcpt_to = []
                            data = ""
                            in_data_mode = False
                        else:
                            data += request + "\n"
                    
                    elif request.upper() == 'QUIT':
                        self.send_response(client_socket, "221 Bye")
                        break
                    
                    else:
                        self.send_response(client_socket, "250 OK")
                
                except Exception as e:
                    print(f"⚠️ Client error: {e}")
                    break
        
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        finally:
            client_socket.close()
    
    def send_response(self, client_socket, response):
        """Send SMTP response to client"""
        try:
            client_socket.send(f"{response}\r\n".encode('utf-8'))
        except:
            pass
    
    def extract_email(self, command):
        """Extract email address from SMTP command"""
        # Simple email extraction
        start = command.find('<')
        end = command.find('>')
        if start != -1 and end != -1:
            return command[start+1:end]
        
        # Fallback - split by space and find email-like string
        parts = command.split()
        for part in parts:
            if '@' in part:
                return part.strip('<>')
        
        return ""
    
    def send_spoofed_email(self, mail_from, rcpt_to, data):
        """Send email with spoofed sender through Gmail relay"""
        try:
            # Parse email data
            lines = data.split('\n')
            headers = {}
            body_start = 0
            
            # Extract headers
            for i, line in enumerate(lines):
                if line.strip() == '':
                    body_start = i + 1
                    break
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
            
            body = '\n'.join(lines[body_start:])
            
            # Create spoofed message
            msg = MIMEMultipart()
            
            # Use the spoofed From address
            spoofed_from = headers.get('from', mail_from)
            msg['From'] = spoofed_from
            msg['To'] = ', '.join(rcpt_to)
            msg['Subject'] = headers.get('subject', 'No Subject')
            
            # Add body
            if '<html>' in body.lower() or '<body>' in body.lower():
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send through Gmail relay
            with smtplib.SMTP(self.relay_host, self.relay_port) as server:
                server.starttls()
                server.login(self.relay_user, self.relay_pass)
                
                # Send with spoofed From but authenticated through Gmail
                server.send_message(msg, from_addr=self.relay_user, to_addrs=rcpt_to)
            
            print(f"✅ SPOOFED EMAIL SENT!")
            print(f"   From: {spoofed_from}")
            print(f"   To: {rcpt_to}")
            print(f"   Subject: {headers.get('subject', 'No Subject')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send spoofed email: {e}")
            return False

def main():
    print("🔥 NUCLEAR SMTP SERVER")
    print("=" * 40)
    print("This server allows UNLIMITED From address spoofing!")
    print("Deploy on ANY RDP/VPS - no port 25 needed!")
    print()
    
    # Configuration
    host = input("Enter server IP (or 0.0.0.0 for all): ").strip() or "0.0.0.0"
    port = input("Enter port (default 2525): ").strip() or "2525"
    
    try:
        port = int(port)
    except:
        port = 2525
    
    print(f"\n🚀 Starting Nuclear SMTP Server on {host}:{port}")
    print("\n📋 SMTP Settings for your app:")
    print(f"Host: {host if host != '0.0.0.0' else '[YOUR_RDP_IP]'}")
    print(f"Port: {port}")
    print("Username: (leave blank)")
    print("Password: (leave blank)")
    print("From: ANY EMAIL ADDRESS YOU WANT!")
    print("\n⚠️ Remember to update Gmail credentials in the code!")
    print("-" * 50)
    
    # Start server
    server = NuclearSMTPServer(host, port)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()