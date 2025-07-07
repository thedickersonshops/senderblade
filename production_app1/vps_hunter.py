#!/usr/bin/env python3
"""
VPS Port 25 Hunter - Find providers that actually work
"""

import socket
import threading
import time

# VPS providers to test (add more as we find them)
VPS_PROVIDERS = {
    "Contabo": ["88.99.0.1", "88.99.0.2"],  # Known to work
    "OVH": ["51.68.0.1", "51.68.0.2"],     # France
    "Hetzner": ["78.46.0.1", "78.46.0.2"], # Germany  
    "BuyVM": ["107.189.0.1"],              # Luxembourg
    "RamNode": ["107.191.0.1"],            # Netherlands
    "Hostinger": ["109.205.0.1"],          # Lithuania
    "Time4VPS": ["185.232.0.1"],           # Lithuania
    "AlphaVPS": ["185.189.0.1"],           # Bulgaria
    "VirMach": ["107.173.0.1"],            # Various
    "Inception": ["185.130.0.1"],          # Netherlands
}

def test_port_25(host, provider):
    """Test if port 25 is open on a host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, 25))
        sock.close()
        
        if result == 0:
            print(f"✅ {provider} ({host}): Port 25 OPEN!")
            return True
        else:
            print(f"❌ {provider} ({host}): Port 25 blocked")
            return False
    except Exception as e:
        print(f"⚠️ {provider} ({host}): Error - {e}")
        return False

def hunt_working_providers():
    """Hunt for VPS providers with open port 25"""
    print("🔍 Hunting for VPS providers with open port 25...")
    print("=" * 50)
    
    working_providers = []
    
    for provider, hosts in VPS_PROVIDERS.items():
        for host in hosts:
            if test_port_25(host, provider):
                working_providers.append(provider)
                break  # Found one working host for this provider
    
    print("\n" + "=" * 50)
    print("🎯 WORKING PROVIDERS:")
    for provider in working_providers:
        print(f"✅ {provider}")
    
    if not working_providers:
        print("❌ No providers found with open port 25")
        print("💡 Time for Plan B: Home server setup")
    
    return working_providers

if __name__ == "__main__":
    hunt_working_providers()