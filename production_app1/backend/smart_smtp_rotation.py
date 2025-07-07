"""
Smart SMTP Rotation - Intelligent Server Management
"""
import sqlite3
import time
import random
from flask import Blueprint, request, jsonify

# Create blueprint
smtp_rotation = Blueprint('smtp_rotation', __name__)

class SmartSMTPRotation:
    def __init__(self):
        self.init_rotation_tables()
    
    def init_rotation_tables(self):
        """Initialize SMTP rotation tables"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # SMTP server health tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS smtp_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    smtp_id INTEGER,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    last_success TIMESTAMP,
                    last_failure TIMESTAMP,
                    health_score REAL DEFAULT 100.0,
                    is_active BOOLEAN DEFAULT 1,
                    cooldown_until TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (smtp_id) REFERENCES smtp_servers (id)
                )
            ''')
            
            # SMTP usage tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS smtp_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    smtp_id INTEGER,
                    emails_sent_today INTEGER DEFAULT 0,
                    last_reset_date DATE DEFAULT CURRENT_DATE,
                    total_emails_sent INTEGER DEFAULT 0,
                    avg_response_time REAL DEFAULT 0.0,
                    FOREIGN KEY (smtp_id) REFERENCES smtp_servers (id)
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"SMTP rotation init error: {e}")
    
    def get_best_smtp_server(self, exclude_ids=None):
        """Get the best available SMTP server"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Build exclusion clause
            exclude_clause = ""
            params = []
            if exclude_ids:
                placeholders = ','.join(['?' for _ in exclude_ids])
                exclude_clause = f"AND s.id NOT IN ({placeholders})"
                params.extend(exclude_ids)
            
            # Get servers with health data
            query = f'''
                SELECT s.id, s.name, s.host, s.port, s.username, s.password, 
                       s.from_email, s.from_name, s.max_emails_per_day,
                       COALESCE(h.health_score, 100.0) as health_score,
                       COALESCE(h.is_active, 1) as is_active,
                       COALESCE(h.cooldown_until, '') as cooldown_until,
                       COALESCE(u.emails_sent_today, 0) as emails_sent_today
                FROM smtp_servers s
                LEFT JOIN smtp_health h ON s.id = h.smtp_id
                LEFT JOIN smtp_usage u ON s.id = u.smtp_id
                WHERE s.status = 'active' 
                AND COALESCE(h.is_active, 1) = 1
                AND (h.cooldown_until IS NULL OR h.cooldown_until < datetime('now'))
                AND COALESCE(u.emails_sent_today, 0) < s.max_emails_per_day
                {exclude_clause}
                ORDER BY health_score DESC, emails_sent_today ASC, RANDOM()
                LIMIT 1
            '''
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result:
                server = {
                    'id': result[0],
                    'name': result[1],
                    'host': result[2],
                    'port': result[3],
                    'username': result[4],
                    'password': result[5],
                    'from_email': result[6],
                    'from_name': result[7],
                    'max_emails_per_day': result[8],
                    'health_score': result[9],
                    'emails_sent_today': result[12]
                }
                
                conn.close()
                return {'success': True, 'server': server}
            else:
                conn.close()
                return {'success': False, 'message': 'No available SMTP servers'}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def record_smtp_success(self, smtp_id, response_time=0.0):
        """Record successful SMTP operation"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Update health
            cursor.execute('''
                INSERT OR REPLACE INTO smtp_health 
                (smtp_id, success_count, failure_count, last_success, health_score, is_active)
                VALUES (
                    ?, 
                    COALESCE((SELECT success_count FROM smtp_health WHERE smtp_id = ?), 0) + 1,
                    COALESCE((SELECT failure_count FROM smtp_health WHERE smtp_id = ?), 0),
                    datetime('now'),
                    MIN(100.0, COALESCE((SELECT health_score FROM smtp_health WHERE smtp_id = ?), 100.0) + 2.0),
                    1
                )
            ''', (smtp_id, smtp_id, smtp_id, smtp_id))
            
            # Update usage
            cursor.execute('''
                INSERT OR REPLACE INTO smtp_usage 
                (smtp_id, emails_sent_today, last_reset_date, total_emails_sent, avg_response_time)
                VALUES (
                    ?,
                    CASE 
                        WHEN COALESCE((SELECT last_reset_date FROM smtp_usage WHERE smtp_id = ?), CURRENT_DATE) = CURRENT_DATE
                        THEN COALESCE((SELECT emails_sent_today FROM smtp_usage WHERE smtp_id = ?), 0) + 1
                        ELSE 1
                    END,
                    CURRENT_DATE,
                    COALESCE((SELECT total_emails_sent FROM smtp_usage WHERE smtp_id = ?), 0) + 1,
                    (COALESCE((SELECT avg_response_time FROM smtp_usage WHERE smtp_id = ?), 0.0) + ?) / 2.0
                )
            ''', (smtp_id, smtp_id, smtp_id, smtp_id, smtp_id, response_time))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def record_smtp_failure(self, smtp_id, error_message=""):
        """Record failed SMTP operation"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            # Get current failure count
            cursor.execute('SELECT failure_count FROM smtp_health WHERE smtp_id = ?', (smtp_id,))
            result = cursor.fetchone()
            current_failures = result[0] if result else 0
            
            # Calculate new health score and cooldown
            new_health = max(0.0, 100.0 - (current_failures + 1) * 10.0)
            cooldown_until = None
            is_active = 1
            
            # If too many failures, set cooldown
            if current_failures >= 3:
                cooldown_minutes = min(60, (current_failures - 2) * 15)  # 15, 30, 45, 60 minutes max
                cursor.execute("SELECT datetime('now', '+{} minutes')".format(cooldown_minutes))
                cooldown_until = cursor.fetchone()[0]
                is_active = 0 if current_failures >= 5 else 1
            
            # Update health
            cursor.execute('''
                INSERT OR REPLACE INTO smtp_health 
                (smtp_id, success_count, failure_count, last_failure, health_score, is_active, cooldown_until)
                VALUES (
                    ?, 
                    COALESCE((SELECT success_count FROM smtp_health WHERE smtp_id = ?), 0),
                    COALESCE((SELECT failure_count FROM smtp_health WHERE smtp_id = ?), 0) + 1,
                    datetime('now'),
                    ?,
                    ?,
                    ?
                )
            ''', (smtp_id, smtp_id, smtp_id, new_health, is_active, cooldown_until))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'health_score': new_health, 'is_active': is_active}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_smtp_health_status(self):
        """Get health status of all SMTP servers"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.id, s.name, s.host, s.status,
                       COALESCE(h.health_score, 100.0) as health_score,
                       COALESCE(h.success_count, 0) as success_count,
                       COALESCE(h.failure_count, 0) as failure_count,
                       COALESCE(h.is_active, 1) as is_active,
                       h.cooldown_until,
                       COALESCE(u.emails_sent_today, 0) as emails_sent_today,
                       s.max_emails_per_day,
                       COALESCE(u.total_emails_sent, 0) as total_emails_sent
                FROM smtp_servers s
                LEFT JOIN smtp_health h ON s.id = h.smtp_id
                LEFT JOIN smtp_usage u ON s.id = u.smtp_id
                ORDER BY health_score DESC
            ''')
            
            servers = []
            for row in cursor.fetchall():
                servers.append({
                    'id': row[0],
                    'name': row[1],
                    'host': row[2],
                    'status': row[3],
                    'health_score': row[4],
                    'success_count': row[5],
                    'failure_count': row[6],
                    'is_active': bool(row[7]),
                    'cooldown_until': row[8],
                    'emails_sent_today': row[9],
                    'max_emails_per_day': row[10],
                    'total_emails_sent': row[11],
                    'usage_percentage': round((row[9] / row[10]) * 100, 1) if row[10] > 0 else 0
                })
            
            conn.close()
            return {'success': True, 'servers': servers}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def reset_daily_usage(self):
        """Reset daily usage counters (run daily)"""
        try:
            conn = sqlite3.connect('sender.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE smtp_usage 
                SET emails_sent_today = 0, last_reset_date = CURRENT_DATE
                WHERE last_reset_date < CURRENT_DATE
            ''')
            
            conn.commit()
            conn.close()
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'message': str(e)}

# Global SMTP rotation instance
smtp_rotator = SmartSMTPRotation()

# API Routes
@smtp_rotation.route('/smtp/best-server', methods=['GET'])
def get_best_server():
    """Get best available SMTP server"""
    exclude_ids = request.args.getlist('exclude', type=int)
    result = smtp_rotator.get_best_smtp_server(exclude_ids)
    return jsonify(result)

@smtp_rotation.route('/smtp/record-success', methods=['POST'])
def record_success():
    """Record SMTP success"""
    data = request.json
    result = smtp_rotator.record_smtp_success(
        data.get('smtp_id'),
        data.get('response_time', 0.0)
    )
    return jsonify(result)

@smtp_rotation.route('/smtp/record-failure', methods=['POST'])
def record_failure():
    """Record SMTP failure"""
    data = request.json
    result = smtp_rotator.record_smtp_failure(
        data.get('smtp_id'),
        data.get('error_message', '')
    )
    return jsonify(result)

@smtp_rotation.route('/smtp/health-status', methods=['GET'])
def get_health_status():
    """Get SMTP health status"""
    result = smtp_rotator.get_smtp_health_status()
    return jsonify(result)

@smtp_rotation.route('/smtp/reset-daily-usage', methods=['POST'])
def reset_daily_usage():
    """Reset daily usage counters"""
    result = smtp_rotator.reset_daily_usage()
    return jsonify(result)