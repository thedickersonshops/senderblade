"""
Domains API - Manages sender domains for random subdomain generation
"""
import sqlite3
from flask import Blueprint, request, jsonify
from simple_db import query_db as simple_query_db, execute_db as simple_execute_db

# Create blueprint
domains_api = Blueprint('domains_api', __name__)

# Override to use sender.db
def query_db(query, args=(), one=False):
    return simple_query_db(query, args, one, 'sender.db')

def execute_db(query, args=()):
    return simple_execute_db(query, args, 'sender.db')

@domains_api.route('/domains', methods=['GET'])
def get_domains():
    """Get all sender domains"""
    domains = query_db('SELECT * FROM sender_domains ORDER BY created_at DESC')
    result = []
    for domain in domains:
        result.append({
            'id': domain['id'],
            'domain': domain['domain'],
            'is_active': bool(domain['is_active']),
            'created_at': domain['created_at']
        })
    return jsonify({'success': True, 'data': result})

@domains_api.route('/domains', methods=['POST'])
def add_domain():
    """Add new sender domain"""
    data = request.json
    domain = data.get('domain', '').strip().lower()
    
    if not domain:
        return jsonify({'success': False, 'message': 'Domain is required'}), 400
    
    # Basic domain validation
    if not '.' in domain or ' ' in domain:
        return jsonify({'success': False, 'message': 'Invalid domain format'}), 400
    
    # Check for duplicates
    existing = query_db('SELECT * FROM sender_domains WHERE domain = ?', [domain], one=True)
    if existing:
        return jsonify({'success': False, 'message': 'Domain already exists'}), 400
    
    # Add domain
    domain_id = execute_db(
        'INSERT INTO sender_domains (domain, is_active) VALUES (?, ?)',
        (domain, 1)
    )
    
    return jsonify({
        'success': True,
        'data': {
            'id': domain_id,
            'domain': domain,
            'is_active': True
        },
        'message': 'Domain added successfully'
    })

@domains_api.route('/domains/<int:domain_id>', methods=['DELETE'])
def delete_domain(domain_id):
    """Delete sender domain"""
    domain = query_db('SELECT * FROM sender_domains WHERE id = ?', [domain_id], one=True)
    if not domain:
        return jsonify({'success': False, 'message': 'Domain not found'}), 404
    
    execute_db('DELETE FROM sender_domains WHERE id = ?', [domain_id])
    return jsonify({'success': True, 'message': 'Domain deleted successfully'})

@domains_api.route('/domains/<int:domain_id>/toggle', methods=['POST'])
def toggle_domain(domain_id):
    """Toggle domain active status"""
    domain = query_db('SELECT * FROM sender_domains WHERE id = ?', [domain_id], one=True)
    if not domain:
        return jsonify({'success': False, 'message': 'Domain not found'}), 404
    
    new_status = 0 if domain['is_active'] else 1
    execute_db('UPDATE sender_domains SET is_active = ? WHERE id = ?', [new_status, domain_id])
    
    return jsonify({
        'success': True,
        'data': {'is_active': bool(new_status)},
        'message': f'Domain {"activated" if new_status else "deactivated"}'
    })

@domains_api.route('/domains/active', methods=['GET'])
def get_active_domains():
    """Get only active domains for random subdomain generation"""
    domains = query_db('SELECT domain FROM sender_domains WHERE is_active = 1')
    domain_list = [domain['domain'] for domain in domains]
    return jsonify({'success': True, 'data': domain_list})