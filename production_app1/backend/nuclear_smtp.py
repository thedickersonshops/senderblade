"""
Nuclear SMTP Rotation System - Beat the Blacklist Mafia
"""
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NuclearSMTP:
    def __init__(self):
        # Emergency SMTP services (no verification needed)
        self.smtp_services = EMERGENCY_SMTP_SERVICES + [
            {
                'name': 'SendGrid',
                'host': 'smtp.sendgrid.net',
                'port': 587,
                'username': 'apikey',  # Always 'apikey' for SendGrid
                'password': 'YOUR_SENDGRID_API_KEY',  # Get from SendGrid
                'daily_limit': 100,
                'monthly_limit': 40000,
                'active': True,
                'reputation': 'excellent'
            },
            {
                'name': 'Mailgun',
                'host': 'smtp.mailgun.org',
                'port': 587,
                'username': 'postmaster@YOUR_DOMAIN.mailgun.org',
                'password': 'YOUR_MAILGUN_PASSWORD',
                'daily_limit': 300,
                'monthly_limit': 5000,
                'active': True,
                'reputation': 'excellent'
            },
            {
                'name': 'Amazon SES',
                'host': 'email-smtp.us-east-1.amazonaws.com',
                'port': 587,
                'username': 'YOUR_SES_ACCESS_KEY',
                'password': 'YOUR_SES_SECRET_KEY',
                'daily_limit': 1000,
                'monthly_limit': 50000,
                'active': True,
                'reputation': 'excellent'
            },
            {
                'name': 'Mailjet',
                'host': 'in-v3.mailjet.com',
                'port': 587,
                'username': 'YOUR_MAILJET_API_KEY',
                'password': 'YOUR_MAILJET_SECRET_KEY',
                'daily_limit': 200,
                'monthly_limit': 6000,
                'active': True,
                'reputation': 'excellent'
            },
            {
                'name': 'SparkPost',
                'host': 'smtp.sparkpostmail.com',
                'port': 587,
                'username': 'SMTP_Injection',
                'password': 'YOUR_SPARKPOST_API_KEY',
                'daily_limit': 100,
                'monthly_limit': 500,
                'active': True,
                'reputation': 'excellent'
            }
        ] if False else []  # Disable the verification-required services
        
        # Track usage
        self.usage_today = {}
        self.last_reset = time.time()
        
    def get_best_smtp(self):
        """Get the best available SMTP service"""
        # Reset daily counters if new day
        if time.time() - self.last_reset > 86400:  # 24 hours
            self.usage_today = {}
            self.last_reset = time.time()
        
        # Filter active services with available quota
        available_services = []
        for service in self.smtp_services:
            if not service['active']:
                continue
                
            service_name = service['name']
            used_today = self.usage_today.get(service_name, 0)
            
            if used_today < service['daily_limit']:
                available_services.append(service)
        
        if not available_services:
            raise Exception("All SMTP services exhausted for today")
        
        # Prefer services with excellent reputation and lower usage
        available_services.sort(key=lambda x: (
            x['reputation'] == 'excellent',  # Excellent reputation first
            -self.usage_today.get(x['name'], 0)  # Lower usage first
        ), reverse=True)
        
        return available_services[0]
    
    def send_email(self, to_email, subject, body, from_name="Newsletter", from_email=None):
        """Send email using best available SMTP service"""
        try:
            # Get best SMTP service
            smtp_service = self.get_best_smtp()
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['To'] = to_email
            
            # Use service-specific from email or provided one
            sender_email = from_email or f"noreply@{smtp_service['name'].lower()}.com"
            msg['From'] = f"{from_name} <{sender_email}>"
            
            # Add professional headers
            msg['Message-ID'] = f"<{int(time.time())}.{random.randint(1000,9999)}@{smtp_service['name'].lower()}.com>"
            msg['Date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
            msg['X-Mailer'] = f'SenderBlade Nuclear v2.0 via {smtp_service["name"]}'
            
            # Attach body
            if '<' in body:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send via selected service
            print(f"🚀 Sending via {smtp_service['name']} ({self.usage_today.get(smtp_service['name'], 0)}/{smtp_service['daily_limit']} used today)")
            
            with smtplib.SMTP(smtp_service['host'], smtp_service['port']) as server:
                server.starttls()
                server.login(smtp_service['username'], smtp_service['password'])
                server.send_message(msg)
            
            # Track usage
            service_name = smtp_service['name']
            self.usage_today[service_name] = self.usage_today.get(service_name, 0) + 1
            
            return {
                'success': True,
                'service': smtp_service['name'],
                'message': f'Email sent successfully via {smtp_service["name"]}'
            }
            
        except Exception as e:
            print(f"❌ Error sending via {smtp_service['name']}: {str(e)}")
            
            # Mark service as temporarily inactive if authentication fails
            if 'authentication' in str(e).lower() or 'login' in str(e).lower():
                smtp_service['active'] = False
                print(f"⚠️ Temporarily disabling {smtp_service['name']} due to auth error")
            
            return {
                'success': False,
                'service': smtp_service['name'],
                'error': str(e)
            }
    
    def get_service_status(self):
        """Get status of all SMTP services"""
        status = []
        for service in self.smtp_services:
            used_today = self.usage_today.get(service['name'], 0)
            status.append({
                'name': service['name'],
                'active': service['active'],
                'used_today': used_today,
                'daily_limit': service['daily_limit'],
                'remaining': service['daily_limit'] - used_today,
                'reputation': service['reputation']
            })
        return status
    
    def reset_service(self, service_name):
        """Reset/reactivate a service"""
        for service in self.smtp_services:
            if service['name'] == service_name:
                service['active'] = True
                print(f"✅ Reactivated {service_name}")
                return True
        return False

# Emergency SMTP services (no verification required)
EMERGENCY_SMTP_SERVICES = [
    {
        'name': 'Elastic Email',
        'host': 'smtp.elasticemail.com',
        'port': 2525,
        'username': 'YOUR_ELASTIC_EMAIL',
        'password': 'YOUR_ELASTIC_API_KEY',
        'daily_limit': 100,
        'active': True,
        'setup_url': 'https://elasticemail.com/account#/create-account',
        'notes': 'Works immediately - no verification needed'
    },
    {
        'name': 'SMTP2GO',
        'host': 'mail.smtp2go.com', 
        'port': 2525,
        'username': 'YOUR_SMTP2GO_USERNAME',
        'password': 'YOUR_SMTP2GO_PASSWORD',
        'daily_limit': 33,  # 1000/month = ~33/day
        'active': True,
        'setup_url': 'https://www.smtp2go.com/pricing/',
        'notes': 'Instant access - no gatekeeping'
    },
    {
        'name': 'SocketLabs',
        'host': 'smtp.socketlabs.com',
        'port': 587,
        'username': 'YOUR_SOCKETLABS_USERNAME', 
        'password': 'YOUR_SOCKETLABS_PASSWORD',
        'daily_limit': 1333,  # 40K/month trial = 1333/day
        'active': True,
        'setup_url': 'https://www.socketlabs.com/signup/',
        'notes': '40K emails FREE trial - no verification'
    },
    {
        'name': 'Postmark',
        'host': 'smtp.postmarkapp.com',
        'port': 587,
        'username': 'YOUR_POSTMARK_TOKEN',
        'password': 'YOUR_POSTMARK_TOKEN',  # Same as username
        'daily_limit': 3,  # 100/month = ~3/day
        'active': True,
        'setup_url': 'https://postmarkapp.com/sign_up',
        'notes': '100 emails/month FREE forever'
    }
]

# Global nuclear SMTP instance
nuclear_smtp = NuclearSMTP()

def send_nuclear_email(to_email, subject, body, from_name="Newsletter", from_email=None):
    """Send email using nuclear SMTP rotation"""
    return nuclear_smtp.send_email(to_email, subject, body, from_name, from_email)

def get_nuclear_status():
    """Get nuclear SMTP status"""
    return nuclear_smtp.get_service_status()

def print_setup_instructions():
    """Print setup instructions for emergency SMTP services"""
    print("🔥 EMERGENCY SMTP SETUP INSTRUCTIONS:")
    print("="*50)
    
    for service in EMERGENCY_SMTP_SERVICES:
        print(f"\n📧 {service['name']}:")
        print(f"   URL: {service['setup_url']}")
        print(f"   Limit: {service['daily_limit']} emails/day")
        print(f"   Notes: {service.get('notes', 'Working service')}")
        print(f"   SMTP: {service['host']}:{service['port']}")
    
    total_daily = sum(s['daily_limit'] for s in EMERGENCY_SMTP_SERVICES)
    total_monthly = total_daily * 30
    
    print(f"\n🎯 TOTAL CAPACITY:")
    print(f"   Daily: {total_daily:,} emails")
    print(f"   Monthly: {total_monthly:,} emails")
    print(f"   Cost: $0 (all FREE tiers)")
    print(f"\n💀 F*CK THE EMAIL CARTEL - WE'RE GOING NUCLEAR!")