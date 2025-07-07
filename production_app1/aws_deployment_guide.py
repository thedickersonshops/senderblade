"""
AWS EC2 Deployment Guide for SenderBlade
Automatic setup with port checking and CloudFlare integration
"""
import boto3
import socket
import time
import requests
import json

class AWSDeployment:
    def __init__(self):
        self.ec2_client = None
        self.instance_id = None
        self.public_ip = None
        
    def setup_aws_credentials(self, access_key, secret_key, region='us-east-1'):
        """Setup AWS credentials"""
        try:
            self.ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            # Test connection
            response = self.ec2_client.describe_regions()
            print("✅ AWS credentials configured successfully")
            return True
            
        except Exception as e:
            print(f"❌ AWS credentials failed: {e}")
            return False
    
    def create_ec2_instance(self):
        """Create EC2 instance for SenderBlade"""
        try:
            print("🚀 Creating AWS EC2 instance...")
            
            # Launch instance
            response = self.ec2_client.run_instances(
                ImageId='ami-0c02fb55956c7d316',  # Ubuntu 20.04 LTS
                MinCount=1,
                MaxCount=1,
                InstanceType='t3.small',  # 2 vCPU, 2GB RAM
                KeyName='senderblade-key',  # Create this key pair first
                SecurityGroupIds=['sg-senderblade'],  # Create security group
                UserData=self.get_user_data_script(),
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': 'SenderBlade-Server'},
                            {'Key': 'Project', 'Value': 'SenderBlade'},
                        ]
                    }
                ]
            )
            
            self.instance_id = response['Instances'][0]['InstanceId']
            print(f"✅ Instance created: {self.instance_id}")
            
            # Wait for instance to be running
            print("⏳ Waiting for instance to start...")
            waiter = self.ec2_client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[self.instance_id])
            
            # Get public IP
            instance_info = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
            self.public_ip = instance_info['Reservations'][0]['Instances'][0]['PublicIpAddress']
            
            print(f"🌐 Instance running at: {self.public_ip}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create instance: {e}")
            return False
    
    def create_security_group(self):
        """Create security group with required ports"""
        try:
            print("🛡️ Creating security group...")
            
            # Create security group
            response = self.ec2_client.create_security_group(
                GroupName='senderblade-sg',
                Description='SenderBlade Security Group'
            )
            
            sg_id = response['GroupId']
            
            # Add inbound rules
            self.ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # SSH
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 80,
                        'ToPort': 80,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # HTTP
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 443,
                        'ToPort': 443,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # HTTPS
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 5001,
                        'ToPort': 5001,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # SenderBlade
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 25,
                        'ToPort': 25,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # SMTP
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 587,
                        'ToPort': 587,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # SMTP Submission
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 465,
                        'ToPort': 465,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # SMTPS
                    }
                ]
            )
            
            print(f"✅ Security group created: {sg_id}")
            return sg_id
            
        except Exception as e:
            print(f"❌ Failed to create security group: {e}")
            return None
    
    def get_user_data_script(self):
        """Get user data script for automatic setup"""
        return """#!/bin/bash
# SenderBlade AWS Auto-Setup Script

# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install -y python3 python3-pip nginx supervisor git

# Install Python packages
pip3 install flask sqlite3 requests smtplib

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
rm /etc/nginx/sites-enabled/default
systemctl restart nginx
systemctl enable nginx

# Configure supervisor
cat > /etc/supervisor/conf.d/senderblade.conf << 'EOF'
[program:senderblade]
command=/usr/bin/python3 app_sender.py
directory=/opt/senderblade
user=senderblade
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/senderblade/app.log
environment=FLASK_ENV=production
EOF

# Start services
systemctl restart supervisor
systemctl enable supervisor

# Create status file
echo "AWS setup completed at $(date)" > /opt/senderblade/setup_complete.txt
"""

def check_port_open(host, port, timeout=5):
    """Check if a port is open on a host"""
    try:
        print(f"🔍 Checking {host}:{port}...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is OPEN on {host}")
            return True
        else:
            print(f"❌ Port {port} is CLOSED on {host}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking port {port}: {e}")
        return False

def check_smtp_ports(host):
    """Check all SMTP-related ports"""
    print(f"📧 CHECKING SMTP PORTS ON {host}")
    print("=" * 50)
    
    smtp_ports = [
        (25, "SMTP"),
        (587, "SMTP Submission (STARTTLS)"),
        (465, "SMTPS (SSL)"),
        (2525, "Alternative SMTP"),
        (26, "Alternative SMTP")
    ]
    
    open_ports = []
    
    for port, description in smtp_ports:
        if check_port_open(host, port):
            open_ports.append((port, description))
    
    print(f"\n📊 RESULTS FOR {host}:")
    if open_ports:
        print("✅ OPEN PORTS:")
        for port, desc in open_ports:
            print(f"   {port} - {desc}")
    else:
        print("❌ NO SMTP PORTS OPEN")
    
    return open_ports

