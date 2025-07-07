"""
Add Found Relays to SenderBlade - Direct integration
"""
from simple_db import execute_db

def add_found_relays():
    """Add your found relays directly to SenderBlade"""
    print("🔗 ADDING FOUND RELAYS TO SENDERBLADE")
    print("=" * 40)
    
    # Your working relays with SSL support
    relays = [
        {"ip": "37.187.195.144", "port": 587, "use_tls": True},
        {"ip": "185.236.84.96", "port": 587, "use_tls": True},
        {"ip": "185.231.222.95", "port": 587, "use_tls": True},
        {"ip": "185.23.69.118", "port": 587, "use_tls": True},
        {"ip": "5.135.131.220", "port": 587, "use_tls": True},
        {"ip": "185.145.97.4", "port": 587, "use_tls": True},
        {"ip": "185.251.27.33", "port": 587, "use_tls": True},
        {"ip": "185.38.250.227", "port": 587, "use_tls": True},
        {"ip": "5.134.219.110", "port": 587, "use_tls": True},
        {"ip": "37.148.211.79", "port": 587, "use_tls": True},
        {"ip": "46.229.117.91", "port": 587, "use_tls": True},
        {"ip": "46.242.198.172", "port": 587, "use_tls": True},
        {"ip": "185.86.155.2", "port": 26, "use_tls": False},
        {"ip": "91.244.204.51", "port": 587, "use_tls": True},
    ]
    
    added_count = 0
    
    for relay in relays:
        try:
            execute_db(
                '''INSERT INTO smtp_servers (name, host, port, username, password, 
                   from_email, from_name, require_auth, use_tls) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    f"Relay {relay['ip']}:{relay['port']}",
                    relay['ip'],
                    relay['port'],
                    '',  # No username
                    '',  # No password
                    f"noreply@{relay['ip']}",
                    'Newsletter',
                    False,  # No auth required
                    relay['use_tls']  # TLS for port 587
                )
            )
            
            added_count += 1
            print(f"✅ Added {relay['ip']}:{relay['port']}")
            
        except Exception as e:
            print(f"❌ Error adding {relay['ip']}: {e}")
    
    print(f"\n🎉 Successfully added {added_count} relays to SenderBlade!")
    print(f"🚀 Ready for unlimited FREE sending!")
    
    return added_count

if __name__ == "__main__":
    add_found_relays()