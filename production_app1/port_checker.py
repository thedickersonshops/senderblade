"""
Port Checker Tool - Check if SMTP ports are open
"""
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

def check_single_port(host, port, timeout=5):
    """Check if a single port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_smtp_ports(host):
    """Check all SMTP ports on a host"""
    print(f"🔍 CHECKING SMTP PORTS ON {host}")
    print("=" * 50)
    
    # SMTP ports to check
    smtp_ports = [
        (25, "SMTP (Plain)"),
        (587, "SMTP Submission (STARTTLS)"),
        (465, "SMTPS (SSL/TLS)"),
        (2525, "Alternative SMTP"),
        (26, "Alternative SMTP"),
        (1025, "Alternative SMTP"),
        (8025, "Alternative SMTP"),
    ]
    
    results = {}
    
    print("⏳ Testing ports...")
    for port, description in smtp_ports:
        print(f"   Testing {port}...", end=" ")
        
        if check_single_port(host, port, timeout=3):
            print("✅ OPEN")
            results[port] = {'status': 'open', 'description': description}
        else:
            print("❌ CLOSED")
            results[port] = {'status': 'closed', 'description': description}
    
    # Summary
    print(f"\n📊 RESULTS FOR {host}:")
    open_ports = [port for port, info in results.items() if info['status'] == 'open']
    
    if open_ports:
        print("✅ OPEN PORTS:")
        for port in open_ports:
            print(f"   {port} - {results[port]['description']}")
        
        print(f"\n🎯 SMTP CAPABILITY:")
        if 587 in open_ports:
            print("   ✅ Can send via STARTTLS (port 587)")
        if 465 in open_ports:
            print("   ✅ Can send via SSL/TLS (port 465)")
        if 25 in open_ports:
            print("   ✅ Can send via plain SMTP (port 25)")
        
    else:
        print("❌ NO SMTP PORTS OPEN")
        print("   This server cannot send emails directly")
    
    return results

def check_multiple_hosts(hosts):
    """Check SMTP ports on multiple hosts"""
    print(f"🌐 CHECKING SMTP PORTS ON {len(hosts)} HOSTS")
    print("=" * 60)
    
    all_results = {}
    
    for i, host in enumerate(hosts, 1):
        print(f"\n[{i}/{len(hosts)}] Checking {host}...")
        results = check_smtp_ports(host)
        all_results[host] = results
        
        if i < len(hosts):
            print("\n" + "-" * 30)
    
    # Summary of all hosts
    print(f"\n📋 SUMMARY OF ALL HOSTS:")
    print("=" * 40)
    
    for host, results in all_results.items():
        open_ports = [port for port, info in results.items() if info['status'] == 'open']
        if open_ports:
            print(f"✅ {host}: {len(open_ports)} ports open ({', '.join(map(str, open_ports))})")
        else:
            print(f"❌ {host}: No SMTP ports open")
    
    return all_results

def check_port_587_specifically(host):
    """Specifically check if port 587 is open and working"""
    print(f"🎯 CHECKING PORT 587 ON {host}")
    print("=" * 40)
    
    # Check if port is open
    print("1. Testing port connectivity...", end=" ")
    if not check_single_port(host, 587, timeout=5):
        print("❌ CLOSED")
        print("   Port 587 is not accessible")
        return False
    
    print("✅ OPEN")
    
    # Try SMTP connection
    print("2. Testing SMTP connection...", end=" ")
    try:
        import smtplib
        
        with smtplib.SMTP(host, 587, timeout=10) as server:
            server.ehlo()
            print("✅ SUCCESS")
            
            # Check STARTTLS support
            print("3. Testing STARTTLS support...", end=" ")
            if server.has_extn('STARTTLS'):
                print("✅ SUPPORTED")
                
                # Try STARTTLS
                print("4. Testing STARTTLS connection...", end=" ")
                try:
                    server.starttls()
                    server.ehlo()
                    print("✅ SUCCESS")
                    
                    print(f"\n🎉 PORT 587 FULLY WORKING ON {host}")
                    print("   ✅ Port is open")
                    print("   ✅ SMTP connection works")
                    print("   ✅ STARTTLS supported")
                    print("   ✅ Ready for email sending")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ FAILED ({e})")
                    
            else:
                print("❌ NOT SUPPORTED")
                
    except Exception as e:
        print(f"❌ FAILED ({e})")
    
    print(f"\n⚠️  PORT 587 PARTIALLY WORKING ON {host}")
    print("   ✅ Port is open")
    print("   ❌ SMTP/STARTTLS issues")
    
    return False

def quick_port_check(host, port):
    """Quick check for any port"""
    print(f"⚡ QUICK CHECK: {host}:{port}")
    
    if check_single_port(host, port, timeout=3):
        print(f"✅ {host}:{port} is OPEN")
        return True
    else:
        print(f"❌ {host}:{port} is CLOSED")
        return False

# Common SMTP servers to test
COMMON_SMTP_SERVERS = [
    'smtp.gmail.com',
    'smtp.outlook.com', 
    'smtp.yahoo.com',
    'smtp.aol.com',
    'smtp.zoho.com',
    'smtp.mail.com',
]

def test_common_smtp_servers():
    """Test common SMTP servers"""
    print("📧 TESTING COMMON SMTP SERVERS")
    print("=" * 50)
    
    for server in COMMON_SMTP_SERVERS:
        print(f"\n🔍 Testing {server}...")
        check_smtp_ports(server)

if __name__ == "__main__":
    print("🔍 SMTP PORT CHECKER TOOL")
    print("=" * 40)
    
    # Example usage
    print("\n📋 USAGE EXAMPLES:")
    print("1. Check specific host:")
    print("   check_smtp_ports('your-server.com')")
    print()
    print("2. Check port 587 specifically:")
    print("   check_port_587_specifically('your-server.com')")
    print()
    print("3. Quick port check:")
    print("   quick_port_check('your-server.com', 587)")
    print()
    print("4. Test multiple hosts:")
    print("   check_multiple_hosts(['server1.com', 'server2.com'])")
    print()
    
    # Interactive mode
    try:
        host = input("Enter host to check (or press Enter to test common SMTP servers): ").strip()
        
        if not host:
            test_common_smtp_servers()
        else:
            print()
            check_smtp_ports(host)
            print()
            check_port_587_specifically(host)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")