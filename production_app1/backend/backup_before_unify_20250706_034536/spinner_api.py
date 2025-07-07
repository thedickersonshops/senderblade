"""
Spinner API - Handles message spinning functionality
"""
import os
import re
import random
import json
import sqlite3
import base64
import hashlib
from flask import Blueprint, request, jsonify, g
from message_spinner import get_message_spinner

# Create blueprint
spinner_api = Blueprint('spinner_api', __name__)

# Import database helper functions
from simple_db import query_db as simple_query_db, execute_db as simple_execute_db

# Override to use sender.db
def query_db(query, args=(), one=False):
    return simple_query_db(query, args, one, 'sender.db')

def execute_db(query, args=()):
    return simple_execute_db(query, args, 'sender.db')

@spinner_api.route('/spinner/process', methods=['POST'])
def process_spinner():
    """
    Process a message with spinning syntax
    
    Spinning syntax:
    - {option1|option2|option3} - Random selection from options
    - {{first_name}}, {{last_name}}, {{email}} - Personalization variables
    """
    data = request.json
    content = data.get('content', '')
    subject = data.get('subject', '')
    personalization = data.get('personalization', {})
    count = data.get('count', 1)
    
    if not content:
        return jsonify({'success': False, 'message': 'Content is required'}), 400
    
    try:
        spinner = get_message_spinner()
        
        # Process the content with spinning syntax
        content_variations = spinner.generate_variations(content, count)
        
        # Process subject if provided
        subject_variations = []
        if subject:
            subject_variations = spinner.generate_variations(subject, count)
        
        return jsonify({
            'success': True,
            'variations': content_variations,
            'subject_variations': subject_variations
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing spinner: {str(e)}'}), 500

@spinner_api.route('/spinner/auto', methods=['POST'])
def auto_spin():
    """Automatically add spinning syntax to content"""
    data = request.json
    content = data.get('content', '')
    subject = data.get('subject', '')
    level = data.get('level', 'medium')  # low, medium, high
    
    if not content:
        return jsonify({'success': False, 'message': 'Content is required'}), 400
    
    try:
        spinner = get_message_spinner()
        
        # Auto-spin content
        spun_content = spinner.auto_spin(content, level)
        
        # Auto-spin subject if provided
        spun_subject = ""
        if subject:
            spun_subject = spinner.auto_spin(subject, level)
        
        return jsonify({
            'success': True,
            'data': {
                'original': content,
                'spun': spun_content,
                'original_subject': subject,
                'spun_subject': spun_subject
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error auto-spinning content: {str(e)}'}), 500

@spinner_api.route('/spinner/preview', methods=['POST'])
def preview_spinner():
    """
    Generate preview variations of a message with spinning syntax
    """
    data = request.json
    content = data.get('content', '')
    subject = data.get('subject', '')
    count = data.get('count', 3)  # Default to 3 previews
    
    if not content:
        return jsonify({'success': False, 'message': 'Content is required'}), 400
    
    try:
        spinner = get_message_spinner()
        
        # Generate content variations using simple spinning
        content_variations = []
        for _ in range(count):
            content_variations.append(spinner.spin_text(content))
        
        # Generate subject variations if provided
        subject_variations = []
        if subject:
            for _ in range(count):
                subject_variations.append(spinner.spin_text(subject))
        
        # Sample personalization data for preview
        sample_personalization = {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@example.com',
            'company': 'Acme Inc',
            'job_title': 'Marketing Manager',
            'sender_name': 'Your Name',
            'sender_email': 'you@example.com'
        }
        
        # Apply personalization to previews
        for i in range(len(content_variations)):
            for var, value in sample_personalization.items():
                # Replace both formats: {first_name} and {{first_name}}
                # Be careful to avoid replacing spinning syntax like {option1|option2}
                content_variations[i] = re.sub(r'\{\{' + re.escape(var) + r'\}\}', value, content_variations[i])
                content_variations[i] = re.sub(r'\{' + re.escape(var) + r'\}(?![^<]*>|\|)', value, content_variations[i])
            
        if subject_variations:
            for i in range(len(subject_variations)):
                for var, value in sample_personalization.items():
                    # Replace both formats: {first_name} and {{first_name}}
                    # Be careful to avoid replacing spinning syntax like {option1|option2}
                    subject_variations[i] = re.sub(r'\{\{' + re.escape(var) + r'\}\}', value, subject_variations[i])
                    subject_variations[i] = re.sub(r'\{' + re.escape(var) + r'\}(?![^<]*>|\|)', value, subject_variations[i])
        
        return jsonify({
            'success': True,
            'content_variations': content_variations,
            'subject_variations': subject_variations
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating preview: {str(e)}'}), 500

@spinner_api.route('/spinner/analyze', methods=['POST'])
def analyze_spinner():
    """
    Analyze a message with spinning syntax to show possible variations
    """
    data = request.json
    content = data.get('content', '')
    
    if not content:
        return jsonify({'success': False, 'message': 'Content is required'}), 400
    
    try:
        # Find all spinning syntax blocks
        spinner_blocks = re.findall(r'\{([^{}]+)\}', content)
        
        variations = {}
        total_combinations = 1
        
        for i, block in enumerate(spinner_blocks):
            if '|' in block:
                options = block.split('|')
                variations[f'Block {i+1}'] = {
                    'original': f'{{{block}}}',
                    'options': options,
                    'count': len(options)
                }
                total_combinations *= len(options)
        
        # Find personalization variables
        personalization_vars = []
        for match in re.findall(r'\{\{([^{}]+)\}\}', content):
            if match not in personalization_vars:
                personalization_vars.append(match)
        
        return jsonify({
            'success': True,
            'data': {
                'variations': variations,
                'total_combinations': total_combinations,
                'personalization_variables': personalization_vars
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error analyzing spinner: {str(e)}'}), 500

@spinner_api.route('/spinner/encrypt', methods=['POST'])
def encrypt_message():
    """Encrypt a message with a password"""
    data = request.json
    content = data.get('content', '')
    password = data.get('password', '')
    
    if not content:
        return jsonify({'success': False, 'message': 'Content is required'}), 400
    
    if not password:
        return jsonify({'success': False, 'message': 'Password is required'}), 400
    
    try:
        # Generate a key from the password
        key = hashlib.sha256(password.encode()).digest()
        
        # Simple XOR encryption (for compatibility without external libraries)
        key_bytes = bytearray(key)
        content_bytes = bytearray(content.encode('utf-8'))
        encrypted_bytes = bytearray(len(content_bytes))
        
        for i in range(len(content_bytes)):
            encrypted_bytes[i] = content_bytes[i] ^ key_bytes[i % len(key_bytes)]
        
        # Base64 encode for safe transport
        encrypted_content = base64.b64encode(encrypted_bytes).decode('utf-8')
        
        return jsonify({
            'success': True,
            'data': {
                'encrypted_content': encrypted_content
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error encrypting message: {str(e)}'}), 500

@spinner_api.route('/spinner/decrypt', methods=['POST'])
def decrypt_message():
    """Decrypt a message with a password"""
    data = request.json
    encrypted_content = data.get('encrypted_content', '')
    password = data.get('password', '')
    
    if not encrypted_content:
        return jsonify({'success': False, 'message': 'Encrypted content is required'}), 400
    
    if not password:
        return jsonify({'success': False, 'message': 'Password is required'}), 400
    
    try:
        # Generate a key from the password
        key = hashlib.sha256(password.encode()).digest()
        
        # Decode base64
        encrypted_bytes = bytearray(base64.b64decode(encrypted_content))
        
        # Simple XOR decryption
        key_bytes = bytearray(key)
        decrypted_bytes = bytearray(len(encrypted_bytes))
        
        for i in range(len(encrypted_bytes)):
            decrypted_bytes[i] = encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)]
        
        # Decode to string
        decrypted_content = decrypted_bytes.decode('utf-8')
        
        return jsonify({
            'success': True,
            'data': {
                'decrypted_content': decrypted_content
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error decrypting message: {str(e)}'}), 500

# Template management endpoints
@spinner_api.route('/spinner/templates', methods=['GET'])
def get_templates():
    """Get all spinner templates"""
    try:
        templates = query_db('SELECT * FROM spinner_templates ORDER BY name')
        result = []
        for template in templates:
            result.append({
                'id': template['id'],
                'name': template['name'],
                'content': template['content'],
                'subject': template['subject'] or '',
                'description': template['description'],
                'created_at': template['created_at']
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching templates: {str(e)}'}), 500

@spinner_api.route('/spinner/templates', methods=['POST'])
def create_template():
    """Create a new spinner template"""
    data = request.json
    name = data.get('name')
    content = data.get('content')
    subject = data.get('subject', '')
    description = data.get('description', '')
    
    if not name or not content:
        return jsonify({'success': False, 'message': 'Name and content are required'}), 400
    
    try:
        template_id = execute_db(
            'INSERT INTO spinner_templates (name, content, subject, description) VALUES (?, ?, ?, ?)',
            (name, content, subject, description)
        )
        
        return jsonify({
            'success': True,
            'data': {
                'id': template_id,
                'name': name,
                'content': content,
                'subject': subject,
                'description': description
            },
            'message': 'Template created successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating template: {str(e)}'}), 500