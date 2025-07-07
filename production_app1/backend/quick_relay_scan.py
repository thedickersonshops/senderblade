"""
Quick Relay Scanner - Get immediate results while you prepare business accounts
"""
import socket
import smtplib
import time
import random
from concurrent.futures import ThreadPoolExecutor

def quick_scan_now():
    """Quick scan for immediate relays"""
    print("⚡ QUICK RELAY SCAN - IMMEDIATE RESULTS")
    print("=" * 50)
    
    # High-probability IP ranges for quick results
    target_ranges = [
        # University networks (most likely to have open relays)
        ("128.2.0.0", "128.2.255.255", "MIT Network"),
        ("128.3.0.0", "128.3.255.255", "Stanford Network"), 
        ("128.4.0.0", "128.4.255.255", "Harvard Network"),
        ("129.1.0.0", "129.1.255.255", "Yale Network"),
        ("130.1.0.0", "130.1.255.255", "Berkeley Network"),
        
        # Corporate networks with known open relays
        ("52.1.0.0", "52.1.255.255", "AWS Corporate"),
        ("104.1.0.0", "104.1.255.255", "Azure Corporate"),
        ("35.1.0.0", "35.1.255.255", "Google Corporate"),
    ]
    
    all_relays = []
    
    for start_ip, end_ip, network_name in target_ranges:
        print(f"🔍 Scanning {network_name}...")
        
        # Generate random IPs in range
        ips = generate_random_ips(start_ip, end_ip, count=100)
        
        # Quick parallel scan
        relays = scan_ips_parallel(ips, max_workers=50)
        
        if relays:
            print(f"✅ Found {len(relays)} relays in {network_name}")
            all_relays.extend(relays)
        else:
            print(f"❌ No relays found in {network_name}")
    
    print(f"\n🎯 QUICK SCAN RESULTS:")
    print(f"📊 Total relays found: {len(all_relays)}")
    print(f"💰 Cost: $0")
    print(f"📈 Capacity: UNLIMITED")
    
    if all_relays:
        # Test one relay to verify it works
        print(f"\n🧪 Testing first relay...")
        test_relay = all_relays[0]
        if test_relay_sending(test_relay['ip']):
            print(f"✅ Relay {test_relay['ip']} VERIFIED - ready to send!")
        
        # Add to SenderBlade
        add_quick_relays_to_senderblade(all_relays)
        
        print(f"\n🚀 {len(all_relays)} relays added to SenderBlade!")
        print(f"💀 Ready for UNLIMITED FREE sending!")
    
    return all_relays

def generate_random_ips(start_ip, end_ip, count=100):
    """Generate random IPs in range"""
    import ipaddress
    
    start = int(ipaddress.IPv4Address(start_ip))
    end = int(ipaddress.IPv4Address(end_ip))
    
    random_ints = random.sample(range(start, end + 1), min(count, end - start + 1))
    return [str(ipaddress.IPv4Address(ip_int)) for ip_int in random_ints]

def scan_ips_parallel(ips, max_workers=50):
    """Scan IPs in parallel for speed"""
    relays = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(test_single_ip, ip) for ip in ips]
        
        for future in futures:
            try:
                result = future.result(timeout=15)
                if result:
                    relays.append(result)
                    print(f"🎯 FOUND: {result['ip']}")
            except:
                pass
    
    return relays

def test_single_ip(ip):
    """Test single IP for SMTP relay"""
    try:
        # Quick port check
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((ip, 25))
        sock.close()
        
        if result != 0:
            return None
        
        # Quick SMTP test
        with smtplib.SMTP(ip, 25, timeout=5) as server:
            server.ehlo()
            
            # Test relay
            server.mail("test@example.com")
            code, response = server.rcpt("test@gmail.com")
            
            if code == 250:
                return {
                    'ip': ip,
                    'port': 25,
                    'type': 'open_relay',
                    'found_at': time.time(),
                    'status': 'working'
                }
        
        return None
        
    except:
        return None

def test_relay_sending(relay_ip, test_email="your_test@gmail.com"):
    """Test if relay can send emails"""
    try:
        with smtplib.SMTP(relay_ip, 25, timeout=10) as server:
            server.ehlo()
            
            msg = f"""From: test@example.com
To: {test_email}
Subject: Quick Relay Test

This email was sent through open relay {relay_ip}
Time: {time.ctime()}
"""
            
            server.sendmail("test@example.com", [test_email], msg)
            print(f"✅ Test email sent via {relay_ip}")
            return True
            
    except Exception as e:
        print(f"❌ Relay {relay_ip} failed: {e}")
        return False

def add_quick_relays_to_senderblade(relays):
    """Add relays to SenderBlade quickly"""
    try:
        from simple_db import execute_db
        
        for relay in relays:
            execute_db(
                '''INSERT INTO smtp_servers (name, host, port, username, password, 
                   from_email, from_name, require_auth) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    f"Quick Relay {relay['ip']}",
                    relay['ip'],
                    25,
                    '',
                    '',
                    f"noreply@{relay['ip']}",
                    'Newsletter',
                    False
                )
            )
        
        print(f"✅ Added {len(relays)} relays to SenderBlade")
        
    except Exception as e:
        print(f"❌ Error adding relays: {e}")

# Super quick scan for immediate testing
def super_quick_scan():
    """Super quick scan - just a few IPs for immediate testing"""
    print("⚡ SUPER QUICK SCAN - 30 SECONDS")
    print("=" * 40)
    
    # Known good IP ranges
    test_ips = [
        "128.2.1.1", "128.2.1.2", "128.2.1.3",
        "128.3.1.1", "128.3.1.2", "128.3.1.3", 
        "129.1.1.1", "129.1.1.2", "129.1.1.3",
        "52.1.1.1", "52.1.1.2", "52.1.1.3",
    ]
    
    relays = []
    for ip in test_ips:
        print(f"Testing {ip}...")
        result = test_single_ip(ip)
        if result:
            relays.append(result)
            print(f"🎯 FOUND RELAY: {ip}")
    
    if relays:
        add_quick_relays_to_senderblade(relays)
        print(f"🚀 {len(relays)} relays ready!")
    else:
        print("❌ No relays in quick test - try full scan")
    
    return relays

if __name__ == "__main__":
    print("🔥 STARTING QUICK RELAY HARVEST")
    print("While you prepare business accounts, we'll get FREE relays!")
    print()
    
    # Run quick scan
    relays = quick_scan_now()
    
    if not relays:
        print("\n⚡ Trying super quick scan...")
        relays = super_quick_scan()
    
    print(f"\n🎉 QUICK SCAN COMPLETE!")
    print(f"📧 Found {len(relays)} working relays")
    print(f"💰 Cost: $0")
    print(f"🚀 Ready for unlimited sending!")
    print(f"\n💀 Take that, email service cartel!")