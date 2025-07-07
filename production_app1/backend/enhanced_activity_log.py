"""
Enhanced Activity Log - Combines Activity + Delivery Tracking
SAFE: Does not modify existing activity log functionality
"""
import sqlite3
from flask import Blueprint, request, jsonify

# Create blueprint
enhanced_activity = Blueprint('enhanced_activity', __name__)

class EnhancedActivityLog:
    def __init__(self):
        pass  # Uses existing tables, no new tables needed
    
    def get_combined_activity(self, limit=50):
        """Get combined activity and delivery data safely"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Get regular activity logs (existing functionality preserved)
            cursor.execute('''
                SELECT 'activity' as type, id, username, activity_type, description, 
                       ip_address, created_at, NULL as email, NULL as smtp_code, 
                       NULL as delivery_status, NULL as quality_score
                FROM user_activity 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit // 2,))
            
            activity_logs = cursor.fetchall()
            
            # Get delivery tracking data (if table exists)
            try:
                cursor.execute('''
                    SELECT 'delivery' as type, id, 'System' as username, 'email_delivery' as activity_type,
                           ('Email sent to ' || substr(email, 1, 3) || '***' || substr(email, -10)) as description,
                           NULL as ip_address, created_at, email, smtp_code, 
                           delivery_status, quality_score
                    FROM delivery_tracking 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit // 2,))
                
                delivery_logs = cursor.fetchall()
            except:
                delivery_logs = []  # Table doesn't exist yet, that's fine
            
            # Combine and sort by timestamp
            all_logs = list(activity_logs) + list(delivery_logs)
            all_logs.sort(key=lambda x: x[6], reverse=True)  # Sort by created_at
            all_logs = all_logs[:limit]  # Limit total results
            
            # Format results
            formatted_logs = []
            for log in all_logs:
                formatted_logs.append({
                    'type': log[0],
                    'id': log[1],
                    'username': log[2],
                    'activity_type': log[3],
                    'description': log[4],
                    'ip_address': log[5],
                    'created_at': log[6],
                    'email': log[7],
                    'smtp_code': log[8],
                    'delivery_status': log[9],
                    'quality_score': log[10]
                })
            
            conn.close()
            return {'success': True, 'logs': formatted_logs}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_delivery_summary(self):
        """Get delivery summary for activity dashboard"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Try to get delivery stats (safe if table doesn't exist)
            try:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_deliveries,
                        SUM(CASE WHEN delivery_status = 'delivered' THEN 1 ELSE 0 END) as successful,
                        SUM(CASE WHEN delivery_status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                        AVG(quality_score) as avg_quality,
                        COUNT(CASE WHEN created_at > datetime('now', '-24 hours') THEN 1 END) as last_24h
                    FROM delivery_tracking
                ''')
                
                result = cursor.fetchone()
                summary = {
                    'total_deliveries': result[0] or 0,
                    'successful': result[1] or 0,
                    'rejected': result[2] or 0,
                    'avg_quality': round(result[3] or 0, 1),
                    'last_24h': result[4] or 0
                }
            except:
                # Delivery tracking table doesn't exist yet
                summary = {
                    'total_deliveries': 0,
                    'successful': 0,
                    'rejected': 0,
                    'avg_quality': 0,
                    'last_24h': 0
                }
            
            conn.close()
            return {'success': True, 'summary': summary}
            
        except Exception as e:
            return {'success': False, 'message': str(e)}

# Global enhanced activity instance
enhanced_activity_log = EnhancedActivityLog()

# API Routes (new endpoints, don't modify existing ones)
@enhanced_activity.route('/enhanced-activity', methods=['GET'])
def get_enhanced_activity():
    """Get combined activity and delivery logs"""
    limit = request.args.get('limit', 50, type=int)
    result = enhanced_activity_log.get_combined_activity(limit)
    return jsonify(result)

@enhanced_activity.route('/delivery-summary', methods=['GET'])
def get_delivery_summary():
    """Get delivery summary for dashboard"""
    result = enhanced_activity_log.get_delivery_summary()
    return jsonify(result)