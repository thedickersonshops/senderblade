#!/bin/bash

# HOME MAIL SERVER SETUP
# Run this on your home computer/server
# Requires: Port forwarding on router (port 25 -> your computer)

echo "🏠 Setting up HOME MAIL SERVER..."
echo "This will turn your home into a mail server!"

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Create mail server directory
mkdir -p ~/mail-server
cd ~/mail-server

# Create Docker Compose for mail server
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  postfix:
    image: catatnight/postfix
    hostname: mail.finleyfingoosknj.shop
    environment:
      - maildomain=finleyfingoosknj.shop
      - smtp_user=admin:smtp123pass
    ports:
      - "25:25"
      - "587:587"
    volumes:
      - ./postfix:/etc/postfix/main.cf.d
    restart: unless-stopped

  # Optional: Web interface
  roundcube:
    image: roundcube/roundcubemail
    ports:
      - "8080:80"
    environment:
      - ROUNDCUBEMAIL_DEFAULT_HOST=postfix
    depends_on:
      - postfix
EOF

# Create custom Postfix config for spoofing
mkdir -p postfix
cat > postfix/custom.cf << 'EOF'
# Allow any From address (spoofing enabled)
smtpd_sender_restrictions = 
smtpd_recipient_restrictions = permit_mynetworks,reject_unauth_destination
disable_vrfy_command = yes

# No authentication required for local network
smtpd_sasl_auth_enable = no
EOF

# Start the mail server
docker-compose up -d

echo "✅ HOME MAIL SERVER RUNNING!"
echo ""
echo "📧 SMTP Settings:"
echo "Host: $(curl -s ifconfig.me)"
echo "Port: 25 or 587"
echo "Username: admin"
echo "Password: smtp123pass"
echo "From: ANY EMAIL ADDRESS (spoofing enabled)"
echo ""
echo "🔧 Router Setup Required:"
echo "1. Forward port 25 to this computer"
echo "2. Forward port 587 to this computer"
echo "3. Set up dynamic DNS (optional)"
echo ""
echo "🌐 Web Interface: http://localhost:8080"