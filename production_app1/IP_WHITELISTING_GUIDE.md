# 🛡️ IP Whitelisting & Delisting Guide

## 🚨 Emergency IP Recovery Plan

### If Your Server IP Gets Blacklisted, Here's How to Fix It:

## 🔧 Major Blacklist Removal Services

### 1. Spamhaus (Most Important)
**URL**: https://www.spamhaus.org/lookup/
**Process**:
```
1. Go to Spamhaus lookup
2. Enter your server IP
3. If listed, click "Remove" link
4. Fill out removal form with:
   - Server IP address
   - Reason for delisting
   - Steps taken to prevent future issues
5. Wait 24-48 hours for review
```

### 2. SpamCop
**URL**: https://www.spamcop.net/bl.shtml
**Process**:
```
1. Check if IP is listed
2. SpamCop auto-delists after 24 hours of no complaints
3. No manual removal needed
4. Just wait and monitor
```

### 3. SURBL/URIBL
**URL**: https://admin.uribl.com/
**Process**:
```
1. Submit delisting request
2. Provide server details
3. Explain legitimate use
4. Usually processed within 24 hours
```

### 4. Barracuda Central
**URL**: https://www.barracudacentral.org/rbl/removal-request
**Process**:
```
1. Submit removal request form
2. Provide IP and contact details
3. Explain server purpose
4. Usually delisted within 2-4 hours
```

### 5. SORBS
**URL**: http://www.sorbs.net/delisting/
**Process**:
```
1. Use their delisting form
2. Provide technical justification
3. May require payment ($50-100)
4. Processing time: 1-3 days
```

## 🛠️ Automated Delisting Script

### Create Monitoring & Auto-Delist Script:
```bash
#!/bin/bash
# IP Blacklist Monitor & Auto-Delist
# Save as: /root/ip_monitor.sh

SERVER_IP="YOUR_SERVER_IP"
EMAIL="your-email@domain.com"

# Blacklists to check
BLACKLISTS=(
    "zen.spamhaus.org"
    "bl.spamcop.net"
    "dnsbl.sorbs.net"
    "b.barracudacentral.org"
    "blacklist.woody.ch"
    "dnsbl-1.uceprotect.net"
    "dnsbl-2.uceprotect.net"
    "dnsbl-3.uceprotect.net"
)

echo "🔍 Checking IP: $SERVER_IP"
echo "📅 Date: $(date)"
echo "================================"

BLACKLISTED=false

for bl in "${BLACKLISTS[@]}"; do
    result=$(dig +short $SERVER_IP.$bl)
    if [ -n "$result" ]; then
        echo "⚠️  BLACKLISTED on $bl: $result"
        BLACKLISTED=true
        
        # Auto-submit delisting requests
        case $bl in
            "zen.spamhaus.org")
                echo "📧 Spamhaus delisting: https://www.spamhaus.org/lookup/"
                ;;
            "b.barracudacentral.org")
                echo "📧 Barracuda delisting: https://www.barracudacentral.org/rbl/removal-request"
                ;;
            "dnsbl.sorbs.net")
                echo "📧 SORBS delisting: http://www.sorbs.net/delisting/"
                ;;
        esac
    else
        echo "✅ Clean on $bl"
    fi
done

if [ "$BLACKLISTED" = true ]; then
    echo ""
    echo "🚨 ACTION REQUIRED: IP is blacklisted!"
    echo "📧 Sending alert email..."
    
    # Send email alert (requires mailutils)
    echo "Server IP $SERVER_IP is blacklisted. Check logs and submit delisting requests." | \
    mail -s "🚨 IP Blacklist Alert" $EMAIL
    
    # Stop mail services temporarily
    echo "⏸️  Stopping mail services..."
    systemctl stop postfix
    
else
    echo ""
    echo "🎉 All clear! IP is not blacklisted."
fi

echo "================================"
```

### Set up automated monitoring:
```bash
# Make script executable
chmod +x /root/ip_monitor.sh

# Run every hour
crontab -e
# Add this line:
0 * * * * /root/ip_monitor.sh >> /var/log/ip_monitor.log 2>&1
```

## 🌐 Proactive Whitelisting Services

### 1. Return Path (Validity)
**URL**: https://validity.com/
**Service**: Sender reputation monitoring
**Cost**: $200-500/month
**Benefits**: 
- Proactive monitoring
- ISP relationships
- Faster delisting

### 2. SendGrid Expert Services
**URL**: https://sendgrid.com/
**Service**: IP reputation management
**Cost**: $100-300/month
**Benefits**:
- Dedicated IP pools
- Reputation monitoring
- Expert support

