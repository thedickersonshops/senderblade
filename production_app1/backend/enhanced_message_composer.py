"""
Enhanced Message Composer - Rich Email Editor
"""
import sqlite3
from flask import Blueprint, request, jsonify
from signature_manager import signature_mgr

# Create blueprint
message_composer = Blueprint('message_composer', __name__)

class EnhancedMessageComposer:
    def __init__(self):
        self.init_composer_tables()
    
    def init_composer_tables(self):
        """Initialize message composer tables"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Email templates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    subject TEXT,
                    html_content TEXT,
                    plain_content TEXT,
                    template_type TEXT DEFAULT 'custom',
                    category TEXT DEFAULT 'general',
                    is_favorite BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Content blocks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    block_type TEXT DEFAULT 'text',
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Message composer init error: {e}")
    
    def save_template(self, user_id, name, subject, html_content, plain_content, category='general'):
        """Save email template"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO email_templates (user_id, name, subject, html_content, plain_content, category)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, name, subject, html_content, plain_content, category))
            
            template_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'success': True, 'template_id': template_id}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_templates(self, user_id):
        """Get user templates"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, subject, html_content, plain_content, category, is_favorite, created_at
                FROM email_templates 
                WHERE user_id = ? 
                ORDER BY is_favorite DESC, created_at DESC
            ''', (user_id,))
            
            templates = []
            for row in cursor.fetchall():
                templates.append({
                    'id': row[0],
                    'name': row[1],
                    'subject': row[2],
                    'html_content': row[3],
                    'plain_content': row[4],
                    'category': row[5],
                    'is_favorite': bool(row[6]),
                    'created_at': row[7]
                })
            
            conn.close()
            return {'success': True, 'templates': templates}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_content_blocks(self):
        """Get reusable content blocks"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, content, block_type, category
                FROM content_blocks 
                ORDER BY category, name
            ''')
            
            blocks = []
            for row in cursor.fetchall():
                blocks.append({
                    'id': row[0],
                    'name': row[1],
                    'content': row[2],
                    'block_type': row[3],
                    'category': row[4]
                })
            
            conn.close()
            return {'success': True, 'blocks': blocks}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def compose_message_with_signature(self, message_content, html_content, user_id, signature_id=None):
        """Compose message with signature integration"""
        try:
            # Get signature (default if not specified)
            if signature_id:
                # Get specific signature
                signatures_result = signature_mgr.get_signatures(user_id)
                if signatures_result['success']:
                    signature = next((s for s in signatures_result['signatures'] if s['id'] == signature_id), None)
                else:
                    signature = None
            else:
                # Get default signature
                signature_result = signature_mgr.get_default_signature(user_id)
                signature = signature_result.get('signature') if signature_result['success'] else None
            
            if signature:
                # Apply signature to plain text
                final_message = signature_mgr.apply_signature_to_message(
                    message_content, signature['content'], signature['position'], False
                )
                
                # Apply signature to HTML if provided with enhanced formatting
                final_html = None
                if html_content and signature['html_content']:
                    final_html = signature_mgr.apply_signature_to_message(
                        html_content, signature['html_content'], signature['position'], True
                    )
                elif html_content:
                    # Convert plain signature to HTML with proper line breaks
                    signature_lines = signature['content'].split('\n')
                    html_signature_lines = []
                    for line in signature_lines:
                        if line.strip():
                            html_signature_lines.append(line.strip())
                    html_signature = '<br>\n'.join(html_signature_lines)
                    final_html = signature_mgr.apply_signature_to_message(
                        html_content, html_signature, signature['position'], True
                    )
                
                return {
                    'success': True,
                    'message_content': final_message,
                    'html_content': final_html,
                    'signature_applied': signature['name']
                }
            else:
                return {
                    'success': True,
                    'message_content': message_content,
                    'html_content': html_content,
                    'signature_applied': None
                }
                
        except Exception as e:
            return {'success': False, 'message': str(e)}

# Global composer instance
enhanced_composer = EnhancedMessageComposer()

# API Routes
@message_composer.route('/templates', methods=['GET'])
def get_templates():
    """Get email templates"""
    user_id = request.args.get('user_id', 1)
    result = enhanced_composer.get_templates(user_id)
    return jsonify(result)

@message_composer.route('/templates', methods=['POST'])
def save_template():
    """Save email template"""
    data = request.json
    result = enhanced_composer.save_template(
        data.get('user_id', 1),
        data.get('name'),
        data.get('subject'),
        data.get('html_content'),
        data.get('plain_content'),
        data.get('category', 'general')
    )
    return jsonify(result)

@message_composer.route('/content-blocks', methods=['GET'])
def get_content_blocks():
    """Get content blocks"""
    result = enhanced_composer.get_content_blocks()
    return jsonify(result)

@message_composer.route('/compose-with-signature', methods=['POST'])
def compose_with_signature():
    """Compose message with signature integration"""
    data = request.json
    result = enhanced_composer.compose_message_with_signature(
        data.get('message_content', ''),
        data.get('html_content'),
        data.get('user_id', 1),
        data.get('signature_id')
    )
    return jsonify(result)