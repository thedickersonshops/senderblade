"""
Enrichment API - Handles contact enrichment operations
"""
import sqlite3
import re
import requests
from flask import Blueprint, request, jsonify, g

# Create blueprint
enrichment_api = Blueprint('enrichment_api', __name__)

# Database helper functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
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

# Enrichment routes
@enrichment_api.route('/enrich', methods=['POST'])
def enrich_contacts():
    data = request.json
    contacts = data.get('contacts', [])
    
    if not contacts:
        return jsonify({'success': False, 'message': 'No contacts provided'}), 400
    
    enriched_data = {}
    for contact in contacts:
        email = contact.get('email')
        if not email:
            continue
        
        # Enrich contact
        enriched_contact = enrich_contact(contact)
        enriched_data[email] = enriched_contact
    
    return jsonify({'success': True, 'data': enriched_data})

# Helper function to enrich a contact
def enrich_contact(contact):
    email = contact.get('email')
    first_name = contact.get('first_name', '')
    last_name = contact.get('last_name', '')
    
    # Extract domain
    domain = email.split('@')[1] if '@' in email else ''
    
    # Extract name from email if not provided
    if not first_name or not last_name:
        extracted_name = extract_name_from_email(email)
        if not first_name:
            first_name = extracted_name.get('first_name', '')
        if not last_name:
            last_name = extracted_name.get('last_name', '')
    
    # Get company info from domain
    company_info = get_company_info(domain)
    
    # Get social profiles
    social_profiles = get_social_profiles(first_name, last_name, domain)
    
    # Combine all data
    enriched_data = {
        'first_name': first_name,
        'last_name': last_name,
        'company': company_info.get('name', ''),
        'job_title': guess_job_title(email, domain),
        'social_profiles': social_profiles,
        'source': 'multi_source',
        'confidence_score': calculate_confidence_score(first_name, last_name, company_info)
    }
    
    return enriched_data

# Helper function to extract name from email
def extract_name_from_email(email):
    if not email or '@' not in email:
        return {'first_name': '', 'last_name': ''}
    
    username = email.split('@')[0]
    
    # Remove numbers and special characters
    username = re.sub(r'[0-9_\.\-]+', ' ', username).strip()
    
    # Split into parts
    parts = username.split()
    
    if len(parts) == 0:
        return {'first_name': '', 'last_name': ''}
    elif len(parts) == 1:
        return {'first_name': parts[0].capitalize(), 'last_name': ''}
    else:
        return {
            'first_name': parts[0].capitalize(),
            'last_name': parts[-1].capitalize()
        }

# Helper function to get company info from domain
def get_company_info(domain):
    if not domain:
        return {'name': ''}
    
    # Remove TLD
    company_name = domain.split('.')[0]
    
    # Clean up company name
    company_name = company_name.replace('-', ' ').replace('_', ' ')
    company_name = ' '.join(word.capitalize() for word in company_name.split())
    
    return {'name': company_name}

# Helper function to get social profiles
def get_social_profiles(first_name, last_name, domain):
    if not first_name or not last_name:
        return {}
    
    # Create placeholder social profiles
    social_profiles = {
        'linkedin': f"https://www.linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
        'twitter': f"https://twitter.com/{first_name.lower()}{last_name.lower()}"
    }
    
    return social_profiles

# Helper function to guess job title
def guess_job_title(email, domain):
    # Common job titles
    job_titles = [
        'Software Engineer',
        'Marketing Manager',
        'Sales Representative',
        'Product Manager',
        'Data Analyst',
        'Customer Support',
        'Operations Manager'
    ]
    
    # Use hash of email to select a job title
    hash_value = sum(ord(c) for c in email)
    index = hash_value % len(job_titles)
    
    return job_titles[index]

# Helper function to calculate confidence score
def calculate_confidence_score(first_name, last_name, company_info):
    score = 0.5  # Base score
    
    if first_name:
        score += 0.1
    
    if last_name:
        score += 0.1
    
    if company_info.get('name'):
        score += 0.1
    
    # Cap at 0.9 since we're not using real data sources
    return min(0.9, score)