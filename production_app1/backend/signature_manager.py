"""
Enhanced Signature Manager - Professional Email Signatures
"""
import sqlite3
import time
from flask import Blueprint, request, jsonify

# Create blueprint
signature_manager = Blueprint('signature_manager', __name__)

class SignatureManager:
    def __init__(self):
        self.init_signature_tables()
    
    def init_signature_tables(self):
        """Initialize signature tables"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_signatures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    html_content TEXT,
                    position TEXT DEFAULT 'bottom',
                    is_default BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Signature manager init error: {e}")
    
    def create_signature(self, user_id, name, content, html_content=None, position='bottom'):
        """Create a new signature with support for long content"""
        try:
            # Validate content length (allow up to 5000 characters)
            if len(content) > 5000:
                return {'success': False, 'message': 'Signature content too long (max 5000 characters)'}
            
            # Auto-generate HTML version if not provided
            if not html_content and content:
                html_content = content.replace('\n', '<br>\n')
            
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO email_signatures (user_id, name, content, html_content, position)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, content, html_content, position))
            
            signature_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'success': True, 'signature_id': signature_id, 'message': 'Signature saved successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_signatures(self, user_id):
        """Get all signatures for a user"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, content, html_content, position, is_default, created_at
                FROM email_signatures 
                WHERE user_id = ? 
                ORDER BY is_default DESC, created_at DESC
            ''', (user_id,))
            
            signatures = []
            for row in cursor.fetchall():
                signatures.append({
                    'id': row[0],
                    'name': row[1],
                    'content': row[2],
                    'html_content': row[3],
                    'position': row[4],
                    'is_default': bool(row[5]),
                    'created_at': row[6],
                    'preview': row[2][:100] + '...' if len(row[2]) > 100 else row[2]  # Add preview
                })
            
            conn.close()
            return {'success': True, 'signatures': signatures}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def set_default_signature(self, user_id, signature_id):
        """Set a signature as default"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Remove default from all signatures
            cursor.execute('UPDATE email_signatures SET is_default = 0 WHERE user_id = ?', (user_id,))
            
            # Set new default
            cursor.execute('UPDATE email_signatures SET is_default = 1 WHERE id = ? AND user_id = ?', 
                         (signature_id, user_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Default signature updated'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def apply_signature_to_message(self, message_content, signature_content, position='bottom', is_html=False):
        """Apply signature to message content with enhanced formatting"""
        try:
            if not signature_content:
                return message_content
            
            if is_html:
                # HTML message with proper signature formatting
                # Ensure signature lines are properly separated
                if not signature_content.startswith('<'):
                    # Convert plain text signature to HTML with proper line breaks
                    signature_lines = signature_content.split('\n')
                    formatted_lines = []
                    for line in signature_lines:
                        if line.strip():
                            formatted_lines.append(line.strip())
                    signature_content = '<br>\n'.join(formatted_lines)
                
                if position == 'top':
                    return f"{signature_content}<br><br>\n{message_content}"
                else:  # bottom
                    return f"{message_content}<br><br>\n---<br>\n{signature_content}"
            else:
                # Plain text message with proper line breaks
                # Ensure signature lines are properly separated
                signature_lines = signature_content.split('\n')
                formatted_lines = []
                for line in signature_lines:
                    if line.strip():
                        formatted_lines.append(line.strip())
                formatted_signature = '\n'.join(formatted_lines)
                
                if position == 'top':
                    return f"{formatted_signature}\n\n{message_content}"
                else:  # bottom
                    return f"{message_content}\n\n---\n{formatted_signature}"
                    
        except Exception as e:
            print(f"Signature application error: {e}")
            return message_content
    
    def get_default_signature(self, user_id):
        """Get user's default signature"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, content, html_content, position
                FROM email_signatures 
                WHERE user_id = ? AND is_default = 1
                LIMIT 1
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'success': True,
                    'signature': {
                        'id': result[0],
                        'name': result[1],
                        'content': result[2],
                        'html_content': result[3],
                        'position': result[4]
                    }
                }
            else:
                return {'success': False, 'message': 'No default signature found'}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}

# Global signature manager
signature_mgr = SignatureManager()

# API Routes
@signature_manager.route('/signatures', methods=['GET'])
def get_signatures():
    """Get user signatures"""
    user_id = request.args.get('user_id', 1)  # Default to user 1 for now
    result = signature_mgr.get_signatures(user_id)
    return jsonify(result)

@signature_manager.route('/signatures', methods=['POST'])
def create_signature():
    """Create new signature"""
    data = request.json
    user_id = data.get('user_id', 1)
    name = data.get('name')
    content = data.get('content')
    html_content = data.get('html_content')
    position = data.get('position', 'bottom')
    
    result = signature_mgr.create_signature(user_id, name, content, html_content, position)
    return jsonify(result)

@signature_manager.route('/signatures/<int:signature_id>/default', methods=['POST'])
def set_default_signature(signature_id):
    """Set signature as default"""
    data = request.json
    user_id = data.get('user_id', 1)
    
    result = signature_mgr.set_default_signature(user_id, signature_id)
    return jsonify(result)

@signature_manager.route('/signatures/default', methods=['GET'])
def get_default_signature():
    """Get user's default signature"""
    user_id = request.args.get('user_id', 1)
    result = signature_mgr.get_default_signature(user_id)
    return jsonify(result)

@signature_manager.route('/signatures/apply', methods=['POST'])
def apply_signature():
    """Apply signature to message content"""
    data = request.json
    message_content = data.get('message_content', '')
    signature_content = data.get('signature_content', '')
    position = data.get('position', 'bottom')
    is_html = data.get('is_html', False)
    
    result_content = signature_mgr.apply_signature_to_message(
        message_content, signature_content, position, is_html
    )
    
    return jsonify({
        'success': True,
        'content': result_content
    })