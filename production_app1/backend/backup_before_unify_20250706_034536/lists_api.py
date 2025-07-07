"""
Lists API - Handles all list and contact operations (simplified)
"""
import json
import sqlite3
from flask import Blueprint, request, jsonify, g

# Create blueprint
lists_api = Blueprint('lists_api', __name__)

# Database helper functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('sender.db')
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id

# Lists routes
@lists_api.route('/lists', methods=['GET'])
def get_lists():
    lists = query_db('SELECT l.*, COUNT(c.id) as contact_count FROM lists l LEFT JOIN contacts c ON l.id = c.list_id GROUP BY l.id')
    result = []
    for lst in lists:
        result.append({
            'id': lst['id'],
            'name': lst['name'],
            'description': lst['description'],
            'contact_count': lst['contact_count'],
            'created_at': lst['created_at']
        })
    return jsonify({'success': True, 'data': result})

@lists_api.route('/lists', methods=['POST'])
def create_list():
    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({'success': False, 'message': 'List name is required'}), 400
    
    list_id = execute_db('INSERT INTO lists (name, description) VALUES (?, ?)', (name, description))
    
    return jsonify({
        'success': True,
        'data': {
            'id': list_id,
            'name': name,
            'description': description,
            'contact_count': 0
        },
        'message': 'List created successfully'
    })

@lists_api.route('/lists/<int:list_id>', methods=['GET'])
def get_list(list_id):
    lst = query_db('SELECT l.*, COUNT(c.id) as contact_count FROM lists l LEFT JOIN contacts c ON l.id = c.list_id WHERE l.id = ? GROUP BY l.id', [list_id], one=True)
    
    if not lst:
        return jsonify({'success': False, 'message': 'List not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': lst['id'],
            'name': lst['name'],
            'description': lst['description'],
            'contact_count': lst['contact_count'],
            'created_at': lst['created_at']
        }
    })

@lists_api.route('/lists/<int:list_id>', methods=['DELETE'])
def delete_list(list_id):
    # Check if list exists
    lst = query_db('SELECT * FROM lists WHERE id = ?', [list_id], one=True)
    if not lst:
        return jsonify({'success': False, 'message': 'List not found'}), 404
    
    # Delete contacts first
    execute_db('DELETE FROM contacts WHERE list_id = ?', [list_id])
    
    # Delete list
    execute_db('DELETE FROM lists WHERE id = ?', [list_id])
    
    return jsonify({'success': True, 'message': 'List deleted successfully'})

@lists_api.route('/lists/<int:list_id>/contacts', methods=['GET'])
def get_contacts(list_id):
    # Check if list exists
    lst = query_db('SELECT * FROM lists WHERE id = ?', [list_id], one=True)
    if not lst:
        return jsonify({'success': False, 'message': 'List not found'}), 404
    
    # Get page parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total count
    total_count = query_db('SELECT COUNT(*) as count FROM contacts WHERE list_id = ?', [list_id], one=True)['count']
    
    # Get contacts with pagination
    contacts = query_db('SELECT * FROM contacts WHERE list_id = ? LIMIT ? OFFSET ?', 
                      [list_id, per_page, offset])
    
    result = []
    for contact in contacts:
        result.append({
            'id': contact['id'],
            'email': contact['email'],
            'first_name': contact['first_name'],
            'last_name': contact['last_name'],
            'created_at': contact['created_at']
        })
    
    return jsonify({
        'success': True,
        'data': result,
        'pagination': {
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'pages': (total_count + per_page - 1) // per_page
        }
    })

@lists_api.route('/lists/<int:list_id>/contacts', methods=['POST'])
def add_contacts(list_id):
    # Check if list exists
    lst = query_db('SELECT * FROM lists WHERE id = ?', [list_id], one=True)
    if not lst:
        return jsonify({'success': False, 'message': 'List not found'}), 404
    
    data = request.json
    contacts = data.get('contacts', [])
    
    if not contacts:
        return jsonify({'success': False, 'message': 'No contacts provided'}), 400
    
    added_count = 0
    for contact in contacts:
        email = contact.get('email')
        if not email:
            continue
        
        # Check if contact already exists
        existing = query_db('SELECT * FROM contacts WHERE list_id = ? AND email = ?', [list_id, email], one=True)
        if existing:
            continue
        
        first_name = contact.get('first_name', '')
        last_name = contact.get('last_name', '')
        
        execute_db(
            'INSERT INTO contacts (list_id, email, first_name, last_name) VALUES (?, ?, ?, ?)',
            (list_id, email, first_name, last_name)
        )
        added_count += 1
    
    return jsonify({
        'success': True,
        'message': f'{added_count} contacts added successfully',
        'added_count': added_count
    })