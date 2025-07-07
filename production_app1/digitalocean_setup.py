"""
DigitalOcean Deployment Script - SMTP Friendly Alternative to AWS
"""
import requests
import time
import json

class DigitalOceanDeployment:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.digitalocean.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
    def create_droplet(self, name="senderblade-server", region="nyc1", size="s-2vcpu-2gb"):
        """Create DigitalOcean droplet with SMTP ports open"""
        try:
            print("🚀 Creating DigitalOcean droplet...")
            print(f"   Name: {name}")
            print(f"   Region: {region}")
            print(f"   Size: {size}")
            
            droplet_data = {
                "name": name,
                "region": region,
                "size": size,
                "image": "ubuntu-20-04-x64",
                "ssh_keys": [],  # Add your SSH key IDs here
                "backups": False,
                "ipv6": True,
                "user_data": self.get_user_data_script(),
                "monitoring": True,
                "tags": ["senderblade", "email-server"]
            }
            
            response = requests.post(
                f"{self.base_url}/droplets",
                headers=self.headers,
                json=droplet_data
            )
            
            if response.status_code == 202:
                droplet = response.json()["droplet"]
                droplet_id = droplet["id"]
                
                print(f"✅ Droplet created successfully!")
                print(f"   ID: {droplet_id}")
                print(f"   Status: {droplet['status']}")
                
                # Wait for droplet to be active
                print("⏳ Waiting for droplet to be active...")
                public_ip = self.wait_for_droplet_active(droplet_id)
                
                if public_ip:
                    print(f"🌐 Droplet is active!")
                    print(f"   Public IP: {public_ip}")
                    print(f"   SSH: ssh root@{public_ip}")
                    
                    # Test SMTP ports
                    print("\n📧 Testing SMTP ports...")
                    time.sleep(30)  # Wait for server to fully boot
                    self.test_smtp_ports(public_ip)
                    
                    return {
                        'success': True,
                        'droplet_id': droplet_id,
                        'public_ip': public_ip,
                        'ssh_command': f"ssh root@{public_ip}"
                    }
                
            else:
                print(f"❌ Failed to create droplet: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            print(f"❌ Error creating droplet: {e}")
            return {'success': False, 'error': str(e)}
    
    def wait_for_droplet_active(self, droplet_id, max_wait=300):
        """Wait for droplet to become active"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    f"{self.base_url}/droplets/{droplet_id}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    droplet = response.json()["droplet"]
                    status = droplet["status"]
                    
                    print(f"   Status: {status}")
                    
                    if status == "active":
                        # Get public IP
                        for network in droplet["networks"]["v4"]:
                            if network["type"] == "public":
                                return network["ip_address"]
                    
                    time.sleep(10)
                else:
                    print(f"❌ Error checking droplet status: {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ Error waiting for droplet: {e}")
                break
        
        print("❌ Timeout waiting for droplet to become active")
        return None
    
    def test_smtp_ports(self, ip_address):
        """Test SMTP ports on the new droplet"""
        import socket
        
        smtp_ports = [25, 587, 465, 2525]
        open_ports = []
        
        print(f"🔍 Testing SMTP ports on {ip_address}...")
        
        for port in smtp_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((ip_address, port))
                sock.close()
                
                if result == 0:
                    print(f"   ✅ Port {port}: OPEN")
                    open_ports.append(port)
                else:
                    print(f"   ❌ Port {port}: CLOSED")
                    
            except Exception as e:
                print(f"   ❌ Port {port}: ERROR ({e})")
        
        if open_ports:
            print(f"\n🎉 SUCCESS! {len(open_ports)} SMTP ports are open!")
            print("   DigitalOcean allows email sending!")
        else:
            print(f"\n⚠️  No SMTP ports open yet (server may still be booting)")
            print("   Try testing again in a few minutes")
        
        return open_ports
    
    def get_user_data_script(self):
        """Get cloud-init script for automatic setup"""
        return """#!/bin/bash
# SenderBlade DigitalOcean Auto-Setup Script

# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3 python3-pip nginx supervisor git ufw

# Configure firewall (allow all ports including SMTP)
ufw allow ssh
ufw allow http
ufw allow https
ufw allow 5001
ufw allow 25    # SMTP
ufw allow 587   # SMTP Submission
ufw allow 465   # SMTPS
ufw allow 2525  # Alternative SMTP
ufw --force enable

# Install Python packages
pip3 install flask requests

# Create senderblade user
useradd -m -s /bin/bash senderblade
usermod -aG sudo senderblade

# Create directories
mkdir -p /opt/senderblade
mkdir -p /var/log/senderblade
chown -R senderblade:senderblade /opt/senderblade
chown -R senderblade:senderblade /var/log/senderblade

# Configure nginx
cat > /etc/nginx/sites-available/senderblade << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable nginx site
ln -s /etc/nginx/sites-available/senderblade /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx
systemctl enable nginx

# Create setup completion marker
echo "DigitalOcean setup completed at $(date)" > /opt/senderblade/setup_complete.txt
echo "SMTP ports should be open by default" >> /opt/senderblade/setup_complete.txt

# Test SMTP ports and log results
for port in 25 587 465 2525; do
    if nc -z localhost $port 2>/dev/null; then
        echo "Port $port: OPEN" >> /opt/senderblade/port_test.txt
    else
        echo "Port $port: CLOSED" >> /opt/senderblade/port_test.txt
    fi
done
"""
    
    def list_regions(self):
        """List available DigitalOcean regions"""
        try:
            response = requests.get(f"{self.base_url}/regions", headers=self.headers)
            
            if response.status_code == 200:
                regions = response.json()["regions"]
                
                print("🌍 AVAILABLE DIGITALOCEAN REGIONS:")
                print("=" * 50)
                
                for region in regions:
                    if region["available"]:
                        print(f"   {region['slug']}: {region['name']}")
                
                return regions
            else:
                print(f"❌ Failed to get regions: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting regions: {e}")
            return []
    
    def list_sizes(self):
        """List available droplet sizes"""
        try:
            response = requests.get(f"{self.base_url}/sizes", headers=self.headers)
            
            if response.status_code == 200:
                sizes = response.json()["sizes"]
                
                print("💻 AVAILABLE DROPLET SIZES:")
                print("=" * 50)
                
                for size in sizes:
                    if size["available"]:
                        print(f"   {size['slug']}: {size['memory']}MB RAM, {size['vcpus']} vCPU - ${size['price_monthly']}/month")
                
                return sizes
            else:
                print(f"❌ Failed to get sizes: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting sizes: {e}")
            return []

def quick_digitalocean_setup():
    """Quick setup guide for DigitalOcean"""
    print("🚀 DIGITALOCEAN QUICK SETUP GUIDE")
    print("=" * 50)
    
    print("\n📋 STEPS:")
    print("1. Go to: https://cloud.digitalocean.com")
    print("2. Sign up for account (get $100 credit with referral)")
    print("3. Go to API → Generate New Token")
    print("4. Copy your API token")
    print("5. Run this script with your token")
    
    print("\n💰 RECOMMENDED DROPLET:")
    print("   Size: s-2vcpu-2gb ($12/month)")
    print("   Region: nyc1 (New York) or sfo3 (San Francisco)")
    print("   Image: Ubuntu 20.04 LTS")
    print("   Features: All SMTP ports open by default!")
    
    print("\n🔥 ADVANTAGES OVER AWS:")
    print("   ✅ All SMTP ports open (25, 587, 465)")
    print("   ✅ No email restrictions")
    print("   ✅ Cheaper than AWS ($12 vs $17)")
    print("   ✅ Clean IP reputation")
    print("   ✅ Easy setup")
    print("   ✅ No vendor lock-in")

if __name__ == "__main__":
    print("🌊 DIGITALOCEAN DEPLOYMENT FOR SENDERBLADE")
    print("The SMTP-friendly alternative to AWS!")
    print()
    
    # Show quick setup guide
    quick_digitalocean_setup()
    
    # Interactive setup
    try:
        api_token = input("\nEnter your DigitalOcean API token (or press Enter to skip): ").strip()
        
        if api_token:
            do = DigitalOceanDeployment(api_token)
            
            print("\n🌍 Available regions:")
            do.list_regions()
            
            print("\n💻 Available sizes:")
            do.list_sizes()
            
            # Create droplet
            create = input("\nCreate droplet now? (y/n): ").strip().lower()
            if create == 'y':
                result = do.create_droplet()
                
                if result['success']:
                    print(f"\n🎉 DIGITALOCEAN DEPLOYMENT SUCCESSFUL!")
                    print(f"   IP Address: {result['public_ip']}")
                    print(f"   SSH Command: {result['ssh_command']}")
                    print(f"\n📧 SMTP ports should be OPEN (unlike AWS)!")
                    print(f"🚀 Ready to deploy SenderBlade!")
                else:
                    print(f"\n❌ Deployment failed: {result['error']}")
        else:
            print("\n💡 Get your API token from: https://cloud.digitalocean.com/account/api/tokens")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")