"""
Real validation for SMTP and proxies
"""
import smtplib
import ssl
import socket
import requests
import socks
from flask import Blueprint, request, jsonify

# Create blueprint
validation_api = Blueprint('validation_api', __name__)

@validation_api.route('/api/smtp/real-test', methods=['POST'])
def test_smtp_real():
    data = request.json
    host = data.get('host')
    port = data.get('port')
    username = data.get('username')
    password = data.get('password')
    
    if not host or not port or not username or not password:
        return jsonify({'success': False, 'message': 'Host, port, username, and password are required'}), 400
    
    try:
        # Create a secure SSL context
        context = ssl.create_default_context()
        
        # Try to connect to the SMTP server
        with smtplib.SMTP(host, int(port), timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(username, password)
        
        return jsonify({
            'success': True,
            'data': {
                'status': 'success',
                'message': 'SMTP connection successful'
            }
        })
    except smtplib.SMTPAuthenticationError:
        return jsonify({'success': False, 'message': 'SMTP authentication failed: Invalid username or password'}), 400
    except smtplib.SMTPConnectError:
        return jsonify({'success': False, 'message': 'SMTP connection failed: Unable to connect to server'}), 400
    except smtplib.SMTPServerDisconnected:
        return jsonify({'success': False, 'message': 'SMTP server disconnected'}), 400
    except smtplib.SMTPException as e:
        return jsonify({'success': False, 'message': f'SMTP error: {str(e)}'}), 400
    except socket.gaierror:
        return jsonify({'success': False, 'message': 'SMTP error: Invalid hostname'}), 400
    except socket.timeout:
        return jsonify({'success': False, 'message': 'SMTP error: Connection timed out'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'SMTP error: {str(e)}'}), 400

@validation_api.route('/api/proxy/real-test', methods=['POST'])
def test_proxy_real():
    data = request.json
    host = data.get('host')
    port = data.get('port')
    username = data.get('username', '')
    password = data.get('password', '')
    proxy_type = data.get('proxy_type', 'http')
    
    if not host or not port:
        return jsonify({'success': False, 'message': 'Host and port are required'}), 400
    
    try:
        # Set up proxy
        proxy_url = f"{proxy_type}://"
        if username and password:
            proxy_url += f"{username}:{password}@"
        proxy_url += f"{host}:{port}"
        
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        # Test connection with a request to ipinfo.io
        response = requests.get('https://ipinfo.io/json', proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            ip = data.get('ip', 'Unknown')
            
            return jsonify({
                'success': True,
                'data': {
                    'status': 'success',
                    'message': 'Proxy connection successful',
                    'ip': ip
                }
            })
        else:
            return jsonify({'success': False, 'message': f'Proxy connection failed: HTTP {response.status_code}'}), 400
    except requests.exceptions.ProxyError:
        return jsonify({'success': False, 'message': 'Proxy error: Invalid proxy or authentication failed'}), 400
    except requests.exceptions.ConnectTimeout:
        return jsonify({'success': False, 'message': 'Proxy error: Connection timed out'}), 400
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'message': 'Proxy error: Connection refused'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Proxy error: {str(e)}'}), 400