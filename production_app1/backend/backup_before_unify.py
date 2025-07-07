"""
Backup Everything Before Unification
Protecting all your working code, mate!
"""
import shutil
import os
from datetime import datetime

def backup_everything():
    """Backup all important files before unification"""
    
    print("🛡️ BACKING UP EVERYTHING BEFORE UNIFICATION")
    print("=" * 50)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backup_before_unify_{timestamp}'
    
    try:
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        print(f"📁 Created backup directory: {backup_dir}")
        
        # Files to backup (your precious working code)
        important_files = [
            'app_sender.py',  # Main SenderBlade app
            'senderblade_admin_final.py',  # Working admin system
            'simple_admin.py',  # Admin authentication
            'enterprise_auth.py',  # User management
            'sender.db',  # Your database
            'database.db',  # Secondary database
        ]
        
        # Backup each file
        for file in important_files:
            if os.path.exists(file):
                shutil.copy2(file, backup_dir)
                print(f"✅ Backed up: {file}")
            else:
                print(f"⚠️  File not found: {file}")
        
        # Backup API files (your working email system)
        api_files = [
            'lists_api.py',
            'smtp_api_fixed.py', 
            'proxy_api_fixed.py',
            'spinner_api.py',
            'campaigns_api.py',
            'generator_api.py',
            'auth_api.py',
            'health_api.py'
        ]
        
        for file in api_files:
            if os.path.exists(file):
                shutil.copy2(file, backup_dir)
                print(f"✅ Backed up API: {file}")
        
        print(f"\n🎉 BACKUP COMPLETE!")
        print(f"📁 All your working code is safe in: {backup_dir}")
        print("🛡️ If anything goes wrong, we can restore everything!")
        
        return backup_dir
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

if __name__ == "__main__":
    backup_everything()