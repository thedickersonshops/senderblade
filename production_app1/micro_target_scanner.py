"""
Micro Target Scanner - Very small, specific targets
"""
import socket
import smtplib
import time
import random

def scan_micro_targets():
    """Scan very specific small targets"""
    print("🎯 MICRO TARGET SCANNER")
    print("=" * 30)
    
    # Very specific small ranges
    micro_targets = [
        # Small web hosting companies
        "192.185.0.0/24",    # Small hosting
        "192.186.0.0/24",    # Regional hosting
        "198.54.0.0/24",     # Micro hosting
        "199.34.0.0/24",     # Local hosting
        
        # Small ISPs
        "66.45.0.0/24",      # Regional ISP
        "67.23.0.0/24",      # Local ISP
        "68.12.0.0/24",      # Cable ISP
        
        # Community organizations
        "161.45.0.0/24",     # Community college
        "162.23.0.0/24",     # Local school
        "170.12.0.0/24",     # City government
        
        # Small business blocks
        "74.125.0.0/24",     # Small business
        "75.134.0.0/24",     # Local business
        "76.89.0.0/24",      # Regional business
    ]
    
    all_relays = []
    
    for cidr in micro_targets:
        print(f"🔍 Scanning {cidr}...")
        
        # Generate all IPs in /24 range (254 IPs)
        base_ip = cidr.split('/')[0]
        base_parts = base_ip.split('.')
        base = '.'.join(base_parts[:3])
        
        # Test random 20 IPs from the /24
        test_ips = [f"{base}.{random.randint(1, 254)}" for _ in range(20)]
        
        for ip in test_ips:
            if test_single_ip(ip):
                relay = {
                    'ip': ip,
                    'port': 25,
                    'type': 'micro_relay',
                    'range': cidr
                }
                all_relays.append(relay)
                print(f"✅ FOUND: {ip}")
            
            # Small delay
            time.sleep(0.2)
    
    print(f"\n🎯 Total micro relays: {len(all_relays)}")
    return all_relays

def test_single_ip(ip):
    """Quick test single IP"""
    try:
        # Port check
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, 25))
        sock.close()
        
        if result != 0:
            return False
        
        # SMTP check
        with smtplib.SMTP(ip, 25, timeout=5) as server:
            server.ehlo()
            server.mail("test@example.com")
            code, response = server.rcpt("test@gmail.com")
            return code == 250
            
    except:
        return False

if __name__ == "__main__":
    relays = scan_micro_targets()
    
    if relays:
        print(f"\n🎉 SUCCESS! Found {len(relays)} micro relays")
        for relay in relays:
            print(f"   {relay['ip']} ({relay['range']})")
    else:
        print("\n❌ No micro relays found")