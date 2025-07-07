#!/bin/bash

# DIY Mail Server Setup Script
# Run this on your VPS

echo "🚀 Setting up DIY Mail Server..."

# Update system
apt update && apt upgrade -y

# Install Postfix (mail server)
apt install postfix postfix-pcre -y

# Install additional tools
apt install mailutils swaks -y

# Configure Postfix for relay
cat > /etc/postfix/main.cf << 'EOF'
# Basic Postfix Configuration
myhostname = mail.finleyfingoosknj.shop
mydomain = finleyfingoosknj.shop
myorigin = $mydomain
inet_interfaces = all
inet_protocols = ipv4
mydestination = 
relayhost = 
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128 0.0.0.0/0
mailbox_size_limit = 0
recipient_delimiter = +
home_mailbox = Maildir/

# SMTP Authentication
smtpd_sasl_auth_enable = yes
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
smtpd_sasl_security_options = noanonymous
broken_sasl_auth_clients = yes

# TLS Configuration
smtpd_tls_cert_file = /etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file = /etc/ssl/private/ssl-cert-snakeoil.key
smtpd_use_tls = yes
smtpd_tls_session_cache_database = btree:${data_directory}/smtpd_scache
smtp_tls_session_cache_database = btree:${data_directory}/smtp_scache

# Relay restrictions
smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination

# Custom header cleanup (allows spoofing)
header_checks = pcre:/etc/postfix/header_checks
EOF

# Create header cleanup rules (this allows From spoofing)
cat > /etc/postfix/header_checks << 'EOF'
# Allow any From address (disable sender verification)
/^From:.*/ IGNORE
EOF

# Restart Postfix
systemctl restart postfix
systemctl enable postfix

# Create SMTP user
useradd -m smtpuser
echo "smtpuser:smtp123pass" | chpasswd

echo "✅ Mail server setup complete!"
echo "📧 SMTP Settings:"
echo "Host: $(curl -s ifconfig.me)"
echo "Port: 25"
echo "Username: smtpuser"
echo "Password: smtp123pass"
echo "From: ANY EMAIL ADDRESS (spoofing enabled)"