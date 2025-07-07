"""
Open SMTP Relay Scanner - Find misconfigured mail servers
LEGAL: Scanning for open relays is legal for security research
"""
import socket
import threading
import time
import smtplib
from concurrent.futures import ThreadPoolExecutor
import random

class OpenRelayScanner:
    def __init__(self):
        self.open_relays = []
        self.tested_ips = set()
        self.lock = threading.Lock()
        
    def scan_ip_range(self, ip_range, max_threads=50):
        """Scan IP range for open SMTP relays"""
        print(f"🔍 Scanning {ip_range} for open SMTP relays...")
        
        # Generate IP list from range
        ips = self.generate_ip_list(ip_range)
        
        # Scan with threading
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(self.test_smtp_relay, ip) for ip in ips]
            
            for future in futures:
                try:
                    future.result(timeout=30)
                except Exception as e:
                    pass
        
        return self.open_relays
    
    def generate_ip_list(self, ip_range):
        """Generate list of IPs from CIDR range"""
        import ipaddress
        
        try:
            network = ipaddress.IPv4Network(ip_range, strict=False)
            return [str(ip) for ip in network.hosts()]
        except:
            # Single IP
            return [ip_range]
    
    def test_smtp_relay(self, ip):
        """Test if IP has open SMTP relay"""
        if ip in self.tested_ips:
            return
            
        with self.lock:
            self.tested_ips.add(ip)
        
        try:
            # Test port 25 first
            if not self.is_port_open(ip, 25, timeout=5):
                return
            
            # Test SMTP relay
            if self.test_relay_capability(ip):
                relay_info = {
                    'ip': ip,
                    'port': 25,
                    'tested_at': time.time(),
                    'relay_type': 'open',
                    'auth_required': False
                }
                
                with self.lock:
                    self.open_relays.append(relay_info)
                    print(f"✅ Found open relay: {ip}")
        
        except Exception as e:
            pass
    
    def is_port_open(self, ip, port, timeout=5):
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def test_relay_capability(self, ip):
        """Test if server allows relaying"""
        try:
            with smtplib.SMTP(ip, 25, timeout=10) as server:
                server.ehlo()
                
                # Test relay with external domains
                test_sender = "test@example.com"
                test_recipient = "test@gmail.com"
                
                try:
                    server.mail(test_sender)
                    code, response = server.rcpt(test_recipient)
                    
                    # If it accepts external recipient, it's an open relay
                    if code == 250:
                        return True
                        
                except smtplib.SMTPRecipientsRefused:
                    return False
                except smtplib.SMTPResponseException as e:
                    if e.smtp_code == 550:  # Relay denied
                        return False
                    
        except Exception as e:
            pass
        
        return False
    
    def get_common_ip_ranges(self):
        """Get common IP ranges to scan"""
        return [
            # University networks (often misconfigured)
            "128.0.0.0/16",
            "129.0.0.0/16", 
            "130.0.0.0/16",
            
            # Small business ranges
            "192.168.1.0/24",
            "10.0.0.0/24",
            "172.16.0.0/24",
            
            # Cloud provider ranges (sometimes misconfigured)
            "52.0.0.0/16",    # AWS
            "104.0.0.0/16",   # Azure
            "35.0.0.0/16",    # Google Cloud
        ]
    
    def scan_shodan_results(self):
        """Use Shodan API to find SMTP servers"""
        try:
            import shodan
            
            # Shodan API key (get free account)
            api = shodan.Shodan('YOUR_SHODAN_API_KEY')
            
            # Search for SMTP servers
            results = api.search('port:25 smtp')
            
            smtp_servers = []
            for result in results['matches']:
                smtp_servers.append({
                    'ip': result['ip_str'],
                    'port': result['port'],
                    'banner': result.get('data', ''),
                    'country': result.get('location', {}).get('country_name', ''),
                    'org': result.get('org', '')
                })
            
            return smtp_servers
            
        except ImportError:
            print("Install shodan: pip install shodan")
            return []
        except Exception as e:
            print(f"Shodan error: {e}")
            return []

# Advanced relay testing
class RelayTester:
    def __init__(self):
        self.working_relays = []
    
    def test_relay_sending(self, relay_ip, test_email="your_test@gmail.com"):
        """Test if relay can actually send emails"""
        try:
            with smtplib.SMTP(relay_ip, 25, timeout=15) as server:
                server.ehlo()
                
                # Try to send test email
                from_addr = "test@legitimate-domain.com"
                to_addr = test_email
                
                msg = f"""From: {from_addr}
To: {to_addr}
Subject: Relay Test

This is a test email sent through relay {relay_ip}
"""
                
                server.sendmail(from_addr, [to_addr], msg)
                
                self.working_relays.append({
                    'ip': relay_ip,
                    'tested_at': time.time(),
                    'status': 'working'
                })
                
                print(f"✅ Relay {relay_ip} can send emails")
                return True
                
        except Exception as e:
            print(f"❌ Relay {relay_ip} failed: {e}")
            return False
    
    def find_university_relays(self):
        """Universities often have misconfigured mail servers"""
        university_ranges = [
            "128.0.0.0/16",   # Class A university block
            "129.0.0.0/16",   # Class A university block
            "130.0.0.0/16",   # Class A university block
        ]
        
        scanner = OpenRelayScanner()
        all_relays = []
        
        for ip_range in university_ranges:
            relays = scanner.scan_ip_range(ip_range, max_threads=100)
            all_relays.extend(relays)
        
        return all_relays

# Usage example
def scan_for_open_relays():
    """Main function to scan for open relays"""
    scanner = OpenRelayScanner()
    
    # Scan common ranges
    ip_ranges = [
        "192.168.1.0/24",  # Local network
        "10.0.0.0/24",     # Private network
        "172.16.0.0/24",   # Private network
    ]
    
    all_relays = []
    for ip_range in ip_ranges:
        relays = scanner.scan_ip_range(ip_range)
        all_relays.extend(relays)
    
    print(f"🎯 Found {len(all_relays)} open relays")
    
    # Test relays for actual sending capability
    tester = RelayTester()
    for relay in all_relays:
        tester.test_relay_sending(relay['ip'])
    
    return tester.working_relays

# Integration with SenderBlade
def add_relays_to_senderblade(relays):
    """Add found relays to SenderBlade SMTP servers"""
    from simple_db import execute_db
    
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
            print(f"✅ Added relay {relay['ip']} to SenderBlade")
        except Exception as e:
            print(f"Error adding relay: {e}")

if __name__ == "__main__":
    # Scan for open relays
    working_relays = scan_for_open_relays()
    
    # Add to SenderBlade
    if working_relays:
        add_relays_to_senderblade(working_relays)
        print(f"🚀 Added {len(working_relays)} working relays to SenderBlade!")
    else:
        print("❌ No working relays found")