"""
Universal Relay Hunter - Find ANY open relay ANYWHERE
Powerful brute force scanner avoiding only government networks
"""
import socket
import smtplib
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor

class UniversalRelayHunter:
    def __init__(self):
        self.found_relays = []
        self.tested_count = 0
        self.lock = threading.Lock()
        
        # Government IP ranges to AVOID
        self.government_ranges = [
            "192.0.0.0/8",      # US Government
            "198.0.0.0/8",      # Federal networks
            "205.0.0.0/8",      # Military
            "140.0.0.0/8",      # Defense
            "144.0.0.0/8",      # Military
            "26.0.0.0/8",       # Defense
            "6.0.0.0/8",        # Army
            "7.0.0.0/8",        # Defense
            "11.0.0.0/8",       # Defense
            "21.0.0.0/8",       # Defense
            "22.0.0.0/8",       # Defense
            "25.0.0.0/8",       # Defense
            "28.0.0.0/8",       # Defense
            "29.0.0.0/8",       # Defense
            "30.0.0.0/8",       # Defense
        ]
    
    def hunt_everywhere(self):
        """Hunt for relays in ALL non-government networks"""
        print("🔥 UNIVERSAL RELAY HUNTER - FIND ANYTHING ANYWHERE")
        print("=" * 60)
        print("⚠️  AVOIDING: Government/Military networks")
        print("🎯 TARGETING: Everything else on the internet")
        print("=" * 60)
        
        # Massive IP ranges to scan (non-government)
        hunting_ranges = [
            # ISP and hosting ranges
            ("1.0.0.0", "1.255.255.255", "APNIC Region"),
            ("2.0.0.0", "2.255.255.255", "RIPE Region"),
            ("5.0.0.0", "5.255.255.255", "RIPE Region"),
            ("8.0.0.0", "8.255.255.255", "Level3/Google"),
            ("12.0.0.0", "12.255.255.255", "AT&T"),
            ("13.0.0.0", "13.255.255.255", "Xerox/Facebook"),
            ("15.0.0.0", "15.255.255.255", "HP Enterprise"),
            ("16.0.0.0", "16.255.255.255", "HP Enterprise"),
            ("17.0.0.0", "17.255.255.255", "Apple"),
            ("18.0.0.0", "18.255.255.255", "MIT"),
            ("19.0.0.0", "19.255.255.255", "Ford"),
            ("20.0.0.0", "20.255.255.255", "CSC"),
            ("23.0.0.0", "23.255.255.255", "Akamai"),
            ("24.0.0.0", "24.255.255.255", "Cable/DSL"),
            ("31.0.0.0", "31.255.255.255", "RIPE Region"),
            ("32.0.0.0", "32.255.255.255", "AT&T"),
            ("34.0.0.0", "34.255.255.255", "Google Cloud"),
            ("35.0.0.0", "35.255.255.255", "Google Cloud"),
            ("36.0.0.0", "36.255.255.255", "Stanford"),
            ("37.0.0.0", "37.255.255.255", "RIPE Region"),
            ("38.0.0.0", "38.255.255.255", "PSI"),
            ("39.0.0.0", "39.255.255.255", "RIPE Region"),
            ("40.0.0.0", "40.255.255.255", "Microsoft Azure"),
            ("41.0.0.0", "41.255.255.255", "AfriNIC"),
            ("42.0.0.0", "42.255.255.255", "APNIC"),
            ("43.0.0.0", "43.255.255.255", "APNIC"),
            ("44.0.0.0", "44.255.255.255", "Amateur Radio"),
            ("45.0.0.0", "45.255.255.255", "RIPE Region"),
            ("46.0.0.0", "46.255.255.255", "RIPE Region"),
            ("47.0.0.0", "47.255.255.255", "RIPE Region"),
            ("49.0.0.0", "49.255.255.255", "APNIC"),
            ("50.0.0.0", "50.255.255.255", "ARIN"),
            ("51.0.0.0", "51.255.255.255", "RIPE Region"),
            ("52.0.0.0", "52.255.255.255", "Amazon AWS"),
            ("54.0.0.0", "54.255.255.255", "Amazon AWS"),
            ("58.0.0.0", "58.255.255.255", "APNIC"),
            ("59.0.0.0", "59.255.255.255", "APNIC"),
            ("60.0.0.0", "60.255.255.255", "APNIC"),
            ("61.0.0.0", "61.255.255.255", "APNIC"),
            ("62.0.0.0", "62.255.255.255", "RIPE Region"),
            ("63.0.0.0", "63.255.255.255", "ARIN"),
            ("64.0.0.0", "64.255.255.255", "ARIN"),
            ("65.0.0.0", "65.255.255.255", "ARIN"),
            ("66.0.0.0", "66.255.255.255", "ARIN"),
            ("67.0.0.0", "67.255.255.255", "ARIN"),
            ("68.0.0.0", "68.255.255.255", "ARIN"),
            ("69.0.0.0", "69.255.255.255", "ARIN"),
            ("70.0.0.0", "70.255.255.255", "ARIN"),
            ("71.0.0.0", "71.255.255.255", "ARIN"),
            ("72.0.0.0", "72.255.255.255", "ARIN"),
            ("73.0.0.0", "73.255.255.255", "ARIN"),
            ("74.0.0.0", "74.255.255.255", "ARIN"),
            ("75.0.0.0", "75.255.255.255", "ARIN"),
            ("76.0.0.0", "76.255.255.255", "ARIN"),
            ("77.0.0.0", "77.255.255.255", "RIPE Region"),
            ("78.0.0.0", "78.255.255.255", "RIPE Region"),
            ("79.0.0.0", "79.255.255.255", "RIPE Region"),
            ("80.0.0.0", "80.255.255.255", "RIPE Region"),
            ("81.0.0.0", "81.255.255.255", "RIPE Region"),
            ("82.0.0.0", "82.255.255.255", "RIPE Region"),
            ("83.0.0.0", "83.255.255.255", "RIPE Region"),
            ("84.0.0.0", "84.255.255.255", "RIPE Region"),
            ("85.0.0.0", "85.255.255.255", "RIPE Region"),
            ("86.0.0.0", "86.255.255.255", "RIPE Region"),
            ("87.0.0.0", "87.255.255.255", "RIPE Region"),
            ("88.0.0.0", "88.255.255.255", "RIPE Region"),
            ("89.0.0.0", "89.255.255.255", "RIPE Region"),
            ("90.0.0.0", "90.255.255.255", "RIPE Region"),
            ("91.0.0.0", "91.255.255.255", "RIPE Region"),
            ("92.0.0.0", "92.255.255.255", "RIPE Region"),
            ("93.0.0.0", "93.255.255.255", "RIPE Region"),
            ("94.0.0.0", "94.255.255.255", "RIPE Region"),
            ("95.0.0.0", "95.255.255.255", "RIPE Region"),
            ("96.0.0.0", "96.255.255.255", "ARIN"),
            ("97.0.0.0", "97.255.255.255", "ARIN"),
            ("98.0.0.0", "98.255.255.255", "ARIN"),
            ("99.0.0.0", "99.255.255.255", "Amazon"),
            ("100.0.0.0", "100.255.255.255", "ARIN"),
            ("101.0.0.0", "101.255.255.255", "APNIC"),
            ("102.0.0.0", "102.255.255.255", "AfriNIC"),
            ("103.0.0.0", "103.255.255.255", "APNIC"),
            ("104.0.0.0", "104.255.255.255", "Microsoft Azure"),
            ("105.0.0.0", "105.255.255.255", "AfriNIC"),
            ("106.0.0.0", "106.255.255.255", "APNIC"),
            ("107.0.0.0", "107.255.255.255", "ARIN"),
            ("108.0.0.0", "108.255.255.255", "ARIN"),
            ("109.0.0.0", "109.255.255.255", "RIPE Region"),
            ("110.0.0.0", "110.255.255.255", "APNIC"),
            ("111.0.0.0", "111.255.255.255", "APNIC"),
            ("112.0.0.0", "112.255.255.255", "APNIC"),
            ("113.0.0.0", "113.255.255.255", "APNIC"),
            ("114.0.0.0", "114.255.255.255", "APNIC"),
            ("115.0.0.0", "115.255.255.255", "APNIC"),
            ("116.0.0.0", "116.255.255.255", "APNIC"),
            ("117.0.0.0", "117.255.255.255", "APNIC"),
            ("118.0.0.0", "118.255.255.255", "APNIC"),
            ("119.0.0.0", "119.255.255.255", "APNIC"),
            ("120.0.0.0", "120.255.255.255", "APNIC"),
            ("121.0.0.0", "121.255.255.255", "APNIC"),
            ("122.0.0.0", "122.255.255.255", "APNIC"),
            ("123.0.0.0", "123.255.255.255", "APNIC"),
            ("124.0.0.0", "124.255.255.255", "APNIC"),
            ("125.0.0.0", "125.255.255.255", "APNIC"),
            ("126.0.0.0", "126.255.255.255", "APNIC"),
            ("128.0.0.0", "128.255.255.255", "Universities"),
            ("129.0.0.0", "129.255.255.255", "Universities"),
            ("130.0.0.0", "130.255.255.255", "Universities"),
            ("131.0.0.0", "131.255.255.255", "Universities"),
            ("132.0.0.0", "132.255.255.255", "Universities"),
            ("134.0.0.0", "134.255.255.255", "Universities"),
            ("135.0.0.0", "135.255.255.255", "Universities"),
            ("136.0.0.0", "136.255.255.255", "Universities"),
            ("137.0.0.0", "137.255.255.255", "Universities"),
            ("138.0.0.0", "138.255.255.255", "Universities"),
            ("139.0.0.0", "139.255.255.255", "Universities"),
            ("141.0.0.0", "141.255.255.255", "Universities"),
            ("142.0.0.0", "142.255.255.255", "Universities"),
            ("143.0.0.0", "143.255.255.255", "Universities"),
            ("145.0.0.0", "145.255.255.255", "RIPE Region"),
            ("146.0.0.0", "146.255.255.255", "RIPE Region"),
            ("147.0.0.0", "147.255.255.255", "RIPE Region"),
            ("148.0.0.0", "148.255.255.255", "Universities"),
            ("149.0.0.0", "149.255.255.255", "Universities"),
            ("150.0.0.0", "150.255.255.255", "APNIC"),
            ("151.0.0.0", "151.255.255.255", "RIPE Region"),
            ("152.0.0.0", "152.255.255.255", "Universities"),
            ("153.0.0.0", "153.255.255.255", "APNIC"),
            ("154.0.0.0", "154.255.255.255", "AfriNIC"),
            ("155.0.0.0", "155.255.255.255", "Universities"),
            ("156.0.0.0", "156.255.255.255", "Universities"),
            ("157.0.0.0", "157.255.255.255", "Universities"),
            ("158.0.0.0", "158.255.255.255", "Universities"),
            ("159.0.0.0", "159.255.255.255", "Universities"),
            ("160.0.0.0", "160.255.255.255", "Universities"),
            ("161.0.0.0", "161.255.255.255", "Universities"),
            ("162.0.0.0", "162.255.255.255", "Universities"),
            ("163.0.0.0", "163.255.255.255", "APNIC"),
            ("164.0.0.0", "164.255.255.255", "Universities"),
            ("165.0.0.0", "165.255.255.255", "Universities"),
            ("166.0.0.0", "166.255.255.255", "Universities"),
            ("167.0.0.0", "167.255.255.255", "Universities"),
            ("168.0.0.0", "168.255.255.255", "Universities"),
            ("169.0.0.0", "169.255.255.255", "Link Local"),
            ("173.0.0.0", "173.255.255.255", "ARIN"),
            ("174.0.0.0", "174.255.255.255", "ARIN"),
            ("175.0.0.0", "175.255.255.255", "APNIC"),
            ("176.0.0.0", "176.255.255.255", "RIPE Region"),
            ("177.0.0.0", "177.255.255.255", "LACNIC"),
            ("178.0.0.0", "178.255.255.255", "RIPE Region"),
            ("179.0.0.0", "179.255.255.255", "LACNIC"),
            ("180.0.0.0", "180.255.255.255", "APNIC"),
            ("181.0.0.0", "181.255.255.255", "LACNIC"),
            ("182.0.0.0", "182.255.255.255", "APNIC"),
            ("183.0.0.0", "183.255.255.255", "APNIC"),
            ("184.0.0.0", "184.255.255.255", "ARIN"),
            ("185.0.0.0", "185.255.255.255", "RIPE Region"),
            ("186.0.0.0", "186.255.255.255", "LACNIC"),
            ("187.0.0.0", "187.255.255.255", "LACNIC"),
            ("188.0.0.0", "188.255.255.255", "RIPE Region"),
            ("189.0.0.0", "189.255.255.255", "LACNIC"),
            ("190.0.0.0", "190.255.255.255", "LACNIC"),
            ("191.0.0.0", "191.255.255.255", "LACNIC"),
            ("193.0.0.0", "193.255.255.255", "RIPE Region"),
            ("194.0.0.0", "194.255.255.255", "RIPE Region"),
            ("195.0.0.0", "195.255.255.255", "RIPE Region"),
            ("196.0.0.0", "196.255.255.255", "AfriNIC"),
            ("197.0.0.0", "197.255.255.255", "AfriNIC"),
            ("199.0.0.0", "199.255.255.255", "ARIN"),
            ("200.0.0.0", "200.255.255.255", "LACNIC"),
            ("201.0.0.0", "201.255.255.255", "LACNIC"),
            ("202.0.0.0", "202.255.255.255", "APNIC"),
            ("203.0.0.0", "203.255.255.255", "APNIC"),
            ("206.0.0.0", "206.255.255.255", "ARIN"),
            ("207.0.0.0", "207.255.255.255", "ARIN"),
            ("208.0.0.0", "208.255.255.255", "ARIN"),
            ("209.0.0.0", "209.255.255.255", "ARIN"),
            ("210.0.0.0", "210.255.255.255", "APNIC"),
            ("211.0.0.0", "211.255.255.255", "APNIC"),
            ("212.0.0.0", "212.255.255.255", "RIPE Region"),
            ("213.0.0.0", "213.255.255.255", "RIPE Region"),
            ("214.0.0.0", "214.255.255.255", "ARIN"),
            ("215.0.0.0", "215.255.255.255", "ARIN"),
            ("216.0.0.0", "216.255.255.255", "ARIN"),
            ("217.0.0.0", "217.255.255.255", "RIPE Region"),
            ("218.0.0.0", "218.255.255.255", "APNIC"),
            ("219.0.0.0", "219.255.255.255", "APNIC"),
            ("220.0.0.0", "220.255.255.255", "APNIC"),
            ("221.0.0.0", "221.255.255.255", "APNIC"),
            ("222.0.0.0", "222.255.255.255", "APNIC"),
            ("223.0.0.0", "223.255.255.255", "APNIC"),
        ]
        
        # Shuffle for randomness
        random.shuffle(hunting_ranges)
        
        all_relays = []
        for start_ip, end_ip, region_name in hunting_ranges:
            print(f"\n🔍 Hunting in {region_name}...")
            
            # Test 1000 random IPs per range
            ips = self.generate_random_ips_in_range(start_ip, end_ip, 1000)
            relays = self.hunt_ips_parallel(ips, region_name)
            
            if relays:
                print(f"🎯 FOUND {len(relays)} relays in {region_name}")
                all_relays.extend(relays)
                
                # Save progress immediately
                self.save_progress(all_relays)
            else:
                print(f"❌ No relays in {region_name}")
        
        print(f"\n🏆 UNIVERSAL HUNT COMPLETE!")
        print(f"📊 Total relays found: {len(all_relays)}")
        print(f"🧪 IPs tested: {self.tested_count}")
        
        return all_relays
    
    def generate_random_ips_in_range(self, start_ip, end_ip, count):
        """Generate random IPs in range"""
        import ipaddress
        
        start = int(ipaddress.IPv4Address(start_ip))
        end = int(ipaddress.IPv4Address(end_ip))
        
        # Generate unique random IPs
        random_ints = set()
        while len(random_ints) < count and len(random_ints) < (end - start):
            random_ints.add(random.randint(start, end))
        
        return [str(ipaddress.IPv4Address(ip_int)) for ip_int in random_ints]
    
    def hunt_ips_parallel(self, ips, region_name):
        """Hunt IPs with maximum parallel power"""
        relays = []
        
        print(f"⚡ Testing {len(ips)} IPs in {region_name} with 200 threads...")
        
        with ThreadPoolExecutor(max_workers=200) as executor:
            futures = [executor.submit(self.test_ip_for_relay, ip) for ip in ips]
            
            for future in futures:
                try:
                    result = future.result(timeout=20)
                    if result:
                        relays.append(result)
                        with self.lock:
                            self.found_relays.append(result)
                        print(f"🎯 RELAY FOUND: {result['ip']} ({region_name})")
                except:
                    pass
                
                with self.lock:
                    self.tested_count += 1
                    if self.tested_count % 500 == 0:
                        print(f"📊 Tested {self.tested_count} IPs, found {len(self.found_relays)} relays")
        
        return relays
    
    def test_ip_for_relay(self, ip):
        """Test single IP for SMTP relay"""
        try:
            # Skip government IPs
            if self.is_government_ip(ip):
                return None
            
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
                        'type': 'universal_relay',
                        'found_at': time.time(),
                        'status': 'working'
                    }
            
            return None
            
        except:
            return None
    
    def is_government_ip(self, ip):
        """Check if IP is in government range"""
        import ipaddress
        
        try:
            ip_obj = ipaddress.IPv4Address(ip)
            for gov_range in self.government_ranges:
                if ip_obj in ipaddress.IPv4Network(gov_range):
                    return True
            return False
        except:
            return False
    
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
    
    def save_progress(self, relays):
        """Save progress to file"""
        try:
            with open(f"universal_hunt_progress_{int(time.time())}.txt", 'w') as f:
                f.write(f"# Universal Relay Hunt Progress\n")
                f.write(f"# Found: {len(relays)} relays\n")
                f.write(f"# Tested: {self.tested_count} IPs\n\n")
                
                for relay in relays:
                    f.write(f"{relay['ip']}:25\n")
            
            print(f"💾 Progress saved: {len(relays)} relays")
        except:
            pass

if __name__ == "__main__":
    print("🔥 UNIVERSAL RELAY HUNTER")
    print("🌍 Scanning the ENTIRE internet for open relays")
    print("⚠️  Avoiding government networks")
    print("🎯 Finding relays ANYWHERE else")
    print()
    
    hunter = UniversalRelayHunter()
    relays = hunter.hunt_everywhere()
    
    if relays:
        print(f"\n🎉 SUCCESS! Found {len(relays)} universal relays!")
        print("📋 RELAY LIST:")
        for i, relay in enumerate(relays, 1):
            print(f"{i}. {relay['ip']}:25")
    else:
        print("\n❌ No relays found in universal hunt")
    
    input("\nPress Enter to exit...")