"""
Smart Notification System for SenderBlade
Sends notifications without breaking existing code
"""
import smtplib
from email.mime.text import MIMEText

class NotificationSystem:
    """Handle all email notifications safely"""
    
    def __init__(self):
        # Use working Gmail credentials
        self.smtp_config = {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'timothykeeton.tk@gmail.com',
            'password': 'akda bgpw becv kbso'
        }
        self.admin_email = 'emmanueldickerson757@icloud.com'
    
    def send_email(self, to_email, subject, body):
        """Send email safely with error handling"""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.smtp_config['username']
            msg['To'] = to_email
            
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            print(f"✅ Notification sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"⚠️ Notification failed to {to_email}: {e}")
            return False
    
    def notify_admin_new_user(self, username, email):
        """Notify admin of new user registration"""
        subject = "🔔 SenderBlade - New User Awaiting Approval"
        body = f"""
Hello Admin,

A new user has registered and is awaiting your approval:

👤 Username: {username}
📧 Email: {email}
⏰ Registration Time: Just now

Please review and approve this user in the admin panel:
🔗 Admin Panel: http://localhost:5001/admin/users

Best regards,
SenderBlade System
        """
        
        return self.send_email(self.admin_email, subject, body)
    
    def notify_user_pending_approval(self, username, email):
        """Notify user their account is pending approval"""
        subject = "⏳ SenderBlade - Account Pending Approval"
        body = f"""
Hello {username},

Thank you for registering with SenderBlade!

Your account has been successfully created and is currently pending admin approval.

📧 Your Email: {email}
⏳ Status: Pending Approval
🔔 Next Step: Wait for admin approval

You will receive another email once your account is approved and ready to use.

If you have any questions, please contact our support team.

Best regards,
SenderBlade Team
        """
        
        return self.send_email(email, subject, body)
    
    def notify_user_approved(self, username, email):
        """Notify user their account has been approved"""
        subject = "🎉 SenderBlade - Account Approved!"
        body = f"""
Hello {username},

Great news! Your SenderBlade account has been approved and is now active.

👤 Username: {username}
📧 Email: {email}
✅ Status: Approved & Active
🚀 Ready to Use: Yes

You can now log in and start using SenderBlade:
🔗 Login: http://localhost:5001/

Welcome to SenderBlade! We're excited to have you on board.

Best regards,
SenderBlade Team
        """
        
        return self.send_email(email, subject, body)
    
    def notify_user_blocked(self, username, email, reason):
        """Notify user their account has been blocked"""
        subject = "🚫 SenderBlade - Account Status Update"
        body = f"""
Hello {username},

We're writing to inform you about a change to your SenderBlade account status.

👤 Username: {username}
📧 Email: {email}
🚫 Status: Account Blocked
📝 Reason: {reason}

If you believe this is an error or would like to appeal this decision, please contact our support team.

Best regards,
SenderBlade Team
        """
        
        return self.send_email(email, subject, body)

# Global notification instance
notification_system = NotificationSystem()