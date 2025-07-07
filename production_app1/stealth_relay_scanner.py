"""
Stealth Relay Scanner - Target smaller, less monitored networks
"""
import socket
import smtplib
import time
import random
from concurrent.futures import ThreadPoolExecutor

class StealthScanner:
    def __init__(self):
        self.found_relays = []
        
    def scan_small_targets(self):
        """Scan smaller, less monitored networks"""
        print("🥷 STEALTH SCANNER - SMALL TARGETS")
        print("=" * 40)
        
        # Small business/ISP ranges (less monitored)
        small_targets = [
            # Small ISP ranges
            ("66.0.0.0", "66.255.255.255", "Small ISPs"),
            ("67.0.0.0", "67.255.255.255", "Regional ISPs"),
            ("68.0.0.0", "68.255.255.255", "Local ISPs"),
            ("69.0.0.0", "69.255.255.255", "Cable ISPs"),
            
            # Small business hosting
            ("74.0.0.0", "74.255.255.255", "Small Hosting"),
            ("75.0.0.0", "75.255.255.255", "Regional Hosting"),
            ("76.0.0.0", "76.255.255.255", "Local Hosting"),
            
            # Community colleges (less security)
            ("161.0.0.0", "161.255.255.255", "Community Colleges"),
            ("162.0.0.0", "162.255.255.255", "Small Schools"),
            
            # Small government (city/county)
            ("170.0.0.0", "170.255.255.255", "Local Government"),
            ("171.0.0.0", "171.255.255.255", "City Networks"),
        ]
        
        all_relays = []
        for start_ip, end_ip, network_name in small_targets:
            print(f"🔍 {network_name}...")
            
            # Only test 50 random IPs per range (stealth)
            ips = self.generate_random_ips(start_ip, end_ip, 50)
            relays = self.scan_ips_stealth(ips)
            
            if relays:
                print(f"✅ Found {len(relays)} in {network_name}")
                all_relays.extend(relays)
            else:
                print(f"❌ None in {network_name}")
        
        print(f"\n🎯 Total: {len(all_relays)} relays")
        return all_relays
    
    def generate_random_ips(self, start_ip, end_ip, count):
        """Generate random IPs"""
        import ipaddress
        start = int(ipaddress.IPv4Address(start_ip))
        end = int(ipaddress.IPv4Address(end_ip))
        
        random_ints = [random.randint(start, end) for _ in range(count)]
        return [str(ipaddress.IPv4Address(ip)) for ip in random_ints]
    
    def scan_ips_stealth(self, ips):
        """Stealth scanning with delays"""
        relays = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:  # Low threads
            futures = [executor.submit(self.test_ip_stealth, ip) for ip in ips]
            
            for future in futures:
                try:
                    result = future.result(timeout=20)
                    if result:
                        relays.append(result)
                        print(f"🎯 FOUND: {result['ip']}")
                except:
                    pass
                
                # Stealth delay
                time.sleep(random.uniform(0.5, 2.0))
        
        return relays
    
    def test_ip_stealth(self, ip):
        """Stealth test single IP"""
        try:
            # Quick port check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, 25))
            sock.close()
            
            if result != 0:
                return None
            
            # SMTP test
            with smtplib.SMTP(ip, 25, timeout=10) as server:
                server.ehlo()
                server.mail("test@example.com")
                code, response = server.rcpt("test@gmail.com")
                
                if code == 250:
                    return {
                        'ip': ip,
                        'port': 25,
                        'type': 'small_relay',
                        'found_at': time.time()
                    }
            
            return None
        except:
            return None

if __name__ == "__main__":
    scanner = StealthScanner()
    relays = scanner.scan_small_targets()
    
    if relays:
        print(f"\n🎉 Found {len(relays)} small network relays!")
        for relay in relays:
            print(f"   {relay['ip']}:25")
    else:
        print("\n❌ No relays found - try different ranges")