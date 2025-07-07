"""
Generator API - Handles random email generation
"""
import random
import string
from flask import Blueprint, request, jsonify

# Create blueprint
generator_api = Blueprint('generator_api', __name__)

@generator_api.route('/generate/emails', methods=['POST'])
def generate_emails():
    data = request.json
    count = data.get('count', 10)
    gen_type = data.get('type', 'random')
    domain = data.get('domain', '')
    
    if count > 1000:
        count = 1000  # Limit to 1000 emails
    
    emails = []
    
    # Generate random emails
    for _ in range(count):
        if gen_type == 'domain' and domain:
            # Use custom domain
            email = generate_random_email(domain=domain)
        elif gen_type == 'subdomain' and domain:
            # Use random subdomain with custom domain
            email = generate_random_email(subdomain=True, domain=domain)
        else:
            # Completely random
            email = generate_random_email()
        
        # Add to list with random names
        emails.append({
            'email': email,
            'first_name': random_first_name(),
            'last_name': random_last_name()
        })
    
    return jsonify({
        'success': True,
        'data': emails
    })

def generate_random_email(domain=None, subdomain=False):
    # Random username
    username_length = random.randint(5, 10)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
    
    if not domain:
        # Random domain
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'mail.com']
        domain = random.choice(domains)
    
    if subdomain:
        # Add random subdomain
        subdomain_length = random.randint(3, 8)
        subdomain_name = ''.join(random.choices(string.ascii_lowercase, k=subdomain_length))
        return f"{username}@{subdomain_name}.{domain}"
    else:
        return f"{username}@{domain}"

def random_first_name():
    first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Jennifer', 
                  'William', 'Elizabeth', 'James', 'Linda', 'Richard', 'Patricia', 'Thomas', 'Mary']
    return random.choice(first_names)

def random_last_name():
    last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson',
                 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin']
    return random.choice(last_names)