def auto_cloudflare_setup(domain, zone_id, api_token, server_ip):
    """Automatically configure CloudFlare DNS"""
    try:
        print(f"☁️ CONFIGURING CLOUDFLARE FOR {domain}")
        print("=" * 50)
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        # DNS records to create
        dns_records = [
            {'type': 'A', 'name': '@', 'content': server_ip, 'proxied': True},
            {'type': 'A', 'name': 'www', 'content': server_ip, 'proxied': True},
            {'type': 'A', 'name': 'mail', 'content': server_ip, 'proxied': False},  # Don't proxy mail
        ]
        
        created_records = []
        
        for record in dns_records:
            try:
                # Create DNS record
                response = requests.post(
                    f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
                    headers=headers,
                    json=record
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result['success']:
                        print(f"✅ Created {record['type']} record: {record['name']} → {record['content']}")
                        created_records.append(record)
                    else:
                        print(f"❌ Failed to create {record['name']}: {result['errors']}")
                else:
                    print(f"❌ API error for {record['name']}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error creating {record['name']}: {e}")
        
        # Configure SSL settings
        try:
            ssl_settings = {
                'value': 'full'  # Full SSL mode
            }
            
            response = requests.patch(
                f'https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/ssl',
                headers=headers,
                json=ssl_settings
            )
            
            if response.status_code == 200:
                print("✅ SSL mode set to Full")
            else:
                print("❌ Failed to configure SSL")
                
        except Exception as e:
            print(f"❌ SSL configuration error: {e}")
        
        # Enable Always Use HTTPS
        try:
            https_settings = {
                'value': 'on'
            }
            
            response = requests.patch(
                f'https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/always_use_https',
                headers=headers,
                json=https_settings
            )
            
            if response.status_code == 200:
                print("✅ Always Use HTTPS enabled")
            else:
                print("❌ Failed to enable HTTPS redirect")
                
        except Exception as e:
            print(f"❌ HTTPS redirect error: {e}")
        
        print(f"\n🎉 CLOUDFLARE SETUP COMPLETE!")
        print(f"🌐 Your site will be available at: https://{domain}")
        print(f"⏳ DNS propagation may take 5-15 minutes")
        
        return len(created_records) > 0
        
    except Exception as e:
        print(f"❌ CloudFlare setup failed: {e}")
        return False

# AWS Instance Types and Pricing
AWS_INSTANCE_OPTIONS = {
    't3.micro': {'vcpu': 1, 'ram': 1, 'cost': '$8.5/month', 'free_tier': True},
    't3.small': {'vcpu': 2, 'ram': 2, 'cost': '$17/month', 'free_tier': False},
    't3.medium': {'vcpu': 2, 'ram': 4, 'cost': '$34/month', 'free_tier': False},
    't3.large': {'vcpu': 2, 'ram': 8, 'cost': '$67/month', 'free_tier': False},
}

def print_aws_options():
    """Print AWS deployment options"""
    print("☁️ AWS EC2 DEPLOYMENT OPTIONS")
    print("=" * 50)
    
    for instance_type, specs in AWS_INSTANCE_OPTIONS.items():
        free_tier_text = " (FREE TIER)" if specs['free_tier'] else ""
        print(f"{instance_type}{free_tier_text}:")
        print(f"   CPU: {specs['vcpu']} vCPU")
        print(f"   RAM: {specs['ram']} GB")
        print(f"   Cost: {specs['cost']}")
        print()
    
    print("💡 RECOMMENDATIONS:")
    print("   • t3.micro: Testing/development (FREE for 12 months)")
    print("   • t3.small: Production (recommended)")
    print("   • t3.medium: High traffic")
    print()
    
    print("🌍 REGIONS:")
    print("   • us-east-1: Virginia (cheapest)")
    print("   • us-west-2: Oregon")
    print("   • eu-west-1: Ireland")
    print("   • ap-southeast-1: Singapore")

if __name__ == "__main__":
    print("🚀 AWS SENDERBLADE DEPLOYMENT TOOLKIT")
    print("=" * 60)
    
    # Show AWS options
    print_aws_options()
    
    # Example usage
    print("\n📋 EXAMPLE USAGE:")
    print("1. Check if port 587 is open:")
    print("   check_smtp_ports('your-server-ip')")
    print()
    print("2. Auto-setup CloudFlare:")
    print("   auto_cloudflare_setup('yourdomain.com', 'zone_id', 'api_token', 'server_ip')")
    print()
    print("3. Deploy to AWS:")
    print("   aws_deploy = AWSDeployment()")
    print("   aws_deploy.setup_aws_credentials('access_key', 'secret_key')")
    print("   aws_deploy.create_ec2_instance()")