"""
Enhanced Health API - Advanced system monitoring
"""
import os
import sqlite3
import smtplib
import ssl
import socket
import requests
import subprocess
from datetime import datetime
from flask import Blueprint, jsonify
from simple_db import query_db as simple_query_db

# Create blueprint
health_api = Blueprint('health_api', __name__)

def query_db(query, args=(), one=False):
    return simple_query_db(query, args, one, 'sender.db')

@health_api.route('/health', methods=['GET'])
def system_health():
    """Enhanced system health check"""
    try:
        health_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Database health
        health_data['checks']['database'] = check_database()
        
        # SMTP servers health
        health_data['checks']['smtp_servers'] = check_smtp_servers()
        
        # Proxy health
        health_data['checks']['proxies'] = check_proxies()
        
        # IP blacklist check
        health_data['checks']['ip_blacklist'] = check_ip_blacklist()
        
        # Mail queue status
        health_data['checks']['mail_queue'] = check_mail_queue()
        
        # System resources
        health_data['checks']['system_resources'] = check_system_resources()
        
        # Data counts
        health_data['checks']['data_counts'] = get_data_counts()
        
        # Debug: Print what we're returning
        print(f"Health checks returned: {list(health_data['checks'].keys())}")
        for key, value in health_data['checks'].items():
            print(f"{key}: {value.get('status', 'no status')} - {value.get('message', 'no message')}")
        
        # Determine overall status
        failed_checks = [k for k, v in health_data['checks'].items() 
                        if v.get('status') == 'error']
        warning_checks = [k for k, v in health_data['checks'].items() 
                         if v.get('status') == 'warning']
        
        if failed_checks:
            health_data['overall_status'] = 'degraded' if len(failed_checks) < 3 else 'unhealthy'
        elif warning_checks:
            health_data['overall_status'] = 'degraded'
        
        return jsonify({'success': True, 'data': health_data})
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Health check failed: {str(e)}'
        }), 500

def check_database():
    """Check database connectivity and tables"""
    try:
        # Test database connection
        servers = query_db('SELECT COUNT(*) as count FROM smtp_servers')
        
        # Check all required tables
        tables = ['smtp_servers', 'proxies', 'campaigns', 'lists', 'contacts']
        table_status = {}
        
        for table in tables:
            try:
                result = query_db(f'SELECT COUNT(*) as count FROM {table}')
                table_status[table] = result[0]['count'] if result else 0
            except:
                table_status[table] = 'ERROR'
        
        return {
            'status': 'healthy',
            'message': 'Database connection successful',
            'tables': table_status
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }

def check_smtp_servers():
    """Test all SMTP servers connectivity"""
    try:
        servers = query_db('SELECT * FROM smtp_servers')
        if not servers:
            return {
                'status': 'warning',
                'message': 'No SMTP servers configured',
                'servers': [],
                'summary': {
                    'total': 0,
                    'healthy': 0,
                    'unhealthy': 0
                }
            }
        
        server_status = []
        healthy_count = 0
        
        for server in servers:
            status = test_smtp_server(server)
            server_status.append({
                'id': server['id'],
                'name': server['name'],
                'host': server['host'],
                'port': server['port'],
                'status': status['status'],
                'message': status['message'],
                'response_time': status.get('response_time', 0)
            })
            
            if status['status'] == 'healthy':
                healthy_count += 1
        
        overall_status = 'healthy' if healthy_count == len(servers) else \
                        'warning' if healthy_count > 0 else 'error'
        
        return {
            'status': overall_status,
            'message': f'{healthy_count}/{len(servers)} SMTP servers healthy',
            'servers': server_status,
            'summary': {
                'total': len(servers),
                'healthy': healthy_count,
                'unhealthy': len(servers) - healthy_count
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'SMTP check failed: {str(e)}'
        }

def test_smtp_server(server):
    """Test individual SMTP server"""
    try:
        import time
        start_time = time.time()
        
        context = ssl.create_default_context()
        
        if int(server['port']) == 465:
            # SSL connection
            with smtplib.SMTP_SSL(server['host'], server['port'], context=context, timeout=10) as smtp:
                smtp.ehlo()
                if server.get('require_auth', True) and server.get('username'):
                    smtp.login(server['username'], server['password'])
        else:
            # STARTTLS connection
            with smtplib.SMTP(server['host'], server['port'], timeout=10) as smtp:
                smtp.ehlo()
                if smtp.has_extn('STARTTLS'):
                    smtp.starttls(context=context)
                    smtp.ehlo()
                if server.get('require_auth', True) and server.get('username'):
                    smtp.login(server['username'], server['password'])
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'status': 'healthy',
            'message': 'Connection successful',
            'response_time': response_time
        }
    except smtplib.SMTPAuthenticationError:
        return {
            'status': 'error',
            'message': 'Authentication failed'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Connection failed: {str(e)}'
        }

