"""
Campaigns API - Handles campaign operations
"""
import os
import sqlite3
import smtplib
import threading
import time
import random
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, request, jsonify, g

# Create blueprint
campaigns_api = Blueprint('campaigns_api', __name__)

# Import database helper functions
from simple_db import query_db as simple_query_db, execute_db as simple_execute_db

# Override to use sender.db (same as lists)
def query_db(query, args=(), one=False):
    return simple_query_db(query, args, one, 'sender.db')

def execute_db(query, args=()):
    return simple_execute_db(query, args, 'sender.db')

# Campaigns routes
@campaigns_api.route('/campaigns', methods=['GET'])
def get_campaigns():
    try:
        campaigns = query_db('SELECT * FROM campaigns ORDER BY created_at DESC')
        result = []
        for campaign in campaigns:
            try:
                # Get list and SMTP details
                list_info = query_db('SELECT name FROM lists WHERE id = ?', [campaign['list_id']], one=True)
                smtp_info = query_db('SELECT name FROM smtp_servers WHERE id = ?', [campaign['smtp_id']], one=True)
            
                result.append({
                    'id': campaign['id'],
                    'name': campaign['name'],
                    'list_id': campaign['list_id'],
                    'list_name': list_info['name'] if list_info else 'Unknown',
                    'smtp_id': campaign['smtp_id'],
                    'smtp_name': smtp_info['name'] if smtp_info else 'Unknown',
                    'subject': campaign['subject'],
                    'body': campaign['body'],
                    'status': campaign['status'],
                    'sent_emails': campaign['sent_emails'] if 'sent_emails' in campaign.keys() else 0,
                    'total_emails': campaign['total_emails'] if 'total_emails' in campaign.keys() else 0,
                    'created_at': campaign['created_at']
                })
            except Exception as campaign_error:
                print(f"Error processing campaign {campaign['id'] if campaign['id'] else 'unknown'}: {campaign_error}")
                continue
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching campaigns: {str(e)}'}), 500

