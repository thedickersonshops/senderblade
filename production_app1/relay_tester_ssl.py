"""
Relay Tester with SSL Support - Test your found relays properly
"""
import smtplib
import ssl
import time

def test_relay_with_ssl(ip, port=587):
    """Test relay with proper SSL/TLS handling"""
    try:
        print(f"🧪 Testing {ip}:{port}...")
        
        # Create SSL context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        if port == 587:
            # STARTTLS connection
            with smtplib.SMTP(ip, port, timeout=15) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                
                # Test relay without auth
                server.mail("test@example.com")
                code, response = server.rcpt("your_test@gmail.com")
                
                if code == 250:
                    print(f"✅ {ip}:{port} - WORKING RELAY!")
                    return True
                else:
                    print(f"❌ {ip}:{port} - Relay denied ({code})")
                    return False
                    
        elif port == 25:
            # Plain SMTP
            with smtplib.SMTP(ip, port, timeout=15) as server:
                server.ehlo()
                
                server.mail("test@example.com")
                code, response = server.rcpt("your_test@gmail.com")
                
                if code == 250:
                    print(f"✅ {ip}:{port} - WORKING RELAY!")
                    return True
                else:
                    print(f"❌ {ip}:{port} - Relay denied ({code})")
                    return False
        
        elif port == 26:
            # Alternative SMTP port
            with smtplib.SMTP(ip, port, timeout=15) as server:
                server.ehlo()
                
                server.mail("test@example.com")
                code, response = server.rcpt("your_test@gmail.com")
                
                if code == 250:
                    print(f"✅ {ip}:{port} - WORKING RELAY!")
                    return True
                else:
                    print(f"❌ {ip}:{port} - Relay denied ({code})")
                    return False
                    
    except Exception as e:
        print(f"❌ {ip}:{port} - Error: {str(e)}")
        return False

def send_test_email_via_relay(ip, port, to_email="your_test@gmail.com"):
    """Send actual test email via relay"""
    try:
        print(f"📧 Sending test email via {ip}:{port}...")
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        msg = f"""From: test@example.com
To: {to_email}
Subject: Relay Test - {ip}:{port}

This is a test email sent through open relay {ip}:{port}
Time: {time.ctime()}
Status: Working relay confirmed!
"""
        
        if port == 587:
            with smtplib.SMTP(ip, port, timeout=15) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.sendmail("test@example.com", [to_email], msg)
                
        else:
            with smtplib.SMTP(ip, port, timeout=15) as server:
                server.ehlo()
                server.sendmail("test@example.com", [to_email], msg)
        
        print(f"✅ Test email sent successfully via {ip}:{port}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send via {ip}:{port} - {str(e)}")
        return False

def test_your_relays():
    """Test the relays you found"""
    print("🔥 TESTING YOUR FOUND RELAYS")
    print("=" * 40)
    
    # Your found relays
    found_relays = [
        ("37.187.195.144", 587),
        ("185.236.84.96", 587),
        ("185.231.222.95", 587),
        ("185.23.69.118", 587),
        ("5.135.131.220", 587),
        ("185.145.97.4", 587),
        ("185.251.27.33", 587),
        ("185.38.250.227", 587),
        ("5.134.219.110", 587),
        ("37.148.211.79", 587),
        ("46.229.117.91", 587),
        ("46.242.198.172", 587),
        ("185.86.155.2", 26),
        ("91.244.204.51", 587),
    ]
    
    working_relays = []
    
    for ip, port in found_relays:
        if test_relay_with_ssl(ip, port):
            working_relays.append((ip, port))
        time.sleep(1)  # Small delay
    
    print(f"\n🎯 RESULTS:")
    print(f"📊 Tested: {len(found_relays)} relays")
    print(f"✅ Working: {len(working_relays)} relays")
    
    if working_relays:
        print(f"\n🎉 WORKING RELAYS:")
        for ip, port in working_relays:
            print(f"   {ip}:{port}")
        
        # Test sending via first working relay
        if working_relays:
            test_ip, test_port = working_relays[0]
            print(f"\n📧 Testing email send via {test_ip}:{test_port}...")
            send_test_email_via_relay(test_ip, test_port)
    
    return working_relays

def add_working_relays_to_senderblade(working_relays):
    """Add working relays to SenderBlade"""
    print(f"\n🔗 Adding {len(working_relays)} relays to SenderBlade...")
    
    for ip, port in working_relays:
        relay_config = f"""
# Add this to your SenderBlade SMTP servers:
Name: Relay {ip}:{port}
Host: {ip}
Port: {port}
Username: (leave empty)
Password: (leave empty)
From Email: noreply@{ip}
From Name: Newsletter
Require Auth: No
Use TLS: {"Yes" if port == 587 else "No"}
"""
        print(relay_config)

if __name__ == "__main__":
    print("🧪 RELAY TESTER WITH SSL SUPPORT")
    print("Testing your found relays properly...")
    print()
    
    working_relays = test_your_relays()
    
    if working_relays:
        add_working_relays_to_senderblade(working_relays)
        print(f"\n🚀 {len(working_relays)} relays ready for unlimited sending!")
    else:
        print("\n❌ No working relays found")
    
    input("\nPress Enter to exit...")