# 🌐 Multi-Domain Email Server Setup Guide

## ✅ YES! One Server = Multiple Domains

**Answer: Absolutely! One VPS can handle unlimited domains for random subdomains.**

## 🏗️ Server Architecture

### Single VPS Setup:
```
VPS Server (1 IP Address)
├── domain1.com
│   ├── mail.domain1.com
│   ├── news.domain1.com
│   └── abc123.domain1.com
├── domain2.com
│   ├── mail.domain2.com
│   ├── updates.domain2.com
│   └── x7k9m2.domain2.com
└── domain3.com
    ├── info.domain3.com
    ├── alerts.domain3.com
    └── n4p8q1s.domain3.com
```

## 🚀 VPS Requirements

### Minimum Specs:
- **RAM**: 2GB (4GB recommended)
- **CPU**: 2 cores
- **Storage**: 20GB SSD
- **Bandwidth**: 1TB/month
- **OS**: Ubuntu 20.04/22.04 LTS

### Recommended Providers:
- **DigitalOcean**: $12/month droplet
- **Vultr**: $10/month VPS
- **Linode**: $12/month instance
- **AWS EC2**: t3.small instance

## 📧 Email Server Software Options

### Option 1: Postfix + Dovecot (Recommended)
```bash
# Full-featured mail server
- Postfix: SMTP server
- Dovecot: IMAP/POP3 server
- SpamAssassin: Spam filtering
- OpenDKIM: DKIM signing
```

### Option 2: Mail-in-a-Box (Easiest)
```bash
# One-command setup
curl -s https://mailinabox.email/setup.sh | sudo bash
```

### Option 3: iRedMail (Professional)
```bash
# Enterprise-grade setup
wget https://github.com/iredmail/iRedMail/archive/1.6.2.tar.gz
```

## 🔧 DNS Configuration (Per Domain)

### For Each Domain, Add These Records:

#### A Records:
```
Type: A
Name: @
Value: [Your VPS IP]
TTL: 300

Type: A  
Name: *
Value: [Your VPS IP]
TTL: 300

Type: A
Name: mail
Value: [Your VPS IP]
TTL: 300
```

#### MX Record:
```
Type: MX
Name: @
Value: mail.yourdomain.com
Priority: 10
TTL: 300
```

#### SPF Record:
```
Type: TXT
Name: @
Value: v=spf1 ip4:[Your VPS IP] include:_spf.google.com ~all
TTL: 300
```

#### DKIM Record:
```
Type: TXT
Name: default._domainkey
Value: [Generated DKIM key]
TTL: 300
```

#### DMARC Record:
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com
TTL: 300
```

## 🛠️ Step-by-Step Setup

### Step 1: VPS Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git nano ufw

# Configure firewall
sudo ufw allow 22    # SSH
sudo ufw allow 25    # SMTP
sudo ufw allow 587   # SMTP Submission
sudo ufw allow 993   # IMAPS
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Step 2: Install Mail Server
```bash
# Option A: Mail-in-a-Box (Recommended for beginners)
curl -s https://mailinabox.email/setup.sh | sudo bash

# Option B: Manual Postfix setup
sudo apt install -y postfix dovecot-core dovecot-imapd dovecot-pop3d
```

### Step 3: Configure Multiple Domains
```bash
# Add domains to Postfix
sudo nano /etc/postfix/main.cf

# Add this line:
virtual_alias_domains = domain1.com domain2.com domain3.com
```

### Step 4: SSL Certificates
```bash
# Install Certbot
sudo apt install -y certbot

# Get certificates for all domains
sudo certbot certonly --standalone -d domain1.com -d *.domain1.com
sudo certbot certonly --standalone -d domain2.com -d *.domain2.com
sudo certbot certonly --standalone -d domain3.com -d *.domain3.com
```

## 🎯 SenderBlade Integration

### Update Random Subdomain Function:
```python
# Multiple domain support
AVAILABLE_DOMAINS = [
    'domain1.com',
    'domain2.com', 
    'domain3.com'
]

def generate_random_subdomain_email(base_email):
    if '@' not in base_email:
        return base_email
    
    username, domain = base_email.split('@', 1)
    
    # Use random domain from available list
    random_domain = random.choice(AVAILABLE_DOMAINS)
    
    # Generate random subdomain
    subdomains = ['mail', 'news', 'info', 'updates', 'alerts']
    random_subdomain = random.choice(subdomains)
    
    return f"{username}@{random_subdomain}.{random_domain}"
```

## 📊 Benefits of Multi-Domain Setup

### Deliverability Advantages:
- **Domain Rotation**: Spread reputation across domains
- **Subdomain Variation**: Unlimited subdomain combinations
- **Risk Distribution**: If one domain gets flagged, others continue
- **Scalability**: Add more domains anytime

### Cost Efficiency:
- **One Server**: Handle unlimited domains
- **Shared Resources**: Efficient resource utilization
- **Easy Management**: Single point of control

## 🔒 Security Best Practices

### Server Security:
```bash
# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Create non-root user
sudo adduser senderblade
sudo usermod -aG sudo senderblade

# Install fail2ban
sudo apt install -y fail2ban
```

### Email Security:
- **DKIM Signing**: Digital signatures
- **SPF Records**: Authorized senders
- **DMARC Policy**: Authentication policy
- **TLS Encryption**: Secure connections

## 📈 Testing & Monitoring

### Test Email Delivery:
```bash
# Test SMTP connection
telnet your-server-ip 25

# Test authentication
openssl s_client -connect your-server-ip:587 -starttls smtp
```

### Monitor Server Health:
- **Log Files**: `/var/log/mail.log`
- **Queue Status**: `mailq`
- **Connection Tests**: `netstat -tlnp`

## 🚀 Production Deployment

### Launch Checklist:
- ✅ VPS provisioned and secured
- ✅ Mail server installed and configured
- ✅ DNS records configured for all domains
- ✅ SSL certificates installed
- ✅ DKIM/SPF/DMARC configured
- ✅ SenderBlade updated with server details
- ✅ Test emails sent successfully
- ✅ Monitoring setup

### Expected Performance:
- **Sending Capacity**: 10,000+ emails/day
- **Multiple Domains**: Unlimited
- **Subdomain Variations**: Unlimited
- **Inbox Rate**: 80%+ with proper setup

---

## 🎯 Next Steps

1. **Choose VPS Provider**: DigitalOcean recommended
2. **Register Domains**: Get 3-5 domains for testing
3. **Deploy Server**: Use Mail-in-a-Box for easy setup
4. **Configure DNS**: Set up all required records
5. **Test Integration**: Connect SenderBlade to server
6. **Monitor Results**: Track inbox delivery rates

**Ready to build your own email empire!** 🚀📧