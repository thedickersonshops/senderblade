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
    use_random_email = data.get('use_random_email', True)  # Default ON
    random_mode = data.get('random_mode', 'username_only')
    
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
        
        # Create campaign with all settings (add columns if they don't exist)
        try:
            # Try with new columns first
            try:
                campaign_id = execute_db(
                    '''INSERT INTO campaigns (name, list_id, smtp_id, subject, body, from_name, from_email, 
                       reply_to, priority, enable_ip_rotation, delivery_mode, use_random_email, random_mode) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (name, list_id, smtp_id, subject, body, from_name, from_email, reply_to, 
                     priority, enable_ip_rotation, delivery_mode, use_random_email, random_mode)
                )
            except Exception as col_error:
                # Fallback to old columns if new ones don't exist
                print(f"Using fallback campaign creation: {col_error}")
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
            # Get campaign details with enhanced error checking
            print(f"Starting campaign {campaign_id}")
            campaign = query_db('SELECT * FROM campaigns WHERE id = ?', [campaign_id], one=True)
            if not campaign:
                print(f"ERROR: Campaign {campaign_id} not found in database")
                execute_db('UPDATE campaigns SET status = ? WHERE id = ?', ('failed', campaign_id))
                return
            
            # Convert sqlite3.Row to dict to avoid attribute errors
            campaign = dict(campaign)
            print(f"Campaign found: {campaign['name']}")
            
            # Get SMTP server details with validation
            smtp_id = campaign.get('smtp_id')
            print(f"Getting SMTP server {smtp_id}")
            if not smtp_id:
                print(f"ERROR: No SMTP server ID in campaign")
                execute_db('UPDATE campaigns SET status = ? WHERE id = ?', ('failed', campaign_id))
                return
                
            smtp_server = query_db('SELECT * FROM smtp_servers WHERE id = ?', [smtp_id], one=True)
            if not smtp_server:
                print(f"ERROR: SMTP server {smtp_id} not found in database")
                execute_db('UPDATE campaigns SET status = ? WHERE id = ?', ('failed', campaign_id))
                return
            
            # Convert sqlite3.Row to dict to avoid attribute errors
            smtp_server = dict(smtp_server)
            print(f"SMTP server found: {smtp_server['name']}")
            
            # Get contacts with validation
            list_id = campaign.get('list_id')
            print(f"Getting contacts for list {list_id}")
            if not list_id:
                print(f"ERROR: No list ID in campaign")
                execute_db('UPDATE campaigns SET status = ? WHERE id = ?', ('failed', campaign_id))
                return
                
            contacts = query_db('SELECT * FROM contacts WHERE list_id = ?', [list_id])
            if not contacts:
                print(f"ERROR: No contacts found for list {list_id}")
                log_activity(campaign_id, campaign['name'], 'campaign_failed', f'No contacts in list {list_id}', 'error')
                execute_db('UPDATE campaigns SET status = ? WHERE id = ?', ('failed', campaign_id))
                return
            
            # Convert all contacts to dict to avoid sqlite3.Row errors
            contacts = [dict(contact) for contact in contacts]
            print(f"Found {len(contacts)} contacts")
            
            sent_count = 0
            campaign_name = campaign.get('name', 'Unknown Campaign')
            
            print(f"Starting to send {len(contacts)} emails for campaign '{campaign_name}'")
            log_activity(campaign_id, campaign_name, 'campaign_started', f'Starting to send {len(contacts)} emails', 'info')
            
            for i, contact in enumerate(contacts, 1):
                print(f"Processing contact {i}/{len(contacts)}: {contact.get('email', 'unknown')}")
                try:
                    # Validate contact data
                    if not contact or not contact.get('email'):
                        print(f"ERROR: Invalid contact data: {contact}")
                        continue
                        
                    contact_email = contact['email']
                    print(f"Processing email for: {contact_email}")
                    
                    # DEFINE ALL VARIABLES FIRST - CRITICAL FOR SCOPE
                    recipient_domain = contact['email'].split('@')[1].lower() if '@' in contact['email'] else 'unknown.com'
                    is_hotmail = recipient_domain in ['hotmail.com', 'outlook.com', 'live.com', 'msn.com']
                    is_gmail = recipient_domain in ['gmail.com', 'googlemail.com']
                    is_yahoo = recipient_domain in ['yahoo.com', 'yahoo.co.uk', 'ymail.com']
                    delivery_mode = campaign.get('delivery_mode', 'normal')
                    
                    print(f"PROCESSING EMAIL: {contact['email']} | DOMAIN: {recipient_domain}")
                    print(f"DELIVERY MODE: {delivery_mode} for {contact['email']}")
                    
                    # Process message content (spinning and variables)
                    auto_spin_enabled = campaign.get('enable_auto_spin', True)
                    campaign_body = campaign.get('body', '')
                    campaign_subject = campaign.get('subject', '')
                    
                    if not campaign_body or not campaign_subject:
                        print(f"ERROR: Missing campaign body or subject")
                        continue
                        
                    # COMPREHENSIVE DEBUGGING - TRACK LINE BREAK PRESERVATION
                    print("\n=== MESSAGE PROCESSING DEBUG ===")
                    newline_char = '\n'
                    print(f"Original body line count: {len(campaign_body.split(newline_char))}")
                    print(f"Original body contains '---': {'---' in campaign_body}")
                    print(f"Auto-spin enabled: {auto_spin_enabled}")
                    
                    body = process_message_content(campaign_body, contact, auto_spin_enabled)
                    subject_processed = process_message_content(campaign_subject, contact, auto_spin_enabled)
                    
                    print(f"Processed body line count: {len(body.split(newline_char))}")
                    print(f"Processed body contains '---': {'---' in body}")
                    print(f"First 100 chars of processed body: {body[:100]}...")
                    print("=== END DEBUG ===\n")
                    
                    # Create email
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject_processed
                    
                    # ULTRA-AGGRESSIVE SENDER NAME ENFORCEMENT
                    from_name = campaign.get('from_name', '').strip()
                    if not from_name:
                        from_name = 'Customer Service'  # Professional default
                    
                    # Clean and validate sender name
                    from_name = from_name.replace('"', '').replace('<', '').replace('>', '').replace('\n', '').replace('\r', '')
                    from_name = from_name[:50]  # Limit length
                    print(f"ULTRA-ENFORCING SENDER NAME: '{from_name}'")
                    
                    # EMAIL SENDER LOGIC WITH TOGGLE
                    use_random_email = campaign.get('use_random_email', True)  # Default ON
                    
                    # ZOHO SMTP DETECTION - Zoho only allows exact login email
                    smtp_host = smtp_server.get('host', '').lower()
                    is_zoho_smtp = 'zoho.com' in smtp_host
                    
                    if is_zoho_smtp:
                        # ZOHO RESTRICTION: Must use exact login email
                        from_email = smtp_server.get('username', 'sender@example.com')
                        print(f"ZOHO SMTP DETECTED: Using exact login email {from_email} (Zoho restriction)")
                    elif use_random_email:
                        # Random email mode (for compatible SMTP servers)
                        random_mode = campaign.get('random_mode', 'username_only')
                        # Use SMTP server's domain to avoid relay restrictions
                        smtp_username = smtp_server.get('username', '')
                        if '@' in smtp_username:
                            verified_domain = smtp_username.split('@')[1]
                            print(f"USING SMTP DOMAIN: {verified_domain} (to avoid relay restrictions)")
                        else:
                            verified_domain = 'fayehallcookies.online'  # fallback
                        
                        if random_mode == 'username_only':
                            from_email = generate_random_email_option1(verified_domain)
                        elif random_mode == 'username_subdomain':
                            from_email = generate_random_email_option2(verified_domain)
                        elif random_mode == 'subdomain_only':
                            from_email = generate_random_email_option3(verified_domain)
                        else:
                            from_email = generate_random_email_option1(verified_domain)
                        
                        print(f"RANDOM EMAIL MODE: {random_mode}, Email: {from_email}")
                    else:
                        # NORMAL MODE: Use SMTP server's actual email (most reliable)
                        campaign_from_email = campaign.get('from_email', '').strip()
                        smtp_username = smtp_server.get('username', '').strip()
                        
                        if campaign_from_email:
                            from_email = campaign_from_email
                        elif smtp_username:
                            from_email = smtp_username
                        else:
                            from_email = 'sender@example.com'
                            
                        print(f"NORMAL EMAIL MODE: Using {from_email} (Random email disabled)")
                    # Ensure from_email is properly formatted
                    if '@' not in from_email:
                        print(f"WARNING: Invalid from_email '{from_email}', fixing...")
                        from_email = f"sender@{from_email}" if '.' in from_email else f"sender@{from_email}.com"
                        print(f"Fixed from_email: {from_email}")
                    
                    # ULTRA-AGGRESSIVE FROM HEADER ENFORCEMENT
                    from_header = f'"{from_name}" <{from_email}>'
                    msg['From'] = from_header
                    msg['To'] = contact['email']
                    
                    # FORCE SENDER NAME RECOGNITION - MULTIPLE HEADERS
                    msg['Sender'] = from_header
                    msg['Reply-To'] = f'"{from_name}" <{from_email}>'
                    msg['Return-Path'] = from_email
                    msg['Envelope-From'] = from_email
                    
                    # ADDITIONAL SENDER ENFORCEMENT HEADERS
                    msg['X-Sender'] = from_header
                    msg['X-Original-Sender'] = from_email
                    msg['X-Envelope-From'] = from_email
                    
                    print(f"ULTRA-AGGRESSIVE FROM HEADER: {from_header}")
                    
                    if campaign.get('reply_to'):
                        msg['Reply-To'] = campaign['reply_to']
                    
                    # Add professional headers with safe domain extraction
                    try:
                        domain_part = from_email.split('@')[1] if '@' in from_email else 'example.com'
                    except (IndexError, AttributeError):
                        domain_part = 'example.com'
                    
                    msg['Message-ID'] = f"<{int(time.time())}.{contact.get('id', 0)}.{campaign_id}@{domain_part}>"
                    msg['Date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')
                    msg['X-Mailer'] = 'SenderBlade Professional Email System v1.0'
                    msg['Precedence'] = 'bulk'
                    msg['List-Unsubscribe'] = f'<mailto:unsubscribe@{domain_part}>, <https://{domain_part}/unsubscribe>'
                    msg['Return-Path'] = from_email
                    
                    # OUTLOOK-OPTIMIZED INBOX DELIVERY HEADERS
                    msg['MIME-Version'] = '1.0'
                    msg['Content-Type'] = 'text/plain; charset=utf-8'
                    if is_hotmail:
                        msg['Content-Transfer-Encoding'] = 'quoted-printable'  # Better for Outlook
                    else:
                        msg['Content-Transfer-Encoding'] = '8bit'  # Standard for others
                    
                    # SIMPLE ANTI-SPAM HEADERS
                    msg['X-Spam-Status'] = 'No'
                    msg['X-Spam-Score'] = '-2.6'
                    msg['X-Spam-Flag'] = 'NO'
                    
                    # BASIC AUTHENTICATION HEADERS
                    sender_domain = from_email.split('@')[1] if '@' in from_email else 'example.com'
                    msg['Received-SPF'] = f'pass (domain of {from_email} designates sending IP as permitted sender)'
                    
                    # SIMPLE MICROSOFT HEADERS
                    if is_hotmail:
                        msg['X-MS-Exchange-Organization-SCL'] = '-1'
                        msg['X-MS-Has-Attach'] = 'no'
                    
                    # SIMPLE GMAIL HEADERS
                    if is_gmail:
                        msg['X-Google-DKIM-Signature'] = f'v=1; a=rsa-sha256; c=relaxed/relaxed; d=1e100.net'
                        msg['X-Gm-Message-State'] = f'AOJu0Y{random.randint(10000,99999)}'
                    
                    # SIMPLE ZOHO HEADERS
                    if 'zoho.com' in recipient_domain.lower():
                        msg['X-ZohoMail-DKIM'] = 'pass'
                        msg['X-Zoho-Spam-Status'] = 'No'
                    
                    # BASIC BUSINESS HEADERS
                    msg['X-Mailer'] = 'Microsoft Outlook 16.0'
                    msg['X-Auto-Response-Suppress'] = 'OOF, DR, RN, NRN'
                    
                    # Priority headers
                    priority = campaign.get('priority', 'normal')
                    if priority == 'high':
                        msg['X-Priority'] = '2'
                        msg['Importance'] = 'High'
                    elif priority == 'urgent':
                        msg['X-Priority'] = '1'
                        msg['Importance'] = 'High'
                        msg['X-MSMail-Priority'] = 'High'
                    
                    # DELIVERY MODE OPTIMIZATION
                    if delivery_mode == 'stealth':
                        # MICROSOFT EXCHANGE SIMULATION (HOTMAIL/OUTLOOK INBOX)
                        msg['X-Originating-Email'] = f'[{from_email}]'
                        msg['X-MS-Exchange-Organization-MessageDirectionality'] = 'Originating'
                        msg['X-MS-Exchange-Organization-SCL'] = '-1'  # Trusted sender
                        msg['X-MS-Exchange-Organization-PCL'] = '2'   # Low phishing confidence
                        msg['X-MS-Exchange-Organization-AuthSource'] = domain_part
                        msg['X-MS-Exchange-Organization-AuthAs'] = 'Internal'
                        msg['X-MS-Has-Attach'] = 'no'
                        
                        # GMAIL INBOX OPTIMIZATION
                        msg['X-Google-DKIM-Signature'] = f'v=1; a=rsa-sha256; c=relaxed/relaxed; d=1e100.net; s=20230601; h=to:from:subject:date:message-id:mime-version; bh=fake_body_hash_for_gmail; b=fake_google_signature_for_inbox_delivery'
                        msg['X-Gm-Message-State'] = f'AOJu0Y{random.randint(10000, 99999)}FakeGmailStateForInboxDelivery'
                        msg['X-Google-Smtp-Source'] = f'APBJJlH{random.randint(10000, 99999)}FakeSmtpSourceForTrustedDelivery'
                        
                        # YAHOO INBOX HEADERS
                        msg['X-YMail-OSG'] = f'fake_yahoo_osg_{random.randint(1000, 9999)}'
                        msg['X-Rocket-Received'] = f'from mail-{random.randint(100, 999)}.yahoo.com'
                        
                        # UNIVERSAL INBOX DELIVERY HEADERS
                        msg['X-Spam-Status'] = 'No, score=-5.2 required=5.0 tests=BAYES_00,DKIM_SIGNED,DKIM_VALID,DKIM_VALID_AU,RCVD_IN_DNSWL_HI,SPF_PASS autolearn=ham version=3.4.6'
                        msg['X-Spam-Score'] = '-5.2'
                        msg['X-Spam-Level'] = ''
                        msg['X-Spam-Flag'] = 'NO'
                        
                        # TRUSTED SENDER INDICATORS
                        msg['X-Authenticated-Sender'] = from_email
                        msg['X-Sender-Verified'] = 'TRUE'
                        msg['X-Source-IP'] = '192.168.1.100'  # Internal IP simulation
                        msg['X-Source-Dir'] = 'OUT'
                        
                        # BUSINESS EMAIL INDICATORS
                        msg['X-Business-Email'] = 'TRUE'
                        msg['X-Bulk-Mail'] = 'FALSE'
                        msg['X-Commercial'] = 'FALSE'
                        msg['X-Newsletter'] = 'FALSE'
                        
                        # ENHANCED REPUTATION BOOST HEADERS
                        msg['X-SenderScore'] = 'None'
                        msg['X-IronPort-AV'] = f'E=Sophos;i="6.00,199,{int(time.time())}"; d="scan\'208";a="fake_ironport_scan"'
                        msg['X-Barracuda-Connect'] = 'UNKNOWN'
                        msg['X-Barracuda-Start-Time'] = str(int(time.time()))
                        msg['X-Virus-Scanned'] = f'Debian amavisd-new at {domain_part}'
                        
                        # Additional trust indicators
                        msg['X-Sender-Verified'] = 'PASS'
                        msg['X-Email-Type-Id'] = 'PERSONAL'
                        msg['X-Mailer-LID'] = f'personal-{random.randint(1000, 9999)}'
                        msg['X-Priority'] = '3 (Normal)'
                        msg['Importance'] = 'Normal'
                        
                        # FOREFRONT ENHANCED BYPASS (HOTMAIL/OUTLOOK)
                        msg['X-Forefront-Antispam-Report'] = f'CIP:192.168.1.100;CTRY:US;LANG:en;SCL:-1;SRV:;IPV:NLI;SFV:NSPM;H:{domain_part};PTR:{domain_part};CAT:NONE;SFTY:9.99;SFS:(13230022)(4636009)(376002)(39860400002)(346002)(396003)(136003)(366004)(26005)(6916009)(86362001)(478600001)(5660300002)(8676002)(6486002)(2906002)(186003)(8936002)(6506007)(6512007)(316002)(66946007)(66556008)(66476007)(52536014)(36756003)(7696005)(9686003)(1076003)(956004)(6916009);DIR:INB;SFTY:9.99;'
                        msg['X-Microsoft-Antispam'] = 'BCL:0;PCL:0;RULEID:(7020095)(4652040)(5600026)(4534165)(4627221)(201703031133081)(201702281549075)(8989299)(4534169)(4627267)(4627236)(201703061421075)(201703061406153)(201703061421075)(201703061406153);SRVR:mail.fayehallcookies.online;'
                        msg['X-Microsoft-Antispam-Mailbox-Delivery'] = 'ucf:0;jmr:0;auth:0;dest:I;ENG:(750119)(520011016)(706158)(944506458)(944626604)(944625604);'
                        msg['X-Microsoft-Antispam-Message-Info'] = f'fake_message_info_for_inbox_delivery_{random.randint(10000, 99999)}'
                    # BULLETPROOF SIGNATURE FORMATTER - GUARANTEED DETECTION
                    def format_signature_universal(content, is_html=False):
                        """Bulletproof signature formatter - NEVER loses the separator"""
                        print("\n=== SIGNATURE FORMATTER DEBUG ===")
                        print(f"Content length: {len(content)}")
                        newline_char = '\n'
                        print(f"Line count: {len(content.split(newline_char))}")
                        print(f"Contains '---': {'---' in content}")
                        print(f"First 200 chars: {content[:200]}...")
                        
                        # BULLETPROOF SEPARATOR DETECTION
                        separator_found = False
                        main_content = content
                        signature_content = ""
                        
                        # Try multiple separator patterns
                        separators = ['---', '-- ', '--', '___', '***']
                        for sep in separators:
                            if sep in content:
                                parts = content.split(sep, 1)
                                if len(parts) == 2:
                                    main_content = parts[0].strip()
                                    signature_content = parts[1].strip()
                                    separator_found = True
                                    print(f"Found separator '{sep}'")
                                    print(f"Main content lines: {len(main_content.split(newline_char))}")
                                    print(f"Signature content lines: {len(signature_content.split(newline_char))}")
                                    print("=== END SIGNATURE DEBUG ===\n")
                                    break
                        
                        if not separator_found:
                            print(f"No separator found, treating as plain content")
                            print("=== END SIGNATURE DEBUG ===\n")
                            if is_html:
                                return content.replace('\n', '<br>\n')
                            return content
                        
                        if is_html:
                            # PERFECT HTML FORMATTING - GUARANTEED LINE BREAKS
                            main_formatted = main_content.replace('\n', '<br>\n')
                            
                            # Process each signature line individually with FORCED breaks
                            sig_lines = [line.strip() for line in signature_content.split('\n') if line.strip()]
                            sig_html = '<br>\n'.join(sig_lines)
                            
                            # Professional HTML signature with VISIBLE separator
                            return f'''{main_formatted}<br><br>
<div style="border-top: 2px solid #333; margin: 20px 0; padding-top: 15px; font-family: Arial, sans-serif;">
<div style="font-size: 14px; line-height: 1.8; color: #333;">
{sig_html}
</div>
</div>'''
                        else:
                            # Plain text with FORCED separator preservation
                            main_formatted = main_content.replace('\n', '\r\n')
                            sig_lines = [line.strip() for line in signature_content.split('\n') if line.strip()]
                            sig_formatted = '\r\n\r\n'.join(sig_lines)  # Double breaks for visibility
                            crlf = '\r\n'
                            return f"{main_formatted}{crlf}{crlf}-- {crlf}{crlf}{sig_formatted}"
                    
                    # NUCLEAR SIGNATURE SOLUTION - MULTIPART ALTERNATIVE
                    if '<' in body or 'max-width: 600px' in body:
                        # HTML content - keep as is
                        formatted_body = format_signature_universal(body, True)
                        html_part = MIMEText(formatted_body, 'html', 'utf-8')
                        msg.attach(html_part)
                    else:
                        # REVOLUTIONARY APPROACH: Send BOTH plain text AND HTML versions
                        # This forces email clients to use the HTML version for proper formatting
                        
                        # Plain text version (fallback)
                        plain_formatted = format_signature_universal(body, False)
                        text_part = MIMEText(plain_formatted, 'plain', 'utf-8')
                        msg.attach(text_part)
                        
                        # HTML version with perfect signature formatting
                        html_formatted = format_signature_universal(body, True)
                        html_part = MIMEText(html_formatted, 'html', 'utf-8')
                        msg.attach(html_part)
                        
                        # Change message type to multipart/alternative
                        msg.set_type('multipart/alternative')
                    
                    # Get formatted body for logging
                    try:
                        if '<' in body or 'max-width: 600px' in body:
                            log_body = format_signature_universal(body, True)
                        else:
                            log_body = format_signature_universal(body, False)
                        print(f"SIGNATURE FORMATTED: {len(log_body.split('---')[1].split() if '---' in log_body else [])} signature elements")
                    except:
                        print(f"SIGNATURE FORMATTED: Processing complete")
                    print(f"Final message line count: {len(body.split(newline_char))}")
                    
                    # FINAL ULTRA-AGGRESSIVE SENDER NAME ENFORCEMENT
                    final_from_header = f'"{from_name}" <{from_email}>'
                    msg.replace_header('From', final_from_header)
                    
                    # FORCE SENDER NAME IN MULTIPLE PLACES
                    if 'Sender' in msg:
                        msg.replace_header('Sender', final_from_header)
                    if 'Reply-To' in msg:
                        msg.replace_header('Reply-To', final_from_header)
                    
                    # ADDITIONAL SENDER NAME ENFORCEMENT
                    msg['X-Sender-Name'] = from_name
                    msg['X-Display-Name'] = from_name
                    msg['X-From-Name'] = from_name
                    
                    print(f"FINAL ULTRA-ENFORCED FROM: {msg['From']}")
                    print(f"SENDER NAME ENFORCED: '{from_name}' in {len([h for h in msg.keys() if 'sender' in h.lower() or 'from' in h.lower()])} headers")
                    print(f"SIGNATURE OPTIMIZATION: {'HTML table format' if '<' in body else 'Plain text format'} for {contact['email'].split('@')[1] if '@' in contact['email'] else 'unknown'}")
                    print(f"EMAIL READY TO SEND: {contact['email']} via {smtp_server['host']}")
                    
                    # VARIABLES ALREADY DEFINED AT TOP OF LOOP
                    
                    # DELIVERY OPTIMIZATION (using variables defined above)
                    print(f"DELIVERY OPTIMIZATION for {recipient_domain} | Hotmail: {is_hotmail} | Gmail: {is_gmail}")
                    
                    # ENHANCED HOTMAIL/OUTLOOK INBOX OPTIMIZATION  
                    if is_hotmail:
                        # Microsoft Exchange simulation for inbox delivery
                        msg['X-MS-Exchange-Organization-Network-Message-Id'] = f'fake-network-id-{int(time.time())}-{random.randint(1000, 9999)}'
                        msg['X-MS-Exchange-Organization-MessageDirectionality'] = 'Originating'
                        msg['X-MS-Exchange-Organization-AuthSource'] = domain_part
                        msg['X-MS-Exchange-Organization-AuthAs'] = 'Internal'
                        msg['X-MS-Exchange-Organization-AuthMechanism'] = '04'
                        msg['X-MS-Exchange-Organization-SCL'] = '-1'  # Trusted sender
                        msg['X-MS-Exchange-Organization-PCL'] = '2'   # Low phishing confidence
                        msg['X-MS-Exchange-Organization-Antispam-Report'] = f'BCL:0;PCL:0;RULEID:;SRVR:{domain_part};'
                        
                        # Additional Outlook-specific headers for inbox delivery
                        msg['X-MS-Exchange-CrossTenant-Network-Message-Id'] = f'cross-tenant-{int(time.time())}-{random.randint(1000, 9999)}'
                        msg['X-MS-Exchange-CrossTenant-AuthSource'] = domain_part
                        msg['X-MS-Exchange-CrossTenant-AuthAs'] = 'Internal'
                        msg['X-MS-Exchange-Transport-CrossTenantHeadersStamped'] = domain_part
                        
                        # Outlook reputation boost
                        msg['X-MS-Exchange-Organization-ExpirationStartTime'] = time.strftime('%d %b %Y %H:%M:%S %z')
                        msg['X-MS-Exchange-Organization-ExpirationInterval'] = '1:00:00:00.0000000'
                        
                        print(f"ENHANCED HOTMAIL OPTIMIZATION for {contact['email']}")
                    
                    # ICLOUD SPECIFIC OPTIMIZATION
                    elif recipient_domain == 'icloud.com' and delivery_mode == 'stealth':
                        # Apple iCloud inbox optimization
                        msg['X-Apple-Mail-Remote-Attachments'] = 'NO'
                        msg['X-Apple-Base-URL'] = f'https://{domain_part}'
                        msg['X-Universally-Unique-Identifier'] = f'apple-{int(time.time())}-{random.randint(10000, 99999)}'
                        msg['X-Apple-Mail-Signature'] = 'TRUE'
                        
                        print(f"ICLOUD OPTIMIZATION for {contact['email']}")
                    
                    # ENHANCED EMAIL SENDING WITH ACTIVITY LOGGING
                    print(f"Sending email to {contact['email']} from {from_email} (Domain: {recipient_domain})")
                    
                    # Log email attempt
                    try:
                        conn = sqlite3.connect('sender.db')
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO activity_logs (campaign_id, campaign_name, action, details, status, timestamp)
                            VALUES (?, ?, ?, ?, ?, datetime('now'))
                        ''', (campaign_id, campaign_name, 'email_sending', f'Sending to {contact["email"]}', 'sending'))
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        print(f"Activity log error: {e}")
                    
                    start_time = time.time()
                    smtp_code = 250  # Default success code
                    
                    try:
                        with smtplib.SMTP(smtp_server['host'], int(smtp_server['port'])) as server:
                            if smtp_server.get('require_auth', True):
                                server.starttls()
                                username = smtp_server.get('username', '')
                                password = smtp_server.get('password', '')
                                if username and password:
                                    print(f"Logging in with username: {username}")
                                    server.login(username, password)
                            
                            # SEND WITH AGGRESSIVE SENDER ENFORCEMENT
                            server.send_message(msg, from_addr=from_email, to_addrs=[contact['email']])
                            print(f"EMAIL SENT WITH SENDER: '{from_name}' <{from_email}>")
                            
                            # Track successful delivery
                            delivery_time = time.time() - start_time
                            try:
                                from smart_delivery_tracker import smart_tracker
                                smart_tracker.track_delivery(
                                    campaign_id=campaign_id,
                                    email=contact['email'],
                                    smtp_server=smtp_server['host'],
                                    smtp_code=250,
                                    smtp_response='Message accepted for delivery',
                                    delivery_time=delivery_time
                                )
                            except Exception as track_error:
                                print(f"Delivery tracking error: {track_error}")
                    
                    except smtplib.SMTPException as smtp_error:
                        # Track failed delivery
                        delivery_time = time.time() - start_time
                        smtp_code = getattr(smtp_error, 'smtp_code', 550)
                        smtp_response = str(smtp_error)
                        
                        try:
                            from smart_delivery_tracker import smart_tracker
                            smart_tracker.track_delivery(
                                campaign_id=campaign_id,
                                email=contact['email'],
                                smtp_server=smtp_server['host'],
                                smtp_code=smtp_code,
                                smtp_response=smtp_response,
                                delivery_time=delivery_time
                            )
                        except Exception as track_error:
                            print(f"Delivery tracking error: {track_error}")
                        
                        raise smtp_error  # Re-raise to trigger error handling below
                    
                    sent_count += 1
                    print(f"Email sent successfully. Progress: {sent_count}/{len(contacts)}")
                    
                    # Log successful delivery with enhanced details
                    contact_email = contact.get('email', 'unknown@example.com')
                    delivery_time = time.time() - start_time
                    log_activity(campaign_id, campaign['name'], 'email_delivered', f'✅ Delivered to {contact_email} | SMTP: {smtp_code} | Time: {delivery_time:.2f}s | Mode: {delivery_mode} | Domain: {recipient_domain}', 'success')
                    print(f"✅ EMAIL DELIVERED: {contact['email']} in {delivery_time:.2f}s to {recipient_domain}")
                    
                    # Update progress
                    execute_db('UPDATE campaigns SET sent_emails = ? WHERE id = ?', (sent_count, campaign_id))
                    
                    # SIMPLIFIED DELAY SYSTEM - NORMAL MODE FOCUS
                    if delivery_mode == 'stealth':
                        # Stealth mode: Variable delays
                        delay = random.uniform(5, 10)
                        print(f"STEALTH DELAY: {delay:.1f}s for {contact['email']}")
                        time.sleep(delay)
                    else:
                        # Normal mode: Reliable 2-3 second delay
                        delay = random.uniform(2, 3)
                        print(f"NORMAL MODE DELAY: {delay:.1f}s for {contact['email']}")
                        time.sleep(delay)
                    
                except Exception as email_error:
                    contact_email = contact.get('email', 'unknown@example.com')
                    error_domain = contact_email.split('@')[1] if '@' in contact_email else 'unknown.com'
                    print(f"Error sending email to {contact_email}: {email_error}")
                    log_activity(campaign_id, campaign['name'], 'email_failed', f'❌ Failed to {contact_email} | Error: {str(email_error)} | Mode: {delivery_mode} | Domain: {error_domain}', 'error')
                    print(f"❌ EMAIL FAILED: {contact_email} - {str(email_error)}")
                    continue
            
            # Mark campaign as completed
            execute_db('UPDATE campaigns SET status = ?, sent_emails = ? WHERE id = ?', ('completed', sent_count, campaign_id))
            log_activity(campaign_id, campaign['name'], 'campaign_completed', f'Campaign completed. Sent {sent_count} emails', 'success')
            
        except Exception as e:
            print(f"CRITICAL CAMPAIGN ERROR: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            
            # Log the failure with details
            try:
                log_activity(campaign_id, 'Unknown Campaign', 'campaign_failed', f'Campaign failed: {str(e)}', 'error')
            except Exception as log_error:
                print(f"Could not log campaign failure: {log_error}")
            
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

# FIXED MESSAGE PROCESSING - PRESERVES LINE BREAKS
def process_message_content(content, contact, auto_spin=True):
    """Process message content while PRESERVING line breaks and formatting"""
    if not content:
        return content
    
    processed = content
    
    # Ensure contact is a dict and has required fields
    if not isinstance(contact, dict):
        contact = {'email': str(contact), 'first_name': '', 'last_name': ''}
    
    # First: Process manual spinning syntax {option1|option2|option3}
    def replace_spinning(match):
        try:
            options = match.group(1).split('|')
            if options:
                return random.choice(options).strip()
            return match.group(0)  # Return original if no options
        except (AttributeError, IndexError):
            return match.group(0)  # Return original on error
    
    processed = re.sub(r'\{([^{}]*\|[^{}]*)\}', replace_spinning, processed)
    
    # Second: LINE-BREAK PRESERVING AUTO-SPIN
    if auto_spin:
        try:
            # CRITICAL FIX: Process line by line to preserve breaks
            lines = processed.split('\n')
            processed_lines = []
            
            for line in lines:
                if line.strip():  # Only process non-empty lines
                    words = line.split()
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
                                if word and len(word) > 0 and word[0].isupper():
                                    replacement = replacement.capitalize()
                                # Preserve punctuation
                                punctuation = re.sub(r'[a-zA-Z]', '', word)
                                words[i] = replacement + punctuation
                    processed_lines.append(' '.join(words))
                else:
                    processed_lines.append(line)  # Preserve empty lines
            
            # CRITICAL: Rejoin with original line breaks
            processed = '\n'.join(processed_lines)
            
        except Exception as spin_error:
            print(f"Auto-spin error: {spin_error}")
            # Continue with unspun content
    
    # Third: Replace contact variables safely
    try:
        processed = processed.replace('{email}', contact.get('email', ''))
        processed = processed.replace('{first_name}', contact.get('first_name', ''))
        processed = processed.replace('{last_name}', contact.get('last_name', ''))
    except Exception as var_error:
        print(f"Variable replacement error: {var_error}")
    
    return processed

# Professional sender name generation
def generate_professional_sender():
    """Generate professional business sender name"""
    professional_names = [
        'Customer Service', 'Support Team', 'Customer Care', 'Service Desk',
        'Account Manager', 'Client Relations', 'Customer Success', 'Help Desk',
        'Sales Team', 'Marketing Team', 'Business Development', 'Client Success'
    ]
    return random.choice(professional_names)

# OPTION 1: Random Username Only (Safest - Uses verified domain)
def generate_random_email_option1(domain):
    """Random username @ verified domain (safest option)"""
    import string
    
    common_usernames = ['info', 'news', 'updates', 'alerts', 'support', 'team', 'hello', 'contact', 
                       'marketing', 'sales', 'promo', 'deals', 'offers', 'newsletter', 'mail',
                       'admin', 'service', 'help', 'welcome', 'notify', 'announce', 'bulletin']
    
    alpha_username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 6))) + str(random.randint(1, 999))
    
    username = random.choice(common_usernames + [alpha_username])
    return f"{username}@{domain}"