### 3. Mailgun Deliverability Services
**URL**: https://www.mailgun.com/
**Service**: IP warming and monitoring
**Cost**: $50-200/month
**Benefits**:
- Automated IP warming
- Blacklist monitoring
- Delisting assistance

## 🔒 Prevention Strategies

### 1. IP Reputation Services (Free)
```bash
# Check IP reputation before sending
curl -s "https://api.abuseipdb.com/api/v2/check?ipAddress=$SERVER_IP" \
  -H "Key: YOUR_FREE_API_KEY" \
  -H "Accept: application/json"

# Sender Score (free check)
curl -s "https://www.senderscore.org/lookup/?lookup=$SERVER_IP"
```

### 2. Gradual IP Warming
```python
# Add to SenderBlade
WARMUP_SCHEDULE = {
    'week_1': 50,    # 50 emails/day
    'week_2': 100,   # 100 emails/day
    'week_3': 250,   # 250 emails/day
    'week_4': 500,   # 500 emails/day
    'week_5': 1000,  # 1000 emails/day
    'week_6': 2500,  # 2500 emails/day
}

def get_daily_limit():
    # Calculate based on server age
    server_age_days = get_server_age()
    if server_age_days < 7:
        return 50
    elif server_age_days < 14:
        return 100
    # ... continue pattern
```

### 3. Real-time Monitoring
```bash
# Install monitoring tools
sudo apt install -y mailutils dnsutils

# Create real-time alert system
#!/bin/bash
# Save as: /root/realtime_monitor.sh

while true; do
    /root/ip_monitor.sh
    if grep -q "BLACKLISTED" /var/log/ip_monitor.log; then
        # Immediate action
        systemctl stop postfix
        echo "🚨 EMERGENCY: Mail services stopped due to blacklisting"
        break
    fi
    sleep 300  # Check every 5 minutes
done
```

## 📞 Emergency Contact List

### ISP Direct Contacts (for serious issues):
```
Gmail Postmaster: postmaster-en@google.com
Outlook/Hotmail: postmaster@hotmail.com
Yahoo: postmaster@yahoo-inc.com
AOL: postmaster@aol.com
```

### Professional Services:
```
Return Path: support@returnpath.com
SendGrid: support@sendgrid.com
Mailgun: support@mailgun.com
```

## 🎯 Quick Recovery Checklist

### If Blacklisted (Do Immediately):
1. ✅ **Stop Sending**: `systemctl stop postfix`
2. ✅ **Check All Lists**: Run monitoring script
3. ✅ **Submit Requests**: Use automated forms
4. ✅ **Review Logs**: Check `/var/log/mail.log`
5. ✅ **Fix Issues**: Address root cause
6. ✅ **Wait**: 24-48 hours for delisting
7. ✅ **Test**: Send small batch first
8. ✅ **Resume**: Gradual increase

### Prevention Checklist:
1. ✅ **Daily Monitoring**: Automated blacklist checks
2. ✅ **Gradual Warmup**: Follow warming schedule
3. ✅ **Quality Content**: No spam triggers
4. ✅ **Authentication**: SPF/DKIM/DMARC setup
5. ✅ **Bounce Handling**: Monitor bounce rates
6. ✅ **Complaint Monitoring**: Track spam complaints

## 🚀 Advanced Protection

### Multiple IP Strategy:
```bash
# Get additional IPs from DartNode
# Rotate between IPs for sending
# If one gets blacklisted, use others

# Example rotation in SenderBlade:
IP_POOL = [
    "PRIMARY_IP",
    "SECONDARY_IP", 
    "TERTIARY_IP"
]

def get_next_ip():
    # Check blacklist status
    clean_ips = [ip for ip in IP_POOL if not is_blacklisted(ip)]
    return random.choice(clean_ips)
```

### Reputation Insurance:
- **Cost**: $50-100/month
- **Coverage**: Professional delisting services
- **Response**: 24-hour emergency support
- **Providers**: Return Path, SendGrid, Mailgun

---

## 🎯 Summary

**You have multiple safety nets:**
1. **Automated Monitoring**: Hourly blacklist checks
2. **Emergency Scripts**: Auto-stop services if blacklisted
3. **Delisting Forms**: Direct access to all major lists
4. **Professional Services**: Paid support if needed
5. **Multiple IPs**: Backup sending infrastructure

**With proper monitoring and quick response, blacklisting is recoverable within 24-48 hours!** 🚀

Your DartNode server will be well-protected! 🛡️