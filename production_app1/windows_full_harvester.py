"""
Windows RDP Full Harvester - For maximum relay collection
Run this on your second Windows RDP server
"""
import socket
import smtplib
import time
import random
import threading
import json
from concurrent.futures import ThreadPoolExecutor
import requests

class WindowsFullHarvester:
    def __init__(self):
        self.found_relays = []
        self.tested_count = 0
        self.lock = threading.Lock()
        self.start_time = time.time()
        
    def full_harvest_operation(self):
        """Complete relay harvesting operation"""
        print("🏢 WINDOWS RDP FULL HARVESTER - MAXIMUM CAPACITY")
        print("=" * 70)
        print(f"🖥️  Scanner IP: {self.get_my_ip()}")
        print(f"⏰ Started: {time.ctime()}")
        print("=" * 70)
        
        all_relays = []
        
        # Phase 1: Corporate Networks
        print("\n🏢 PHASE 1: CORPORATE NETWORK HARVEST")
        corporate_relays = self.harvest_corporate_networks()
        all_relays.extend(corporate_relays)
        
        # Phase 2: Extended University Networks
        print("\n🎓 PHASE 2: EXTENDED UNIVERSITY HARVEST")
        university_relays = self.harvest_extended_universities()
        all_relays.extend(university_relays)
        
        # Phase 3: Government Networks
        print("\n🏛️  PHASE 3: GOVERNMENT NETWORK HARVEST")
        gov_relays = self.harvest_government_networks()
        all_relays.extend(gov_relays)
        
        # Phase 4: International Networks
        print("\n🌍 PHASE 4: INTERNATIONAL NETWORK HARVEST")
        intl_relays = self.harvest_international_networks()
        all_relays.extend(intl_relays)
        
        # Final results
        elapsed = time.time() - self.start_time
        print(f"\n🎯 FULL HARVEST COMPLETE!")
        print(f"⏱️  Time elapsed: {elapsed/60:.1f} minutes")
        print(f"📊 Total relays: {len(all_relays)}")
        print(f"🧪 IPs tested: {self.tested_count}")
        print(f"💰 Cost: $0")
        
        return all_relays
    
    def harvest_corporate_networks(self):
        """Harvest corporate network relays"""
        corporate_targets = [
            # Amazon AWS ranges
            ("52.0.0.0", "52.255.255.255", "Amazon AWS"),
            ("54.0.0.0", "54.255.255.255", "Amazon AWS Extended"),
            
            # Microsoft Azure ranges
            ("104.0.0.0", "104.255.255.255", "Microsoft Azure"),
            ("40.0.0.0", "40.255.255.255", "Microsoft Corporate"),
            
            # Google Cloud ranges
            ("35.0.0.0", "35.255.255.255", "Google Cloud"),
            ("34.0.0.0", "34.255.255.255", "Google Corporate"),
            
            # Facebook/Meta ranges
            ("31.13.0.0", "31.13.255.255", "Facebook/Meta"),
            ("157.240.0.0", "157.240.255.255", "Facebook Extended"),
            
            # Other major corporations
            ("199.0.0.0", "199.255.255.255", "Corporate Networks"),
            ("208.0.0.0", "208.255.255.255", "Enterprise Networks"),
        ]
        
        return self.scan_network_ranges(corporate_targets, "Corporate", ips_per_range=500)
    
    def harvest_extended_universities(self):
        """Harvest extended university networks"""
        university_targets = [
            # Extended Class A university blocks
            ("128.0.0.0", "128.255.255.255", "University Block 128"),
            ("129.0.0.0", "129.255.255.255", "University Block 129"),
            ("130.0.0.0", "130.255.255.255", "University Block 130"),
            ("131.0.0.0", "131.255.255.255", "University Block 131"),
            ("132.0.0.0", "132.255.255.255", "University Block 132"),
            
            # Research networks
            ("192.12.0.0", "192.12.255.255", "Research Networks"),
            ("198.32.0.0", "198.32.255.255", "Educational Networks"),
            ("204.0.0.0", "204.255.255.255", "Academic Networks"),
        ]
        
        return self.scan_network_ranges(university_targets, "University", ips_per_range=800)
    
    def harvest_government_networks(self):
        """Harvest government network relays"""
        gov_targets = [
            # US Government ranges
            ("192.0.0.0", "192.255.255.255", "Government Networks"),
            ("198.0.0.0", "198.255.255.255", "Federal Networks"),
            ("205.0.0.0", "205.255.255.255", "Military Networks"),
            ("140.0.0.0", "140.255.255.255", "Defense Networks"),
        ]
        
        return self.scan_network_ranges(gov_targets, "Government", ips_per_range=300)
    
    def harvest_international_networks(self):
        """Harvest international network relays"""
        intl_targets = [
            # European networks
            ("80.0.0.0", "80.255.255.255", "European Networks"),
            ("81.0.0.0", "81.255.255.255", "European Extended"),
            
            # Asian networks
            ("202.0.0.0", "202.255.255.255", "Asian Networks"),
            ("203.0.0.0", "203.255.255.255", "Asian Extended"),
            
            # Other international
            ("200.0.0.0", "200.255.255.255", "Latin American"),
            ("196.0.0.0", "196.255.255.255", "African Networks"),
        ]
        
        return self.scan_network_ranges(intl_targets, "International", ips_per_range=400)
    
    def scan_network_ranges(self, targets, category, ips_per_range=500):
        """Scan multiple network ranges"""
        all_relays = []
        
        for start_ip, end_ip, network_name in targets:
            print(f"\n🔍 Scanning {network_name}...")
            
            # Generate random IPs in range
            ips = self.generate_random_ips_in_range(start_ip, end_ip, ips_per_range)
            
            # Scan with high concurrency
            relays = self.scan_ips_parallel(ips, network_name, max_workers=150)
            
            if relays:
                print(f"✅ Found {len(relays)} relays in {network_name}")
                all_relays.extend(relays)
                
                # Save progress
                self.save_relays_json(all_relays, f"full_harvest_{category.lower()}_progress.json")
            else:
                print(f"❌ No relays found in {network_name}")
        
        return all_relays
    
    def generate_random_ips_in_range(self, start_ip, end_ip, count):
        """Generate random IPs in range"""
        import ipaddress
        
        start = int(ipaddress.IPv4Address(start_ip))
        end = int(ipaddress.IPv4Address(end_ip))
        
        # Generate unique random integers
        random_ints = set()
        while len(random_ints) < count and len(random_ints) < (end - start):
            random_ints.add(random.randint(start, end))
        
        return [str(ipaddress.IPv4Address(ip_int)) for ip_int in random_ints]
    
    def scan_ips_parallel(self, ips, network_name, max_workers=150):
        """High-concurrency IP scanning"""
        relays = []
        
        print(f"⚡ Testing {len(ips)} IPs in {network_name} with {max_workers} threads...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.test_smtp_relay, ip, network_name) for ip in ips]
            
            for future in futures:
                try:
                    result = future.result(timeout=15)
                    if result:
                        relays.append(result)
                        with self.lock:
                            self.found_relays.append(result)
                        print(f"🎯 RELAY: {result['ip']} ({network_name})")
                except:
                    pass
                
                with self.lock:
                    self.tested_count += 1
                    if self.tested_count % 100 == 0:
                        elapsed = time.time() - self.start_time
                        rate = self.tested_count / elapsed * 60
                        print(f"📊 Tested {self.tested_count} IPs, found {len(self.found_relays)} relays ({rate:.0f} IPs/min)")
        
        return relays
    
    def test_smtp_relay(self, ip, network_type):
        """Test single IP for SMTP relay"""
        try:
            # Quick port check
            if not self.is_port_open(ip, 25, timeout=3):
                return None
            
            # SMTP relay test
            with smtplib.SMTP(ip, 25, timeout=8) as server:
                server.ehlo()
                
                # Test external relay capability
                server.mail("test@example.com")
                code, response = server.rcpt("test@gmail.com")
                
                if code == 250:
                    return {
                        'ip': ip,
                        'port': 25,
                        'type': f'{network_type.lower()}_relay',
                        'network': network_type,
                        'found_at': time.time(),
                        'scanner': 'windows_full',
                        'status': 'working'
                    }
            
            return None
            
        except:
            return None
    
    def is_port_open(self, ip, port, timeout=3):
        """Port connectivity check"""
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
                'scanner': 'windows_full',
                'scanner_ip': self.get_my_ip(),
                'timestamp': time.time(),
                'total_relays': len(relays),
                'tested_count': self.tested_count,
                'elapsed_minutes': (time.time() - self.start_time) / 60,
                'relays': relays
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"💾 Saved {len(relays)} relays to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving: {e}")
    
    def test_random_relays(self, relays, count=5):
        """Test random relays to verify they work"""
        if not relays:
            return
            
        print(f"\n🧪 Testing {min(count, len(relays))} random relays...")
        
        test_relays = random.sample(relays, min(count, len(relays)))
        
        for i, relay in enumerate(test_relays, 1):
            print(f"Testing relay {i}/{len(test_relays)}: {relay['ip']}")
            
            try:
                with smtplib.SMTP(relay['ip'], 25, timeout=10) as server:
                    server.ehlo()
                    
                    msg = f"""From: test@corporate.com
To: your_test@gmail.com
Subject: Full Harvester Test - {relay['network']}

This email was sent through {relay['network']} relay {relay['ip']}
Scanner: Windows RDP Full Harvester
Time: {time.ctime()}
"""
                    
                    server.sendmail("test@corporate.com", ["your_test@gmail.com"], msg)
                    print(f"✅ Relay {relay['ip']} verified working")
                    
            except Exception as e:
                print(f"❌ Relay {relay['ip']} failed: {e}")