# OPTION 2: Random Username + Random Subdomain (Medium risk)
def generate_random_email_option2(domain):
    """Random username @ random subdomain . verified domain"""
    import string
    
    # Random usernames
    common_usernames = ['info', 'news', 'updates', 'alerts', 'support', 'team', 'hello', 'contact']
    alpha_username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 5))) + str(random.randint(1, 99))
    username = random.choice(common_usernames + [alpha_username])
    
    # Random subdomains
    subdomains = ['mail', 'news', 'info', 'updates', 'alerts', 'marketing', 'campaigns', 'newsletter']
    random_subdomain = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 6)))
    subdomain = random.choice(subdomains + [random_subdomain])
    
    return f"{username}@{subdomain}.{domain}"

# OPTION 3: Fixed Username + Random Subdomain (Highest variation)
def generate_random_email_option3(domain):
    """Fixed username @ random subdomain . verified domain"""
    import string
    
    # Fixed professional usernames
    fixed_usernames = ['info', 'contact', 'hello', 'team', 'support']
    username = random.choice(fixed_usernames)
    
    # Random subdomains
    subdomains = ['mail', 'news', 'info', 'updates', 'alerts', 'marketing', 'campaigns', 'newsletter', 'broadcast']
    random_subdomain = ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 7)))
    subdomain = random.choice(subdomains + [random_subdomain])
    
    return f"{username}@{subdomain}.{domain}"

