"""
A/B Testing System - Campaign Optimization
"""
import sqlite3
import random
import time
from flask import Blueprint, request, jsonify

# Create blueprint
ab_testing = Blueprint('ab_testing', __name__)

class ABTestingSystem:
    def __init__(self):
        self.init_ab_tables()
    
    def init_ab_tables(self):
        """Initialize A/B testing tables"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # A/B test campaigns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ab_test_campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    test_type TEXT DEFAULT 'subject_line',
                    split_percentage INTEGER DEFAULT 50,
                    status TEXT DEFAULT 'draft',
                    winner_variant TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            # A/B test variants table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ab_test_variants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER,
                    variant_name TEXT NOT NULL,
                    subject_line TEXT,
                    message_content TEXT,
                    html_content TEXT,
                    from_name TEXT,
                    sent_count INTEGER DEFAULT 0,
                    open_count INTEGER DEFAULT 0,
                    click_count INTEGER DEFAULT 0,
                    conversion_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES ab_test_campaigns (id)
                )
            ''')
            
            # A/B test results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ab_test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER,
                    variant_id INTEGER,
                    email TEXT,
                    sent_at TIMESTAMP,
                    opened_at TIMESTAMP,
                    clicked_at TIMESTAMP,
                    converted_at TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES ab_test_campaigns (id),
                    FOREIGN KEY (variant_id) REFERENCES ab_test_variants (id)
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"A/B testing init error: {e}")
    
    def create_ab_test(self, name, description, test_type, split_percentage=50):
        """Create new A/B test"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ab_test_campaigns (name, description, test_type, split_percentage)
                VALUES (?, ?, ?, ?)
            ''', (name, description, test_type, split_percentage))
            
            test_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'success': True, 'test_id': test_id}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def add_variant(self, test_id, variant_name, subject_line, message_content, html_content=None, from_name=None):
        """Add variant to A/B test"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ab_test_variants 
                (test_id, variant_name, subject_line, message_content, html_content, from_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (test_id, variant_name, subject_line, message_content, html_content, from_name))
            
            variant_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {'success': True, 'variant_id': variant_id}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_ab_tests(self):
        """Get all A/B tests"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, test_type, split_percentage, status, 
                       winner_variant, created_at, started_at, completed_at
                FROM ab_test_campaigns 
                ORDER BY created_at DESC
            ''')
            
            tests = []
            for row in cursor.fetchall():
                test_id = row[0]
                
                # Get variants for this test
                cursor.execute('''
                    SELECT id, variant_name, subject_line, sent_count, open_count, click_count
                    FROM ab_test_variants 
                    WHERE test_id = ?
                ''', (test_id,))
                
                variants = []
                for variant_row in cursor.fetchall():
                    open_rate = (variant_row[4] / variant_row[3] * 100) if variant_row[3] > 0 else 0
                    click_rate = (variant_row[5] / variant_row[3] * 100) if variant_row[3] > 0 else 0
                    
                    variants.append({
                        'id': variant_row[0],
                        'name': variant_row[1],
                        'subject_line': variant_row[2],
                        'sent_count': variant_row[3],
                        'open_count': variant_row[4],
                        'click_count': variant_row[5],
                        'open_rate': round(open_rate, 2),
                        'click_rate': round(click_rate, 2)
                    })
                
                tests.append({
                    'id': test_id,
                    'name': row[1],
                    'description': row[2],
                    'test_type': row[3],
                    'split_percentage': row[4],
                    'status': row[5],
                    'winner_variant': row[6],
                    'created_at': row[7],
                    'started_at': row[8],
                    'completed_at': row[9],
                    'variants': variants
                })
            
            conn.close()
            return {'success': True, 'tests': tests}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def select_variant_for_recipient(self, test_id, email):
        """Select which variant to send to a recipient"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Get test details
            cursor.execute('SELECT split_percentage FROM ab_test_campaigns WHERE id = ?', (test_id,))
            test = cursor.fetchone()
            if not test:
                return {'success': False, 'message': 'Test not found'}
            
            split_percentage = test[0]
            
            # Get variants
            cursor.execute('''
                SELECT id, variant_name, subject_line, message_content, html_content, from_name
                FROM ab_test_variants 
                WHERE test_id = ? 
                ORDER BY id
            ''', (test_id,))
            
            variants = cursor.fetchall()
            if len(variants) < 2:
                return {'success': False, 'message': 'Need at least 2 variants'}
            
            conn.close()
            
            # Use email hash for consistent assignment
            email_hash = hash(email) % 100
            
            if email_hash < split_percentage:
                selected_variant = variants[0]
            else:
                selected_variant = variants[1]
            
            return {
                'success': True,
                'variant': {
                    'id': selected_variant[0],
                    'name': selected_variant[1],
                    'subject_line': selected_variant[2],
                    'message_content': selected_variant[3],
                    'html_content': selected_variant[4],
                    'from_name': selected_variant[5]
                }
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def record_send(self, test_id, variant_id, email):
        """Record that an email was sent"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Record in results
            cursor.execute('''
                INSERT INTO ab_test_results (test_id, variant_id, email, sent_at)
                VALUES (?, ?, ?, datetime('now'))
            ''', (test_id, variant_id, email))
            
            # Update variant sent count
            cursor.execute('''
                UPDATE ab_test_variants 
                SET sent_count = sent_count + 1 
                WHERE id = ?
            ''', (variant_id,))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def analyze_test_results(self, test_id):
        """Analyze A/B test results and determine winner"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT v.id, v.variant_name, v.sent_count, v.open_count, v.click_count,
                       (CAST(v.open_count AS FLOAT) / v.sent_count * 100) as open_rate,
                       (CAST(v.click_count AS FLOAT) / v.sent_count * 100) as click_rate
                FROM ab_test_variants v
                WHERE v.test_id = ? AND v.sent_count > 0
                ORDER BY open_rate DESC, click_rate DESC
            ''', (test_id,))
            
            results = cursor.fetchall()
            
            if len(results) >= 2:
                winner = results[0]  # Highest open rate
                
                # Update test with winner
                cursor.execute('''
                    UPDATE ab_test_campaigns 
                    SET winner_variant = ?, status = 'completed', completed_at = datetime('now')
                    WHERE id = ?
                ''', (winner[1], test_id))
                
                conn.commit()
            
            conn.close()
            
            analysis = []
            for result in results:
                analysis.append({
                    'variant_id': result[0],
                    'variant_name': result[1],
                    'sent_count': result[2],
                    'open_count': result[3],
                    'click_count': result[4],
                    'open_rate': round(result[5], 2) if result[5] else 0,
                    'click_rate': round(result[6], 2) if result[6] else 0
                })
            
            return {'success': True, 'analysis': analysis, 'winner': analysis[0] if analysis else None}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}

# Global A/B testing instance
ab_tester = ABTestingSystem()

# API Routes
@ab_testing.route('/ab-tests', methods=['GET'])
def get_ab_tests():
    """Get all A/B tests"""
    result = ab_tester.get_ab_tests()
    return jsonify(result)

@ab_testing.route('/ab-tests', methods=['POST'])
def create_ab_test():
    """Create new A/B test"""
    data = request.json
    result = ab_tester.create_ab_test(
        data.get('name'),
        data.get('description'),
        data.get('test_type', 'subject_line'),
        data.get('split_percentage', 50)
    )
    return jsonify(result)

@ab_testing.route('/ab-tests/<int:test_id>/variants', methods=['POST'])
def add_variant(test_id):
    """Add variant to A/B test"""
    data = request.json
    result = ab_tester.add_variant(
        test_id,
        data.get('variant_name'),
        data.get('subject_line'),
        data.get('message_content'),
        data.get('html_content'),
        data.get('from_name')
    )
    return jsonify(result)

@ab_testing.route('/ab-tests/<int:test_id>/select-variant', methods=['POST'])
def select_variant(test_id):
    """Select variant for recipient"""
    data = request.json
    email = data.get('email')
    result = ab_tester.select_variant_for_recipient(test_id, email)
    return jsonify(result)

@ab_testing.route('/ab-tests/<int:test_id>/record-send', methods=['POST'])
def record_send(test_id):
    """Record email send"""
    data = request.json
    result = ab_tester.record_send(test_id, data.get('variant_id'), data.get('email'))
    return jsonify(result)

@ab_testing.route('/ab-tests/<int:test_id>/analyze', methods=['GET'])
def analyze_results(test_id):
    """Analyze A/B test results"""
    result = ab_tester.analyze_test_results(test_id)
    return jsonify(result)