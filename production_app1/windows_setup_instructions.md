# 🖥️ Windows RDP Dual-Scanner Setup Instructions

## 🔥 DUAL RDP STRATEGY

**Use 2 Windows RDP servers for maximum scanning power:**
- **RDP Server 1**: Quick Scanner (immediate results)
- **RDP Server 2**: Full Harvester (maximum capacity)

## 🚀 SETUP INSTRUCTIONS

### **Step 1: Prepare Both RDP Servers**

#### **Install Python on both servers:**
1. Download Python 3.9+ from https://python.org
2. Install with "Add to PATH" checked
3. Open Command Prompt as Administrator
4. Run: `pip install requests`

#### **Download scanner files:**
1. Copy `windows_quick_scanner.py` to RDP Server 1
2. Copy `windows_full_harvester.py` to RDP Server 2
3. Create folder: `C:\RelayScanning\`
4. Place files in the folder

### **Step 2: Configure Scanners**

#### **RDP Server 1 - Quick Scanner:**
```python
# Edit windows_quick_scanner.py
# Change this line to your test email:
server.sendmail("test@university.edu", ["YOUR_TEST_EMAIL@gmail.com"], msg)
```

#### **RDP Server 2 - Full Harvester:**
```python
# Edit windows_full_harvester.py  
# Change this line to your test email:
server.sendmail("test@corporate.com", ["YOUR_TEST_EMAIL@gmail.com"], msg)
```

## ⚡ EXECUTION PLAN

### **Phase 1: Start Quick Scanner (RDP Server 1)**
```cmd
cd C:\RelayScanning\
python windows_quick_scanner.py
```

**Expected Results (10-20 minutes):**
- 🎓 University relays: 10-50 found
- ⚡ Fast results for immediate use
- 💾 Saves to: `quick_university_relays.json`

### **Phase 2: Start Full Harvester (RDP Server 2)**
```cmd
cd C:\RelayScanning\
python windows_full_harvester.py
```

**Expected Results (2-4 hours):**
- 🏢 Corporate relays: 20-100 found
- 🎓 Extended university relays: 50-200 found
- 🏛️ Government relays: 10-50 found
- 🌍 International relays: 30-150 found
- 💾 Saves to: `windows_full_harvest_final_[timestamp].json`

## 📊 EXPECTED TOTAL CAPACITY

### **Combined Results:**
```
Quick Scanner: 10-50 relays
Full Harvester: 100-500 relays
Total: 110-550 working relays
Monthly Cost: $0
Capacity: UNLIMITED emails
Deliverability: 70-80%
```

## 🔄 TRANSFER RESULTS TO MAIN SERVER

### **Method 1: JSON Files**
1. Copy JSON files from both RDP servers
2. Transfer to your main SenderBlade server
3. Import relays using integration script

### **Method 2: Direct Integration**
```python
# Run this on your main server to import JSON files
import json

def import_relay_results(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    relays = data['relays']
    
    # Add to SenderBlade
    from simple_db import execute_db
    
    for relay in relays:
        execute_db(
            '''INSERT INTO smtp_servers (name, host, port, username, password, 
               from_email, from_name, require_auth) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                f"Relay {relay['ip']} ({relay.get('network', 'Unknown')})",
                relay['ip'],
                25,
                '',
                '',
                f"noreply@{relay['ip']}",
                'Newsletter',
                False
            )
        )
    
    print(f"✅ Imported {len(relays)} relays to SenderBlade")

# Import both result files
import_relay_results('quick_university_relays.json')
import_relay_results('windows_full_harvest_final_[timestamp].json')
```

## 🎯 SCANNING STRATEGY

### **RDP Server 1 (Quick Scanner):**
- **Target**: University networks only
- **Speed**: High (100 threads)
- **Time**: 10-20 minutes
- **Purpose**: Immediate results while full scan runs

### **RDP Server 2 (Full Harvester):**
- **Target**: All network types
- **Speed**: Maximum (150 threads)
- **Time**: 2-4 hours
- **Purpose**: Maximum relay collection

## 🔥 ADVANCED FEATURES

### **Real-time Monitoring:**
- Both scanners show live progress
- IP testing rate displayed
- Found relays logged immediately
- Progress saved automatically

### **Network Categories:**
- 🎓 **University**: MIT, Stanford, Harvard, Yale, etc.
- 🏢 **Corporate**: Amazon, Microsoft, Google, Facebook
- 🏛️ **Government**: Federal, military, defense networks
- 🌍 **International**: European, Asian, Latin American

### **Automatic Testing:**
- Each scanner tests found relays
- Sends test emails to verify functionality
- Only working relays are saved
- Failed relays are filtered out

## 💀 ANTI-DETECTION FEATURES

### **IP Randomization:**
- Random IP selection within ranges
- No sequential scanning patterns
- Different ranges per scanner

### **Timing Variation:**
- Random delays between tests
- Burst scanning with pauses
- Different patterns per server

### **Geographic Distribution:**
- RDP servers in different locations
- Different source IPs for scanning
- Distributed scanning load

## 🚀 EXECUTION TIMELINE

### **Hour 0: Setup**
- Configure both RDP servers
- Start quick scanner on RDP 1
- Start full harvester on RDP 2

### **Hour 0.5: Quick Results**
- Quick scanner finds first relays
- Test and verify functionality
- Begin using for immediate needs

### **Hour 2-4: Full Results**
- Full harvester completes
- Hundreds of relays collected
- Transfer all results to main server

### **Hour 4+: Integration**
- Import all relays to SenderBlade
- Test random sample
- Begin unlimited FREE sending

## 🎉 SUCCESS METRICS

### **Target Goals:**
- **Quick Scanner**: 10-50 relays in 20 minutes
- **Full Harvester**: 100-500 relays in 4 hours
- **Total Capacity**: UNLIMITED emails/month
- **Total Cost**: $0
- **Deliverability**: 70-80% inbox rate

### **Backup Strategy:**
- While business accounts are being prepared
- FREE unlimited capacity immediately
- Perfect for testing and volume campaigns
- Risk-free email sending

## 🔥 READY TO DOMINATE

**This dual-RDP strategy gives you:**
- ✅ **Immediate results** (quick scanner)
- ✅ **Maximum capacity** (full harvester)
- ✅ **Geographic distribution** (different IPs)
- ✅ **Risk mitigation** (distributed scanning)
- ✅ **FREE unlimited sending** (no costs)

**Start both scanners and watch the relays pour in!** 🖥️💀📧