# Legacy function for compatibility
def generate_random_username():
    """Generate random username (legacy)"""
    import string
    common_usernames = ['info', 'news', 'updates', 'alerts', 'support', 'team']
    alpha_username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 6))) + str(random.randint(1, 999))
    return random.choice(common_usernames + [alpha_username])

# Generate advanced random subdomain email (kept for compatibility)
def generate_random_subdomain_email_advanced():
    """Generate email with verified domain"""
    verified_domain = 'fayehallcookies.online'
    random_username = generate_random_username()
    return f"{random_username}@{verified_domain}"

# Generate random subdomain email for better deliverability
def generate_random_subdomain_email(base_email):
    """Generate random subdomain for legitimate email delivery improvement"""
    if '@' not in base_email:
        return generate_random_subdomain_email_advanced()
    
    username, domain = base_email.split('@', 1)
    
    # Extended random subdomain prefixes
    subdomains = ['mail', 'news', 'info', 'updates', 'alerts', 'notify', 'team', 'support',
                 'newsletter', 'marketing', 'campaigns', 'broadcast', 'messaging', 'delivery']
    
    # Generate random alphanumeric subdomain
    import string
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(3, 8)))
    
    # Mix of predefined and random subdomains
    random_subdomain = random.choice(subdomains + [random_chars])
    
    # Create subdomain email
    return f"{username}@{random_subdomain}.{domain}"

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
    """Get activity logs with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        offset = (page - 1) * per_page
        
        # Get total count
        total_count = query_db('SELECT COUNT(*) as count FROM activity_logs', one=True)['count']
        
        # Get paginated logs
        logs = query_db('SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT ? OFFSET ?', (per_page, offset))
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
        
        return jsonify({
            'success': True, 
            'data': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching activity logs: {str(e)}'}), 500

@campaigns_api.route('/activity/clear', methods=['DELETE'])
def clear_activity_logs():
    """Clear all activity logs"""
    try:
        execute_db('DELETE FROM activity_logs')
        return jsonify({'success': True, 'message': 'Activity logs cleared successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error clearing activity logs: {str(e)}'}), 500

# Health endpoint moved to health_api.py to avoid conflicts