def check_proxies():
    """Test proxy connectivity"""
    try:
        proxies = query_db('SELECT * FROM proxies')
        if not proxies:
            return {
                'status': 'warning',
                'message': 'No proxies configured',
                'proxies': [],
                'summary': {
                    'total': 0,
                    'healthy': 0,
                    'unhealthy': 0
                }
            }
        
        proxy_status = []
        healthy_count = 0
        
        for proxy in proxies:
            status = test_proxy(proxy)
            proxy_status.append({
                'id': proxy['id'],
                'host': proxy['host'],
                'port': proxy['port'],
                'type': proxy['proxy_type'],
                'status': status['status'],
                'message': status['message']
            })
            
            if status['status'] == 'healthy':
                healthy_count += 1
        
        overall_status = 'healthy' if healthy_count == len(proxies) else \
                        'warning' if healthy_count > 0 else 'error'
        
        return {
            'status': overall_status,
            'message': f'{healthy_count}/{len(proxies)} proxies healthy',
            'proxies': proxy_status,
            'summary': {
                'total': len(proxies),
                'healthy': healthy_count,
                'unhealthy': len(proxies) - healthy_count
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Proxy check failed: {str(e)}'
        }

def test_proxy(proxy):
    """Test individual proxy"""
    try:
        # Simple socket connection test
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((proxy['host'], proxy['port']))
        sock.close()
        
        if result == 0:
            return {
                'status': 'healthy',
                'message': 'Connection successful'
            }
        else:
            return {
                'status': 'error',
                'message': 'Connection failed'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Test failed: {str(e)}'
        }

def check_ip_blacklist():
    """Check if server IP is blacklisted"""
    try:
        # Get server's public IP
        try:
            response = requests.get('https://api.ipify.org', timeout=10)
            server_ip = response.text.strip()
        except:
            return {
                'status': 'warning',
                'message': 'Could not determine server IP'
            }
        
        # Check major blacklists
        blacklists = [
            'zen.spamhaus.org',
            'bl.spamcop.net',
            'dnsbl.sorbs.net',
            'uceprotect.net'
        ]
        
        blacklisted = []
        for bl in blacklists:
            if check_blacklist(server_ip, bl):
                blacklisted.append(bl)
        
        if blacklisted:
            return {
                'status': 'error',
                'message': f'IP {server_ip} blacklisted on: {", ".join(blacklisted)}',
                'server_ip': server_ip,
                'blacklisted_on': blacklisted
            }
        else:
            return {
                'status': 'healthy',
                'message': f'IP {server_ip} not blacklisted',
                'server_ip': server_ip,
                'blacklisted_on': []
            }
    except Exception as e:
        return {
            'status': 'warning',
            'message': f'Blacklist check failed: {str(e)}'
        }

def check_blacklist(ip, blacklist):
    """Check if IP is on specific blacklist"""
    try:
        reversed_ip = '.'.join(reversed(ip.split('.')))
        query = f"{reversed_ip}.{blacklist}"
        socket.gethostbyname(query)
        return True
    except socket.gaierror:
        return False

def check_mail_queue():
    """Check mail queue status"""
    try:
        result = subprocess.run(['mailq'], capture_output=True, text=True, timeout=10)
        output = result.stdout
        
        if 'Mail queue is empty' in output or 'postqueue: warning' in output:
            return {
                'status': 'healthy',
                'message': 'Mail queue is empty',
                'queue_size': 0
            }
        else:
            # Count queued emails
            lines = output.split('\n')
            queue_count = 0
            for line in lines:
                if 'Kbytes in' in line or 'Requests' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'Requests' in part and i > 0:
                            try:
                                queue_count = int(parts[i-1])
                            except:
                                queue_count = 0
                            break
            
            status = 'warning' if queue_count > 10 else 'healthy'
            return {
                'status': status,
                'message': f'{queue_count} emails in queue',
                'queue_size': queue_count
            }
    except Exception as e:
        return {
            'status': 'warning',
            'message': f'Mail queue check not available on this system'
        }

def check_system_resources():
    """Check system resources"""
    try:
        # Disk space (works on both Linux and macOS)
        disk_result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        disk_lines = disk_result.stdout.split('\n')
        disk_usage = '0'
        if len(disk_lines) > 1:
            disk_info = disk_lines[1].split()
            if len(disk_info) > 4:
                disk_usage = disk_info[4].replace('%', '')
        
        # Memory (try different commands for different systems)
        mem_usage = 0
        try:
            # Try macOS command first
            mem_result = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=5)
            if mem_result.returncode == 0:
                # Parse macOS vm_stat output
                lines = mem_result.stdout.split('\n')
                page_size = 4096  # Default page size
                free_pages = 0
                total_pages = 0
                
                for line in lines:
                    if 'page size of' in line:
                        page_size = int(line.split()[-2])
                    elif 'Pages free:' in line:
                        free_pages = int(line.split()[-1].replace('.', ''))
                    elif 'Pages active:' in line:
                        total_pages += int(line.split()[-1].replace('.', ''))
                    elif 'Pages inactive:' in line:
                        total_pages += int(line.split()[-1].replace('.', ''))
                    elif 'Pages wired down:' in line:
                        total_pages += int(line.split()[-1].replace('.', ''))
                
                if total_pages > 0:
                    mem_usage = round(((total_pages - free_pages) / total_pages) * 100, 1)
        except:
            # Try Linux command
            try:
                mem_result = subprocess.run(['free', '-m'], capture_output=True, text=True, timeout=5)
                if mem_result.returncode == 0:
                    mem_lines = mem_result.stdout.split('\n')
                    if len(mem_lines) > 1:
                        mem_info = mem_lines[1].split()
                        if len(mem_info) > 2:
                            total_mem = int(mem_info[1])
                            used_mem = int(mem_info[2])
                            mem_usage = round((used_mem / total_mem) * 100, 1) if total_mem > 0 else 0
            except:
                mem_usage = 0
        
        disk_status = 'error' if int(disk_usage) > 90 else 'warning' if int(disk_usage) > 80 else 'healthy'
        mem_status = 'error' if mem_usage > 90 else 'warning' if mem_usage > 80 else 'healthy'
        
        overall_status = 'error' if disk_status == 'error' or mem_status == 'error' else \
                        'warning' if disk_status == 'warning' or mem_status == 'warning' else 'healthy'
        
        return {
            'status': overall_status,
            'message': f'Disk: {disk_usage}%, Memory: {mem_usage}%',
            'disk_usage': f'{disk_usage}%',
            'memory_usage': f'{mem_usage}%'
        }
    except Exception as e:
        return {
            'status': 'warning',
            'message': f'System monitoring not available on this platform'
        }

def get_data_counts():
    """Get data counts for dashboard"""
    try:
        counts = {}
        tables = ['campaigns', 'lists', 'contacts', 'smtp_servers', 'proxies']
        
        for table in tables:
            try:
                result = query_db(f'SELECT COUNT(*) as count FROM {table}')
                counts[table] = result[0]['count'] if result else 0
            except Exception as table_error:
                print(f"Error counting {table}: {table_error}")
                counts[table] = 0
        
        print(f"Data counts: {counts}")
        
        return {
            'status': 'healthy',
            'message': 'Data counts retrieved',
            'counts': counts
        }
    except Exception as e:
        print(f"Data counts error: {e}")
        return {
            'status': 'warning',
            'message': f'Count check failed: {str(e)}',
            'counts': {}
        }