# ☁️ CloudFlare Setup for piushdokajshfdk.store

## 🚀 STEP-BY-STEP SETUP FOR YOUR DOMAIN

### **Step 1: Add Domain to CloudFlare**
1. **Go to**: https://dash.cloudflare.com
2. **Sign up** for free CloudFlare account (if you don't have one)
3. **Click "Add a Site"**
4. **Enter your domain**: `piushdokajshfdk.store`
5. **Click "Add Site"**
6. **Select FREE plan** (click "Continue")

### **Step 2: CloudFlare Will Scan Your Domain**
- CloudFlare will automatically scan for existing DNS records
- **Click "Continue"** after scan completes
- Don't worry if it finds no records - we'll add them

### **Step 3: Change Nameservers at Spaceship**
CloudFlare will show you 2 nameservers like:
```
ava.ns.cloudflare.com
kai.ns.cloudflare.com
```

**Go to Spaceship (your domain registrar):**
1. **Login to Spaceship**: https://spaceship.com
2. **Go to Domain Management**
3. **Find**: piushdokajshfdk.store
4. **Click "Manage DNS"** or "Nameservers"
5. **Change nameservers** to CloudFlare's nameservers:
   - Remove existing nameservers
   - Add: `ava.ns.cloudflare.com` (example)
   - Add: `kai.ns.cloudflare.com` (example)
6. **Save changes**

### **Step 4: Wait for Activation (5-15 minutes)**
- CloudFlare will verify the nameserver change
- You'll get an email when it's active
- Status will change from "Pending" to "Active"

### **Step 5: Add DNS Records**
Once active, add these DNS records in CloudFlare:

#### **A Record for Root Domain:**
```
Type: A
Name: @
Content: YOUR_VPS_IP (e.g., 52.53.153.46)
Proxy status: Proxied (orange cloud) ✅
TTL: Auto
```

#### **A Record for WWW:**
```
Type: A
Name: www
Content: YOUR_VPS_IP (same as above)
Proxy status: Proxied (orange cloud) ✅
TTL: Auto
```

#### **Optional - Mail Record (if needed later):**
```
Type: A
Name: mail
Content: YOUR_VPS_IP
Proxy status: DNS only (gray cloud) ❌
TTL: Auto
```

### **Step 6: Configure SSL/TLS**
1. **Go to SSL/TLS tab**
2. **Set encryption mode**: Full (strict)
3. **Enable "Always Use HTTPS"**: ON
4. **Enable "HTTP Strict Transport Security"**: ON

### **Step 7: Configure Security**
1. **Go to Security tab**
2. **Set Security Level**: Medium
3. **Enable "Browser Integrity Check"**: ON

### **Step 8: Test Your Setup**
After DNS propagation (5-30 minutes):
- **Visit**: https://piushdokajshfdk.store
- **Should show**: CloudFlare's default page or your VPS content
- **Check SSL**: Green lock icon in browser

## 🎯 WHAT YOU'LL GET

### **Before CloudFlare:**
```
Users → Your VPS IP directly
- Exposed IP address
- No DDoS protection
- No SSL certificate
- Potential blacklist issues
```

### **After CloudFlare:**
```
Users → CloudFlare IPs → Your Hidden VPS
- Clean CloudFlare IP reputation
- Free SSL certificate
- DDoS protection
- Hidden VPS IP
- Global CDN speed
```

## 🔧 SPACESHIP NAMESERVER CHANGE

### **Detailed Spaceship Steps:**
1. **Login**: https://spaceship.com/login
2. **Dashboard**: Click "Domains"
3. **Find Domain**: piushdokajshfdk.store
4. **Click**: "Manage" or gear icon
5. **DNS Settings**: Look for "Nameservers" or "DNS Management"
6. **Change Mode**: From "Default" to "Custom"
7. **Enter CloudFlare Nameservers**:
   - Primary: (CloudFlare will give you these)
   - Secondary: (CloudFlare will give you these)
8. **Save**: Click "Update" or "Save"

### **Example CloudFlare Nameservers:**
```
Primary: ava.ns.cloudflare.com
Secondary: kai.ns.cloudflare.com
```
*(Your actual nameservers will be different)*

## ⏰ TIMELINE

### **Immediate (0-5 minutes):**
- Add domain to CloudFlare
- Get nameserver information
- Change nameservers at Spaceship

### **Short Wait (5-30 minutes):**
- Nameserver propagation
- CloudFlare activation
- DNS record setup

### **Ready to Use (30-60 minutes):**
- Full CloudFlare protection active
- SSL certificate issued
- Domain pointing to your VPS

## 🎉 FINAL RESULT

### **Your Domain Will Be:**
- **https://piushdokajshfdk.store** → Your SenderBlade app
- **Protected by CloudFlare** (DDoS, SSL, CDN)
- **Hidden VPS IP** (complete anonymity)
- **Professional appearance** (custom domain + SSL)

### **Perfect for SenderBlade:**
- ✅ **Users access clean domain** (not IP address)
- ✅ **VPS IP hidden** (CloudFlare proxy)
- ✅ **Free SSL certificate** (professional look)
- ✅ **DDoS protection** (enterprise security)
- ✅ **Global CDN** (fast worldwide access)

## 💡 FREE VPS OPTIONS (While You Decide)

### **Oracle Cloud (Always Free):**
- **1 GB RAM** VM (forever free)
- **All ports open** (including SMTP)
- **No time limit** (truly free)
- **Good for testing** SenderBlade

### **Google Cloud ($300 credit):**
- **$300 free credit** (3 months)
- **All SMTP ports** available
- **Professional infrastructure**

### **Azure ($200 credit):**
- **$200 free credit** (30 days)
- **Good performance**
- **SMTP ports available**

## 🚀 NEXT STEPS

1. **Add domain to CloudFlare** (do this now!)
2. **Change nameservers** at Spaceship
3. **Wait for activation** (15-30 minutes)
4. **Add DNS records** pointing to your VPS
5. **Test domain access** (https://piushdokajshfdk.store)

**Ready to add piushdokajshfdk.store to CloudFlare?** ☁️🔥💀