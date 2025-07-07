"""
Smart Delivery Tracker - Advanced Email Delivery Analytics
"""
import sqlite3
import time
import random
import re
from flask import Blueprint, request, jsonify

# Create blueprint
delivery_tracker = Blueprint('delivery_tracker', __name__)

class SmartDeliveryTracker:
    def __init__(self):
        self.init_delivery_tables()
    
    def init_delivery_tables(self):
        """Initialize delivery tracking tables"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Create delivery tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS delivery_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER,
                    email TEXT,
                    smtp_server TEXT,
                    smtp_code INTEGER,
                    smtp_response TEXT,
                    delivery_status TEXT,
                    delivery_time REAL,
                    spam_likelihood TEXT,
                    inbox_likelihood TEXT,
                    quality_score INTEGER,
                    bounce_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Delivery tracker init error: {e}")
    
    def analyze_smtp_response(self, smtp_code, smtp_response):
        """Analyze SMTP response for delivery insights"""
        delivery_status = 'unknown'
        spam_likelihood = 'unknown'
        inbox_likelihood = 'uncertain'
        quality_score = 50
        
        # Analyze SMTP code
        if smtp_code == 250:
            delivery_status = 'delivered'
            quality_score = 85
            spam_likelihood = 'low'
            inbox_likelihood = 'likely_inbox'
        elif smtp_code in [550, 551, 552, 553, 554]:
            delivery_status = 'rejected'
            quality_score = 20
            spam_likelihood = 'high'
            inbox_likelihood = 'likely_spam'
        elif smtp_code in [421, 450, 451, 452]:
            delivery_status = 'deferred'
            quality_score = 60
            spam_likelihood = 'medium'
            inbox_likelihood = 'uncertain'
        
        # Analyze response text for spam indicators
        if smtp_response:
            response_lower = smtp_response.lower()
            spam_keywords = ['spam', 'blacklist', 'blocked', 'reputation', 'abuse']
            inbox_keywords = ['accepted', 'queued', 'delivered', 'ok']
            
            spam_count = sum(1 for keyword in spam_keywords if keyword in response_lower)
            inbox_count = sum(1 for keyword in inbox_keywords if keyword in response_lower)
            
            if spam_count > 0:
                spam_likelihood = 'high'
                inbox_likelihood = 'likely_spam'
                quality_score = max(10, quality_score - 30)
            elif inbox_count > 0:
                spam_likelihood = 'low'
                inbox_likelihood = 'high_inbox'
                quality_score = min(95, quality_score + 15)
        
        return {
            'delivery_status': delivery_status,
            'spam_likelihood': spam_likelihood,
            'inbox_likelihood': inbox_likelihood,
            'quality_score': quality_score
        }
    
    def track_delivery(self, campaign_id, email, smtp_server, smtp_code, smtp_response, delivery_time):
        """Track email delivery with smart analysis"""
        try:
            analysis = self.analyze_smtp_response(smtp_code, smtp_response)
            
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO delivery_tracking 
                (campaign_id, email, smtp_code, 
                 delivery_status, delivery_time, spam_likelihood, inbox_likelihood, quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                campaign_id, email, smtp_code,
                analysis['delivery_status'], delivery_time, analysis['spam_likelihood'],
                analysis['inbox_likelihood'], analysis['quality_score']
            ))
            
            conn.commit()
            conn.close()
            
            return analysis
            
        except Exception as e:
            print(f"Delivery tracking error: {e}")
            return None
    
    def get_delivery_stats(self):
        """Get comprehensive delivery statistics"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Get overall stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_sent,
                    SUM(CASE WHEN delivery_status = 'delivered' THEN 1 ELSE 0 END) as delivered,
                    SUM(CASE WHEN spam_likelihood = 'low' THEN 1 ELSE 0 END) as likely_inbox,
                    SUM(CASE WHEN spam_likelihood = 'high' THEN 1 ELSE 0 END) as likely_spam,
                    AVG(quality_score) as avg_quality_score,
                    AVG(delivery_time) as avg_delivery_time
                FROM delivery_tracking
            ''')
            
            stats = cursor.fetchone()
            
            # Get recent deliveries
            cursor.execute('''
                SELECT email, smtp_code, delivery_status, spam_likelihood, 
                       inbox_likelihood, quality_score, created_at
                FROM delivery_tracking 
                ORDER BY created_at DESC 
                LIMIT 20
            ''')
            
            recent_deliveries = cursor.fetchall()
            conn.close()
            
            return {
                'total_sent': stats[0] or 0,
                'delivered': stats[1] or 0,
                'likely_inbox': stats[2] or 0,
                'likely_spam': stats[3] or 0,
                'avg_quality_score': round(stats[4] or 0, 1),
                'avg_delivery_time': round(stats[5] or 0, 2),
                'recent_deliveries': recent_deliveries
            }
            
        except Exception as e:
            print(f"Get delivery stats error: {e}")
            return {
                'total_sent': 0, 'delivered': 0, 'likely_inbox': 0, 'likely_spam': 0,
                'avg_quality_score': 0, 'avg_delivery_time': 0, 'recent_deliveries': []
            }

# Global tracker instance
smart_tracker = SmartDeliveryTracker()

# API Routes
@delivery_tracker.route('/delivery-stats', methods=['GET'])
def get_delivery_stats():
    """Get delivery statistics"""
    stats = smart_tracker.get_delivery_stats()
    return jsonify({'success': True, 'data': stats})

@delivery_tracker.route('/track-delivery', methods=['POST'])
def track_delivery():
    """Track a delivery event"""
    data = request.json
    
    result = smart_tracker.track_delivery(
        data.get('campaign_id'),
        data.get('email'),
        data.get('smtp_server'),
        data.get('smtp_code'),
        data.get('smtp_response'),
        data.get('delivery_time')
    )
    
    if result:
        return jsonify({'success': True, 'analysis': result})
    else:
        return jsonify({'success': False, 'message': 'Tracking failed'})