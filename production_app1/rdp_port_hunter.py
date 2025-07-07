#!/usr/bin/env python3
"""
Windows RDP Port 25 Hunter
Test which RDP providers have port 25 open
"""

import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Windows RDP providers to test
RDP_PROVIDERS = {
    "Kamatera": ["91.234.254.1", "91.234.254.2"],
    "Atlantic.Net": ["198.23.249.1", "198.23.249.2"], 
    "InterServer": ["162.244.34.1", "162.244.34.2"],
    "A2Hosting": ["192.185.4.1", "192.185.4.2"],
    "InMotion": ["69.46.86.1", "69.46.86.2"],
    "GoDaddy": ["160.153.129.1", "160.153.129.2"],
    "IONOS": ["217.160.0.1", "217.160.0.2"],
    "Hostwinds": ["104.168.149.1", "104.168.149.2"],
    "LiquidWeb": ["67.227.226.1", "67.227.226.2"],
    
    # Smaller/Alternative providers
    "Vultr-Windows": ["149.28.1.1"],
    "DigitalOcean-Win": ["159.89.1.1"],
    "Linode-Windows": ["172.105.1.1"],
    "Contabo-Win": ["88.99.1.1"],
    
    # Residential-style providers
    "BuyVM": ["107.189.1.1"],
    "RamNode": ["107.191.1.1"],
    "AlphaVPS": ["185.189.1.1"],
}

def test_smtp_ports(host, provider):
    """Test multiple SMTP-related ports"""
    ports = [25, 587, 465, 2525, 1025, 8025]
    results = {}
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                results[port] = "OPEN"
            else:
                results[port] = "CLOSED"
        except Exception:
            results[port] = "ERROR"
    
    return results

def test_provider(provider, hosts):
    """Test all hosts for a provider"""
    print(f"\n🔍 Testing {provider}...")
    
    working_hosts = []
    
    for host in hosts:
        results = test_smtp_ports(host, provider)
        
        # Check if any useful ports are open
        open_ports = [port for port, status in results.items() if status == "OPEN"]
        
        if open_ports:
            print(f"✅ {provider} ({host}): Ports {open_ports} OPEN")
            working_hosts.append((host, open_ports))
        else:
            print(f"❌ {provider} ({host}): All ports blocked")
    
    return working_hosts

def hunt_rdp_providers():
    """Hunt for Windows RDP providers with open SMTP ports"""
    print("🔥 HUNTING WINDOWS RDP PROVIDERS WITH OPEN SMTP PORTS")
    print("=" * 60)
    
    working_providers = {}
    
    # Test providers in parallel for speed
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(test_provider, provider, hosts): provider 
                  for provider, hosts in RDP_PROVIDERS.items()}
        
        for future in futures:
            provider = futures[future]
            try:
                working_hosts = future.result()
                if working_hosts:
                    working_providers[provider] = working_hosts
            except Exception as e:
                print(f"⚠️ Error testing {provider}: {e}")
    
    # Results
    print("\n" + "=" * 60)
    print("🎯 WORKING RDP PROVIDERS:")
    
    if working_providers:
        for provider, hosts in working_providers.items():
            print(f"\n✅ {provider}:")
            for host, ports in hosts:
                print(f"   📧 {host} - Ports: {ports}")
                if 25 in ports:
                    print(f"   🔥 PORT 25 OPEN! Perfect for mail server!")
                elif 587 in ports:
                    print(f"   ⚡ PORT 587 OPEN! Good for authenticated SMTP!")
    else:
        print("❌ No providers found with open SMTP ports")
        print("💡 Time for custom port solution...")
    
    return working_providers

def generate_setup_instructions(working_providers):
    """Generate setup instructions for working providers"""
    if not working_providers:
        return
    
    print("\n" + "=" * 60)
    print("📋 SETUP INSTRUCTIONS:")
    
    for provider, hosts in working_providers.items():
        print(f"\n🔧 {provider} Setup:")
        print(f"1. Sign up at {provider}")
        print(f"2. Get Windows RDP server")
        
        for host, ports in hosts:
            if 25 in ports:
                print(f"3. Use direct SMTP on port 25")
                print(f"   Host: [Your RDP IP]")
                print(f"   Port: 25")
                print(f"   Auth: None needed")
                print(f"   From: ANY EMAIL ADDRESS")
            elif 587 in ports:
                print(f"3. Use authenticated SMTP on port 587")
                print(f"   Host: [Your RDP IP]")
                print(f"   Port: 587")
                print(f"   Auth: Basic setup needed")

if __name__ == "__main__":
    working = hunt_rdp_providers()
    generate_setup_instructions(working)