def run_windows_full_harvest():
    """Main function for Windows RDP full harvesting"""
    print("🔥 WINDOWS RDP FULL HARVESTER STARTING")
    print("🏢 Maximum capacity relay collection")
    print("⏱️  Estimated time: 2-4 hours")
    print()
    
    harvester = WindowsFullHarvester()
    
    # Full harvest operation
    relays = harvester.full_harvest_operation()
    
    if relays:
        # Test some relays
        harvester.test_random_relays(relays, 10)
        
        # Save final results
        harvester.save_relays_json(relays, f"windows_full_harvest_final_{int(time.time())}.json")
        
        # Generate summary
        print(f"\n🎉 FULL HARVEST COMPLETE!")
        print(f"📧 Total relays: {len(relays)}")
        print(f"🧪 IPs tested: {harvester.tested_count}")
        print(f"⏱️  Total time: {(time.time() - harvester.start_time)/60:.1f} minutes")
        print(f"💰 Cost: $0")
        print(f"🚀 Capacity: UNLIMITED")
        
        # Categorize relays
        categories = {}
        for relay in relays:
            network = relay.get('network', 'Unknown')
            categories[network] = categories.get(network, 0) + 1
        
        print(f"\n📊 RELAY BREAKDOWN:")
        for network, count in categories.items():
            print(f"   {network}: {count} relays")
        
    else:
        print(f"\n❌ No relays found in full harvest")
        print(f"🔄 Try different IP ranges or scan times")
    
    return relays

if __name__ == "__main__":
    print("🖥️  WINDOWS RDP FULL HARVESTER")
    print("🌍 Targeting Global Networks")
    print("⚡ Maximum relay collection")
    print()
    
    # Run the full harvest
    relays = run_windows_full_harvest()
    
    print(f"\n💀 Email cartel can't stop global relay network!")
    print(f"🔥 Full harvest complete - check results files!")
    
    # Keep window open
    input("\nPress Enter to exit...")