@campaigns_api.route('/campaigns', methods=['POST'])
def create_campaign():
    data = request.json
    name = data.get('name')
    list_id = data.get('list_id')
    smtp_id = data.get('smtp_id')
    subject = data.get('subject')
    body = data.get('body')
    from_name = data.get('from_name', '')
    from_email = data.get('from_email', '')
    reply_to = data.get('reply_to', '')
    priority = data.get('priority', 'normal')
    enable_ip_rotation = data.get('enable_ip_rotation', False)
    enable_auto_spin = data.get('enable_auto_spin', True)
    delivery_mode = data.get('delivery_mode', 'normal')
    
    if not name or not list_id or not smtp_id or not subject or not body:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    try:
        # Verify list and SMTP exist
        list_exists = query_db('SELECT id FROM lists WHERE id = ?', [list_id], one=True)
        smtp_exists = query_db('SELECT id FROM smtp_servers WHERE id = ?', [smtp_id], one=True)
        
        if not list_exists:
            return jsonify({'success': False, 'message': 'Selected list not found'}), 400
        if not smtp_exists:
            return jsonify({'success': False, 'message': 'Selected SMTP server not found'}), 400
        
        # Create campaign with all settings
        try:
            campaign_id = execute_db(
                '''INSERT INTO campaigns (name, list_id, smtp_id, subject, body, from_name, from_email, 
                   reply_to, priority, enable_ip_rotation, delivery_mode) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (name, list_id, smtp_id, subject, body, from_name, from_email, reply_to, 
                 priority, enable_ip_rotation, delivery_mode)
            )
        except Exception as db_error:
            print(f"Database error: {db_error}")
            return jsonify({'success': False, 'message': f'Database error: {str(db_error)}'}), 500
        
        return jsonify({
            'success': True,
            'data': {
                'id': campaign_id,
                'name': name,
                'list_id': list_id,
                'smtp_id': smtp_id,
                'subject': subject,
                'from_name': from_name,
                'from_email': from_email,
                'delivery_mode': delivery_mode,
                'status': 'draft'
            },
            'message': 'Campaign created successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating campaign: {str(e)}'}), 500

@campaigns_api.route('/campaigns/<int:campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    try:
        # Check if campaign exists
        campaign = query_db('SELECT * FROM campaigns WHERE id = ?', [campaign_id], one=True)
        if not campaign:
            return jsonify({'success': False, 'message': 'Campaign not found'}), 404
        
        # Delete campaign
        execute_db('DELETE FROM campaigns WHERE id = ?', [campaign_id])
        
        return jsonify({'success': True, 'message': 'Campaign deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting campaign: {str(e)}'}), 500

@campaigns_api.route('/campaigns/<int:campaign_id>/send', methods=['POST'])
def send_campaign(campaign_id):
    try:
        # Get campaign details
        campaign = query_db('SELECT * FROM campaigns WHERE id = ?', [campaign_id], one=True)
        if not campaign:
            return jsonify({'success': False, 'message': 'Campaign not found'}), 404
        
        # Get contacts count
        contacts = query_db('SELECT COUNT(*) as count FROM contacts WHERE list_id = ?', [campaign['list_id']], one=True)
        contact_count = contacts['count'] if contacts else 0
        
        if contact_count == 0:
            return jsonify({'success': False, 'message': 'No contacts found in selected list'}), 400
        
        # Update campaign status and total emails
        execute_db('UPDATE campaigns SET status = ?, total_emails = ? WHERE id = ?', ('sending', contact_count, campaign_id))
        
        # Start sending emails in background (simple implementation)
        try:
            send_campaign_emails(campaign_id)
        except Exception as send_error:
            print(f"Error starting email sending: {send_error}")
            execute_db('UPDATE campaigns SET status = ? WHERE id = ?', ('failed', campaign_id))
            return jsonify({'success': False, 'message': f'Error starting campaign: {str(send_error)}'}), 500
        
        return jsonify({
            'success': True, 
            'message': f'Campaign is being sent to {contact_count} contacts',
            'data': {
                'contact_count': contact_count,
                'status': 'sending'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error sending campaign: {str(e)}'}), 500

# Email sending function
def send_campaign_emails(campaign_id):
    """Send campaign emails in background thread"""
    def send_emails():
        try:
            print(f"Starting to send campaign {campaign_id}")
            # Get campaign details
            campaign = query_db('SELECT * FROM campaigns WHERE id = ?', [campaign_id], one=True)
            if not campaign:
                print(f"Campaign {campaign_id} not found")
                return
            print(f"Campaign found: {campaign['name']}")
            
            # Get SMTP server details
            print(f"Getting SMTP server {campaign['smtp_id']}")
            smtp_server = query_db('SELECT * FROM smtp_servers WHERE id = ?', [campaign['smtp_id']], one=True)
            if not smtp_server:
                print(f"SMTP server {campaign['smtp_id']} not found")
                execute_db('UPDATE campaigns SET status = ? WHERE id = ?', ('failed', campaign_id))
                return
            print(f"SMTP server found: {smtp_server['name']}")
            
            # Get contacts
            print(f"Getting contacts for list {campaign['list_id']}")
            contacts = query_db('SELECT * FROM contacts WHERE list_id = ?', [campaign['list_id']])
            if not contacts:
                print(f"No contacts found for list {campaign['list_id']}")
                execute_db('UPDATE campaigns SET status = ? WHERE id = ?', ('completed', campaign_id))
                return
            print(f"Found {len(contacts)} contacts")
            
            sent_count = 0
            
            for contact in contacts:
                try:
                    # Process message content (spinning and variables) FIRST
                    auto_spin_enabled = campaign['enable_auto_spin'] if 'enable_auto_spin' in campaign.keys() else True
                    body = process_message_content(campaign['body'], contact, auto_spin_enabled)
                    subject_processed = process_message_content(campaign['subject'], contact, auto_spin_enabled)
                    
                    # Create email
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject_processed
                    
                    # Set From with name and email (with random subdomain if enabled)
                    from_name = campaign['from_name'] or 'Sender'
                    base_email = campaign['from_email'] or smtp_server['from_email'] or smtp_server['username']
                    
                    # Random subdomains disabled - use base email
                    from_email = base_email
                        
                    msg['From'] = f"{from_name} <{from_email}>"
                    msg['To'] = contact['email']
                    
                    if campaign['reply_to']:
                        msg['Reply-To'] = campaign['reply_to']
                    
                    # Add professional headers for better inbox delivery
                    msg['Message-ID'] = f"<{int(time.time())}.{contact['id']}.{campaign_id}@{from_email.split('@')[1]}>"
                    msg['Date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
                    msg['X-Mailer'] = 'SenderBlade Professional Email System v1.0'
                    msg['Precedence'] = 'bulk'
                    msg['List-Unsubscribe'] = f'<mailto:unsubscribe@{from_email.split("@")[1]}>, <https://{from_email.split("@")[1]}/unsubscribe>'
                    msg['Return-Path'] = from_email
                    
                    # Priority headers
                    if campaign['priority'] == 'high':
                        msg['X-Priority'] = '2'
                        msg['Importance'] = 'High'
                    elif campaign['priority'] == 'urgent':
                        msg['X-Priority'] = '1'
                        msg['Importance'] = 'High'
                        msg['X-MSMail-Priority'] = 'High'
                    if '<' in body:
                        msg.attach(MIMEText(body, 'html'))
                    else:
                        msg.attach(MIMEText(body, 'plain'))
                    
                    # Send email
                    print(f"Sending email to {contact['email']}")
                    with smtplib.SMTP(smtp_server['host'], smtp_server['port']) as server:
                        if smtp_server['require_auth'] if 'require_auth' in smtp_server.keys() else True:
                            server.starttls()
                            server.login(smtp_server['username'], smtp_server['password'])
                        server.send_message(msg)
                    
                    sent_count += 1
                    print(f"Email sent successfully. Progress: {sent_count}/{len(contacts)}")
                    
                    # Log activity
                    log_activity(campaign_id, campaign['name'], 'email_sent', f'Email sent to {contact["email"]}', 'success')
                    
                    # Update progress
                    execute_db('UPDATE campaigns SET sent_emails = ? WHERE id = ?', (sent_count, campaign_id))
                    
                    # Small delay between emails
                    time.sleep(2)
                    
                except Exception as email_error:
                    print(f"Error sending email to {contact['email']}: {email_error}")
                    log_activity(campaign_id, campaign['name'], 'email_failed', f'Failed to send to {contact["email"]}: {str(email_error)}', 'error')
                    continue
            
            # Mark campaign as completed
            execute_db('UPDATE campaigns SET status = ?, sent_emails = ? WHERE id = ?', ('completed', sent_count, campaign_id))
            log_activity(campaign_id, campaign['name'], 'campaign_completed', f'Campaign completed. Sent {sent_count} emails', 'success')
            
        except Exception as e:
            print(f"Campaign sending error: {e}")
            execute_db('UPDATE campaigns SET status = ? WHERE id = ?', ('failed', campaign_id))
    
    # Start sending in background thread
    thread = threading.Thread(target=send_emails)
    thread.daemon = True
    thread.start()

# Dynamic auto-spinning system - automatically generates variations
def get_word_variations(word):
    """Generate variations for any word dynamically"""
    word_lower = word.lower()
    
    # Common word patterns and their variations
    variation_patterns = {
        # Greetings
        'hello': ['hello', 'hi', 'hey', 'greetings'],
        'hi': ['hi', 'hello', 'hey', 'greetings'],
        'hey': ['hey', 'hi', 'hello', 'greetings'],
        
        # Positive adjectives
        'good': ['good', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic'],
        'great': ['great', 'excellent', 'wonderful', 'fantastic', 'amazing', 'good'],
        'excellent': ['excellent', 'great', 'wonderful', 'fantastic', 'amazing'],
        'wonderful': ['wonderful', 'great', 'excellent', 'fantastic', 'amazing'],
        'amazing': ['amazing', 'incredible', 'outstanding', 'remarkable', 'fantastic'],
        'fantastic': ['fantastic', 'amazing', 'incredible', 'wonderful', 'great'],
        'perfect': ['perfect', 'ideal', 'excellent', 'flawless', 'outstanding'],
        'nice': ['nice', 'lovely', 'pleasant', 'wonderful', 'great'],
        'beautiful': ['beautiful', 'lovely', 'gorgeous', 'stunning', 'amazing'],
        'awesome': ['awesome', 'amazing', 'incredible', 'fantastic', 'outstanding'],
        
        # Time words
        'today': ['today', 'now', 'currently', 'at present'],
        'now': ['now', 'currently', 'at present', 'right now'],
        'day': ['day', 'time', 'moment', 'period'],
        'time': ['time', 'moment', 'period', 'day'],
        'morning': ['morning', 'day', 'time'],
        'evening': ['evening', 'night', 'time'],
        
        # Action words
        'try': ['try', 'attempt', 'work', 'strive', 'endeavor'],
        'work': ['work', 'try', 'attempt', 'strive', 'labor'],
        'start': ['start', 'begin', 'initiate', 'commence'],
        'started': ['started', 'begun', 'initiated', 'commenced'],
        'begin': ['begin', 'start', 'initiate', 'commence'],
        'give': ['give', 'offer', 'provide', 'deliver', 'present'],
        'get': ['get', 'obtain', 'receive', 'acquire', 'gain'],
        'make': ['make', 'create', 'build', 'produce', 'generate'],
        'help': ['help', 'assist', 'support', 'aid', 'guide'],
        
        # Frequency words
        'again': ['again', 'once more', 'another time', 'repeatedly'],
        'always': ['always', 'constantly', 'forever', 'perpetually'],
        'never': ['never', 'not ever', 'at no time', 'not once'],
        'often': ['often', 'frequently', 'regularly', 'commonly'],
        
        # Quantity words
        'many': ['many', 'numerous', 'several', 'various', 'multiple'],
        'much': ['much', 'a lot', 'plenty', 'abundant'],
        'more': ['more', 'additional', 'extra', 'further'],
        'most': ['most', 'majority', 'greatest', 'maximum'],
        'all': ['all', 'every', 'entire', 'complete'],
        'some': ['some', 'several', 'a few', 'certain'],
        
        # Relationship words
        'friend': ['friend', 'buddy', 'pal', 'companion'],
        'people': ['people', 'individuals', 'persons', 'folks'],
        'team': ['team', 'group', 'crew', 'staff'],
        'company': ['company', 'business', 'organization', 'firm'],
        
        # Emotion words
        'happy': ['happy', 'pleased', 'delighted', 'glad', 'joyful'],
        'excited': ['excited', 'thrilled', 'enthusiastic', 'eager'],
        'love': ['love', 'adore', 'cherish', 'treasure'],
        'like': ['like', 'enjoy', 'appreciate', 'favor'],
        
        # Importance words
        'important': ['important', 'crucial', 'essential', 'vital', 'significant'],
        'special': ['special', 'unique', 'exclusive', 'premium', 'distinctive'],
        'best': ['best', 'finest', 'top', 'premier', 'optimal'],
        'new': ['new', 'fresh', 'latest', 'recent', 'modern'],
        
        # Communication words
        'tell': ['tell', 'inform', 'notify', 'advise'],
        'show': ['show', 'display', 'demonstrate', 'reveal'],
        'share': ['share', 'distribute', 'spread', 'communicate'],
        'send': ['send', 'deliver', 'transmit', 'forward'],
        
        # Goals and aspirations
        'dreams': ['dreams', 'goals', 'aspirations', 'ambitions'],
        'goals': ['goals', 'objectives', 'targets', 'aims'],
        'success': ['success', 'achievement', 'accomplishment', 'victory'],
        'opportunity': ['opportunity', 'chance', 'possibility', 'opening']
    }
    
    return variation_patterns.get(word_lower, [word])  # Return original if no variations found

# Message processing function
def process_message_content(content, contact, auto_spin=True):
    """Process message content with auto-spinning and variable replacement"""
    if not content:
        return content
    
    processed = content
    
    # First: Process manual spinning syntax {option1|option2|option3}
    def replace_spinning(match):
        options = match.group(1).split('|')
        return random.choice(options).strip()
    
    processed = re.sub(r'\{([^{}]*\|[^{}]*)\}', replace_spinning, processed)
    
    # Second: Auto-spin common words if enabled (50% of words)
    if auto_spin:
        words = processed.split()
        for i, word in enumerate(words):
            # Only spin 50% of spinnable words randomly
            if random.random() < 0.5:
                # Clean word (remove punctuation for matching)
                clean_word = re.sub(r'[^a-zA-Z]', '', word)
                variations = get_word_variations(clean_word)
                
                # Only spin if we have variations (more than just the original word)
                if len(variations) > 1:
                    # Keep original punctuation and case
                    replacement = random.choice(variations)
                    if word and word[0].isupper():
                        replacement = replacement.capitalize()
                    # Preserve punctuation
                    punctuation = re.sub(r'[a-zA-Z]', '', word)
                    words[i] = replacement + punctuation
        processed = ' '.join(words)
    
    # Third: Replace contact variables
    processed = processed.replace('{email}', contact['email'] if contact['email'] else '')
    processed = processed.replace('{first_name}', contact['first_name'] if contact['first_name'] else '')
    processed = processed.replace('{last_name}', contact['last_name'] if contact['last_name'] else '')
    
    return processed

# Generate random subdomain email for better deliverability
def generate_random_subdomain_email(base_email):
    """Generate random subdomain for legitimate email delivery improvement"""
    if '@' not in base_email:
        return base_email
    
    username, domain = base_email.split('@', 1)
    
    # Extended random subdomain prefixes (up to 10 characters)
    subdomains = [
        'mail', 'news', 'info', 'updates', 'alerts', 'notify', 'team', 'support',
        'newsletter', 'marketing', 'campaigns', 'broadcast', 'messaging', 'delivery',
        'outreach', 'connect', 'engage', 'communicate', 'distribute', 'dispatch',
        'transmit', 'forward', 'relay', 'channel', 'network', 'platform', 'service',
        'system', 'portal', 'gateway', 'bridge', 'link', 'hub', 'center', 'office',
        'desk', 'unit', 'dept', 'division', 'branch', 'sector', 'zone', 'region'
    ]
    
    # Generate random alphanumeric subdomain (3-10 characters)
    import string
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(3, 10)))
    
    # Mix of predefined and random subdomains
    if random.choice([True, False]):
        random_subdomain = random.choice(subdomains)
    else:
        random_subdomain = random_chars
    
    # Create subdomain email
    subdomain_email = f"{username}@{random_subdomain}.{domain}"
    
    return subdomain_email

# Activity logging function
def log_activity(campaign_id, campaign_name, action, details, status):
    """Log campaign activity"""
    try:
        execute_db(
            'INSERT INTO activity_logs (campaign_id, campaign_name, action, details, status, timestamp) VALUES (?, ?, ?, ?, ?, datetime("now"))',
            (campaign_id, campaign_name, action, details, status)
        )
    except Exception as e:
        print(f"Error logging activity: {e}")

@campaigns_api.route('/activity', methods=['GET'])
def get_activity_logs():
    """Get activity logs"""
    try:
        logs = query_db('SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 100')
        result = []
        for log in logs:
            result.append({
                'id': log['id'],
                'campaign_id': log['campaign_id'],
                'campaign_name': log['campaign_name'],
                'action': log['action'],
                'details': log['details'],
                'status': log['status'],
                'timestamp': log['timestamp']
            })
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching activity logs: {str(e)}'}), 500

# Health endpoint moved to health_api.py to avoid conflicts