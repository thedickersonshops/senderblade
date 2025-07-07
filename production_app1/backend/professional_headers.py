"""
Professional Email Headers - Anti-Spam Optimization
"""
import random
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ProfessionalHeaders:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
        self.message_ids_domains = [
            'outlook.com', 'gmail.com', 'yahoo.com', 'hotmail.com'
        ]
    
    def generate_message_id(self, sender_domain=None):
        """Generate professional Message-ID"""
        timestamp = str(int(time.time()))
        random_part = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))
        domain = sender_domain or random.choice(self.message_ids_domains)
        return f"<{timestamp}.{random_part}@{domain}>"
    
    def add_professional_headers(self, msg, sender_email, recipient_email, subject):
        """Add professional anti-spam headers"""
        
        # Essential headers for deliverability
        msg['Message-ID'] = self.generate_message_id()
        msg['Date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z', time.gmtime())
        
        # Anti-spam headers
        msg['X-Mailer'] = random.choice([
            'Microsoft Outlook 16.0',
            'Apple Mail (2.3445.104.11)',
            'Thunderbird 91.0'
        ])
        
        msg['X-Priority'] = '3'
        msg['X-MSMail-Priority'] = 'Normal'
        msg['Importance'] = 'Normal'
        
        # Authentication headers (simulated)
        msg['Authentication-Results'] = f'mx.google.com; spf=pass smtp.mailfrom={sender_email}'
        msg['Received-SPF'] = f'pass (google.com: domain of {sender_email} designates sender IP as permitted sender)'
        
        # Content headers
        msg['MIME-Version'] = '1.0'
        msg['Content-Language'] = 'en-US'
        
        # List management headers (for bulk emails)
        if '@' in sender_email:
            domain = sender_email.split('@')[1]
            msg['List-Unsubscribe'] = f'<mailto:unsubscribe@{domain}>'
            msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
        
        return msg
    
    def create_professional_message(self, sender_email, sender_name, recipient_email, 
                                  subject, plain_content, html_content=None):
        """Create professionally formatted email message"""
        
        if html_content:
            msg = MIMEMultipart('alternative')
            
            # Plain text part
            plain_part = MIMEText(plain_content, 'plain', 'utf-8')
            msg.attach(plain_part)
            
            # HTML part
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
        else:
            msg = MIMEText(plain_content, 'plain', 'utf-8')
        
        # Set basic headers
        msg['Subject'] = subject
        msg['From'] = f"{sender_name} <{sender_email}>" if sender_name else sender_email
        msg['To'] = recipient_email
        
        # Add professional headers
        msg = self.add_professional_headers(msg, sender_email, recipient_email, subject)
        
        return msg
    
    def optimize_subject_line(self, subject):
        """Optimize subject line for deliverability"""
        # Remove spam trigger words and optimize
        spam_words = ['FREE', 'URGENT', '!!!', 'CLICK HERE', 'LIMITED TIME']
        
        optimized = subject
        for word in spam_words:
            if word in optimized.upper():
                optimized = optimized.replace(word, word.lower().capitalize())
        
        # Ensure reasonable length
        if len(optimized) > 50:
            optimized = optimized[:47] + '...'
        
        return optimized

# Global headers instance
professional_headers = ProfessionalHeaders()