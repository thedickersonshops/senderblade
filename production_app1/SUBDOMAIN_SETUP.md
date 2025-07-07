# Random Subdomain Setup Guide

## 🎯 What You Need to Configure

### DNS Settings (Required)
To use random subdomains, you need to set up a **wildcard DNS record** for your domain.

#### Example: If your domain is `company.com`

**Add this DNS record:**
```
Type: A Record
Name: *
Value: [Your Server IP]
TTL: 300 (or default)
```

**Or for mail-specific wildcard:**
```
Type: A Record  
Name: *.mail
Value: [Your Server IP]
TTL: 300
```

### How It Works
- **Without Setup**: `sender@company.com`
- **With Wildcard**: `sender@abc123.company.com`, `sender@newsletter.company.com`, etc.
- **Random Examples**: 
  - `sender@x7k9m2.company.com`
  - `sender@marketing.company.com`
  - `sender@n4p8q1s.company.com`

## 🔧 DNS Provider Instructions

### Cloudflare
1. Go to DNS settings
2. Add Record: Type `A`, Name `*`, Content `[Your IP]`
3. Save

### GoDaddy
1. DNS Management
2. Add Record: Type `A`, Host `*`, Points to `[Your IP]`
3. Save

### Namecheap
1. Advanced DNS
2. Add Record: Type `A Record`, Host `*`, Value `[Your IP]`
3. Save

### Google Domains
1. DNS settings
2. Custom records: Type `A`, Name `*`, Data `[Your IP]`
3. Save

## ⚙️ SMTP Server Requirements

### Your SMTP Must Support
- **Domain Authentication**: Your SMTP should authenticate your main domain
- **Subdomain Sending**: Most SMTP providers (Gmail, Outlook) support subdomain sending if you own the main domain

### Recommended SMTP Settings
```
Host: smtp.gmail.com (or your provider)
Port: 587
Username: your-email@company.com
Password: your-app-password
From Email: your-email@company.com (base email)
```

## 🎲 Randomness Levels

### Current Implementation
- **Predefined Subdomains**: newsletter, marketing, campaigns, etc. (up to 10 chars)
- **Random Alphanumeric**: 3-10 character random strings (abc123, x7k9m2, etc.)
- **Mix Strategy**: 50/50 chance between predefined and random

### Examples Generated
```
sender@mail.company.com
sender@newsletter.company.com  
sender@abc123.company.com
sender@x7k9m2p.company.com
sender@marketing.company.com
sender@n4p8q1s.company.com
```

## ✅ Testing Your Setup

### 1. DNS Test
```bash
nslookup random123.yourdomain.com
```
Should return your server IP.

### 2. Email Test
Send a test campaign with "Random Subdomains" enabled and check the From headers in received emails.

### 3. Delivery Test
Monitor your Activity Log for successful deliveries.

## 🚨 Important Notes

### Legal & Legitimate Use
- ✅ **Your Domain Only**: Only works with domains you own
- ✅ **Proper Authentication**: Uses your legitimate SMTP credentials  
- ✅ **Professional Practice**: Standard email marketing technique
- ✅ **Deliverability**: Helps avoid spam filters legitimately

### Technical Requirements
- **DNS Wildcard**: Must be configured for subdomains to resolve
- **SMTP Authentication**: Your SMTP must authenticate your main domain
- **Domain Ownership**: You must own the domain being used

## 🎯 Benefits

### Better Deliverability
- **Subdomain Rotation**: Reduces chance of domain reputation issues
- **Spam Filter Avoidance**: Legitimate technique used by major platforms
- **Professional Appearance**: Looks like enterprise email infrastructure

### Legitimate Marketing
- **Industry Standard**: Used by MailChimp, Constant Contact, etc.
- **Domain Reputation**: Protects your main domain reputation
- **Scalability**: Supports high-volume legitimate campaigns

---

**Ready to use after DNS setup!** 🚀