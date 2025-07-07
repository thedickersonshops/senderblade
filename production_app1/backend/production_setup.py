"""
Production Setup Script - Add missing features for VPS deployment
"""
import os
import sqlite3
import hashlib
from datetime import datetime

def setup_production_features():
    """Add missing production features"""
    print("🚀 SETTING UP PRODUCTION FEATURES")
    print("=" * 50)
    
    # 1. Create admin user
    create_admin_user()
    
    # 2. Setup logging directories
    setup_logging()
    
    # 3. Create backup directories
    setup_backups()
    
    # 4. Initialize production database
    setup_production_db()
    
    # 5. Create environment file
    create_env_file()
    
    print("✅ Production setup complete!")

def create_admin_user():
    """Create admin user for authentication"""
    print("👤 Creating admin user...")
    
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                is_admin BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default admin user
        admin_password = "admin123"  # Change this!
        password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, email, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', password_hash, 'admin@senderblade.com', True))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Admin user created: admin / {admin_password}")
        print("⚠️  CHANGE DEFAULT PASSWORD AFTER DEPLOYMENT!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

def setup_logging():
    """Setup logging directories"""
    print("📝 Setting up logging...")
    
    try:
        os.makedirs('logs', exist_ok=True)
        os.makedirs('logs/campaigns', exist_ok=True)
        os.makedirs('logs/smtp', exist_ok=True)
        os.makedirs('logs/errors', exist_ok=True)
        
        print("✅ Logging directories created")
        
    except Exception as e:
        print(f"❌ Error setting up logging: {e}")

def setup_backups():
    """Setup backup directories"""
    print("💾 Setting up backups...")
    
    try:
        os.makedirs('backups', exist_ok=True)
        os.makedirs('backups/database', exist_ok=True)
        os.makedirs('backups/configs', exist_ok=True)
        
        print("✅ Backup directories created")
        
    except Exception as e:
        print(f"❌ Error setting up backups: {e}")

def setup_production_db():
    """Initialize production database with additional tables"""
    print("🗄️ Setting up production database...")
    
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        # Add production-specific tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                permissions TEXT DEFAULT 'read',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default settings
        default_settings = [
            ('max_emails_per_hour', '1000', 'Maximum emails per hour limit'),
            ('max_campaigns_per_day', '10', 'Maximum campaigns per day'),
            ('enable_rate_limiting', 'true', 'Enable API rate limiting'),
            ('backup_frequency', '24', 'Database backup frequency in hours'),
            ('log_retention_days', '30', 'Log file retention period'),
        ]
        
        for setting in default_settings:
            cursor.execute('''
                INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            ''', setting)
        
        conn.commit()
        conn.close()
        
        print("✅ Production database initialized")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

def create_env_file():
    """Create environment configuration file"""
    print("⚙️ Creating environment file...")
    
    try:
        env_content = f"""# SenderBlade Production Configuration
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Flask Configuration
FLASK_ENV=production
SECRET_KEY={os.urandom(24).hex()}
DEBUG=False

# Database Configuration
DATABASE_URL=sqlite:///sender.db

# Security Settings
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
WTF_CSRF_ENABLED=True

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/senderblade.log

# Email Settings
MAX_EMAILS_PER_HOUR=1000
MAX_CAMPAIGNS_PER_DAY=10

# Backup Settings
BACKUP_ENABLED=True
BACKUP_FREQUENCY=24

# Server Settings
HOST=0.0.0.0
PORT=5001

# CHANGE THESE VALUES FOR PRODUCTION!
ADMIN_EMAIL=admin@yourdomain.com
SMTP_TIMEOUT=30
CONNECTION_POOL_SIZE=20
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Environment file created (.env)")
        print("⚠️  Update .env with your production values!")
        
    except Exception as e:
        print(f"❌ Error creating environment file: {e}")

def create_supervisor_config():
    """Create supervisor configuration for process management"""
    print("🔧 Creating supervisor configuration...")
    
    supervisor_config = """[program:senderblade]
command=/usr/bin/python3 app_sender.py
directory=/path/to/senderblade
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/senderblade.log
environment=FLASK_ENV=production
"""
    
    try:
        with open('senderblade.conf', 'w') as f:
            f.write(supervisor_config)
        
        print("✅ Supervisor config created (senderblade.conf)")
        print("📝 Copy to /etc/supervisor/conf.d/ on your VPS")
        
    except Exception as e:
        print(f"❌ Error creating supervisor config: {e}")

def create_nginx_config():
    """Create nginx configuration"""
    print("🌐 Creating nginx configuration...")
    
    nginx_config = """server {
    listen 80;
    server_name your-domain.com;  # Change this!
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;  # Change this!
    
    # SSL Configuration (certbot will add these)
    # ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static {
        alias /path/to/senderblade/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""
    
    try:
        with open('senderblade_nginx.conf', 'w') as f:
            f.write(nginx_config)
        
        print("✅ Nginx config created (senderblade_nginx.conf)")
        print("📝 Copy to /etc/nginx/sites-available/ on your VPS")
        
    except Exception as e:
        print(f"❌ Error creating nginx config: {e}")

if __name__ == "__main__":
    print("🚀 SENDERBLADE PRODUCTION SETUP")
    print("Preparing for VPS deployment...")
    print()
    
    setup_production_features()
    create_supervisor_config()
    create_nginx_config()
    
    print("\n🎉 PRODUCTION SETUP COMPLETE!")
    print("\n📋 NEXT STEPS:")
    print("1. Upload SenderBlade to your VPS")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run: python production_setup.py")
    print("4. Configure nginx and supervisor")
    print("5. Get SSL certificate: certbot --nginx")
    print("6. Start services: supervisorctl start senderblade")
    print("\n⚠️  IMPORTANT: Change default passwords and update .env file!")