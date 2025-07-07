#!/usr/bin/env python3
import socket
import smtplib
import ssl
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
import json

class PureServerScanner:
    def __init__(self):
        self.found_relays = []
        self.tested_count = 0
        self.lock = threading.Lock()
        
    def scan_random_servers(self):
        """Scan completely random server IPs"""
        print("🔍 PURE SERVER IP SCANNER")
        print("🌐 Scanning random server IPs worldwide")
        print("⚡ No specific targets - just finding servers")
        print("=" * 50)
        
        # Pure server IP ranges (hosting/datacenter ranges)
        server_ranges = [
            # Generic hosting ranges
            "1.0.0.0/8", "2.0.0.0/8", "5.0.0.0/8", "23.0.0.0/8", "31.0.0.0/8",
            "37.0.0.0/8", "41.0.0.0/8", "45.0.0.0/8", "46.0.0.0/8", "47.0.0.0/8",
            "58.0.0.0/8", "59.0.0.0/8", "60.0.0.0/8", "61.0.0.0/8", "62.0.0.0/8",
            "66.0.0.0/8", "67.0.0.0/8", "68.0.0.0/8", "69.0.0.0/8", "70.0.0.0/8",
            "71.0.0.0/8", "72.0.0.0/8", "73.0.0.0/8", "74.0.0.0/8", "75.0.0.0/8",
            "76.0.0.0/8", "77.0.0.0/8", "78.0.0.0/8", "79.0.0.0/8", "80.0.0.0/8",
            "81.0.0.0/8", "82.0.0.0/8", "83.0.0.0/8", "84.0.0.0/8", "85.0.0.0/8",
            "86.0.0.0/8", "87.0.0.0/8", "88.0.0.0/8", "89.0.0.0/8", "90.0.0.0/8",
            "91.0.0.0/8", "92.0.0.0/8", "93.0.0.0/8", "94.0.0.0/8", "95.0.0.0/8",
            "101.0.0.0/8", "103.0.0.0/8", "106.0.0.0/8", "110.0.0.0/8", "111.0.0.0/8",
            "112.0.0.0/8", "113.0.0.0/8", "114.0.0.0/8", "115.0.0.0/8", "116.0.0.0/8",
            "117.0.0.0/8", "118.0.0.0/8", "119.0.0.0/8", "120.0.0.0/8", "121.0.0.0/8",
            "173.0.0.0/8", "174.0.0.0/8", "175.0.0.0/8", "176.0.0.0/8", "177.0.0.0/8",
            "178.0.0.0/8", "179.0.0.0/8", "180.0.0.0/8", "181.0.0.0/8", "182.0.0.0/8",
            "183.0.0.0/8", "184.0.0.0/8", "185.0.0.0/8", "186.0.0.0/8", "187.0.0.0/8",
            "188.0.0.0/8", "189.0.0.0/8", "190.0.0.0/8", "193.0.0.0/8", "194.0.0.0/8",
            "195.0.0.0/8", "196.0.0.0/8", "197.0.0.0/8", "200.0.0.0/8", "201.0.0.0/8",
            "202.0.0.0/8", "203.0.0.0/8", "210.0.0.0/8", "211.0.0.0/8", "212.0.0.0/8",
            "213.0.0.0/8", "217.0.0.0/8", "218.0.0.0/8", "219.0.0.0/8", "220.0.0.0/8",
        ]
        
        # SMTP ports to test
        smtp_ports = [25, 587, 465, 2525, 26]
        
        # Start multiple scanner threads
        for i in range(3):
            scanner_thread = threading.Thread(target=self.scanner_worker, args=(i, server_ranges, smtp_ports))
            scanner_thread.daemon = True
            scanner_thread.start()
        
        # Monitor progress
        while True:
            time.sleep(30)
            with self.lock:
                print(f"📊 Progress: {self.tested_count} IPs tested, {len(self.found_relays)} relays found")
                if len(self.found_relays) > 0:
                    print(f"🎯 Latest relays: {self.found_relays[-3:]}")
    
    def scanner_worker(self, worker_id, server_ranges, smtp_ports):
        """Worker thread for scanning"""
        print(f"🔍 Scanner {worker_id} started")
        
        while True:
            try:
                # Pick random range
                ip_range = random.choice(server_ranges)
                
                # Generate random IPs
                ips = self.generate_random_ips(ip_range, 100)
                
                # Test IPs
                self.test_ip_batch(ips, smtp_ports, worker_id)
                
                # Small delay
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Scanner {worker_id} error: {e}")
                time.sleep(30)
    
    def generate_random_ips(self, ip_range, count):
        """Generate random IPs from range"""
        import ipaddress
        
        try:
            network = ipaddress.IPv4Network(ip_range, strict=False)
            ips = []
            
            for _ in range(count):
                random_int = random.randint(0, min(65535, network.num_addresses - 1))
                ip = str(network.network_address + random_int)
                ips.append(ip)
            
            return ips
        except:
            return []
    
    def test_ip_batch(self, ips, ports, worker_id):
        """Test batch of IPs"""
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            
            for ip in ips:
                for port in ports:
                    future = executor.submit(self.test_server_ip, ip, port, worker_id)
                    futures.append(future)
            
            for future in futures:
                try:
                    future.result(timeout=10)
                except:
                    pass
    
    def test_server_ip(self, ip, port, worker_id):
        """Test single server IP"""
        try:
            with self.lock:
                self.tested_count += 1
            
            # Quick port check
            if not self.is_port_open(ip, port, timeout=3):
                return
            
            # Test SMTP relay
            if self.test_smtp_relay(ip, port):
                relay_info = f"{ip}:{port}"
                
                with self.lock:
                    if relay_info not in self.found_relays:
                        self.found_relays.append(relay_info)
                        print(f"🎯 SCANNER {worker_id} FOUND: {relay_info}")
                        
                        # Save progress
                        self.save_progress()
                        
                        # Keep only last 100 relays
                        if len(self.found_relays) > 100:
                            self.found_relays = self.found_relays[-100:]
        except:
            pass
    
    def is_port_open(self, ip, port, timeout=3):
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def test_smtp_relay(self, ip, port):
        """Test if server allows relay"""
        try:
            if port == 465:
                # SSL
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with smtplib.SMTP_SSL(ip, port, context=context, timeout=8) as server:
                    server.ehlo()
                    server.mail('test@example.com')
                    code, response = server.rcpt('test@gmail.com')
                    return code == 250
                    
            elif port == 587:
                # STARTTLS
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
                    return code == 250
                    
            else:
                # Plain SMTP
                with smtplib.SMTP(ip, port, timeout=8) as server:
                    server.ehlo()
                    server.mail('test@example.com')
                    code, response = server.rcpt('test@gmail.com')
                    return code == 250
                    
        except:
            return False
    
    def save_progress(self):
        """Save progress to file"""
        try:
            data = {
                'timestamp': time.time(),
                'tested_count': self.tested_count,
                'found_relays': self.found_relays,
                'total_relays': len(self.found_relays)
            }
            
            with open('server_relays_found.json', 'w') as f:
                json.dump(data, f, indent=2)
                
        except:
            pass

if __name__ == "__main__":
    print("🔍 PURE SERVER IP SCANNER")
    print("🌐 Scanning random server IPs worldwide")
    print("⚡ No targeting - just finding open servers")
    print("🎯 Looking for misconfigured mail servers")
    print()
    
    scanner = PureServerScanner()
    
    try:
        scanner.scan_random_servers()
    except KeyboardInterrupt:
        print(f"\n🛑 Scanner stopped")
        print(f"📊 Final stats: {scanner.tested_count} IPs tested, {len(scanner.found_relays)} relays found")
        
        if scanner.found_relays:
            print(f"🎯 Found relays:")
            for relay in scanner.found_relays:
                print(f"   {relay}")