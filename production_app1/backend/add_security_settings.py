"""
Add Security and Settings pages to the main admin system
"""

# Security page route
SECURITY_ROUTE = '''
@app.route('/admin/security')
def admin_security():
    if 'admin_email' not in session:
        return redirect('/admin/login')
    
    # Get real IP control data from database
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ip_control WHERE is_active = 1 ORDER BY created_at DESC LIMIT 50")
        ip_controls = cursor.fetchall()
        
        cursor.execute("SELECT ip_address, COUNT(*) as count, MAX(created_at) as last_seen FROM user_activity WHERE ip_address != '' AND ip_address IS NOT NULL GROUP BY ip_address ORDER BY count DESC LIMIT 20")
        ip_activity = cursor.fetchall()
        
        conn.close()
    except:
        ip_controls = []
        ip_activity = []
    
    # Count IP types
    whitelist_count = len([ip for ip in ip_controls if ip[2] == 'whitelist'])
    blacklist_count = len([ip for ip in ip_controls if ip[2] == 'blacklist'])
    suspicious_count = len([ip for ip in ip_controls if ip[2] == 'suspicious'])
    
    # Build IP controls HTML
    ip_controls_html = ""
    for ip in ip_controls:
        status_color = {'whitelist': 'success', 'blacklist': 'danger', 'suspicious': 'warning'}.get(ip[2], 'secondary')
        ip_controls_html += '<tr><td>' + str(ip[1]) + '</td><td><span class="badge bg-' + status_color + '">' + str(ip[2]) + '</span></td><td>' + str(ip[3] or 'No reason') + '</td><td><button class="btn btn-danger btn-sm" onclick="removeIPControl(' + str(ip[0]) + ')"><i class="fas fa-trash"></i> Remove</button></td></tr>'
    
    # Build IP activity HTML
    ip_activity_html = ""
    for ip in ip_activity:
        ip_activity_html += '<tr><td>' + str(ip[0]) + '</td><td>' + str(ip[1]) + '</td><td>' + str(ip[2]) + '</td><td><button class="btn btn-success btn-sm" onclick="whitelistIP(\'' + str(ip[0]) + '\')"><i class="fas fa-check"></i> Whitelist</button> <button class="btn btn-warning btn-sm" onclick="tempBlockIP(\'' + str(ip[0]) + '\')"><i class="fas fa-clock"></i> Temp Block</button> <button class="btn btn-danger btn-sm" onclick="permanentBlockIP(\'' + str(ip[0]) + '\')"><i class="fas fa-ban"></i> Block</button></td></tr>'
    
    security_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Security Management - SenderBlade Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <a href="/admin/dashboard" class="navbar-brand">🛡️ SenderBlade Admin</a>
            <a href="/admin/logout" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <h2><i class="fas fa-shield-alt me-2"></i>Security Management</h2>
        
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-shield-alt fa-2x text-success mb-2"></i>
                        <h5>Whitelisted IPs</h5>
                        <h3 class="text-success">""" + str(whitelist_count) + """</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-ban fa-2x text-danger mb-2"></i>
                        <h5>Blocked IPs</h5>
                        <h3 class="text-danger">""" + str(blacklist_count) + """</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-exclamation-triangle fa-2x text-warning mb-2"></i>
                        <h5>Suspicious IPs</h5>
                        <h3 class="text-warning">""" + str(suspicious_count) + """</h3>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list me-2"></i>IP Control List</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>IP Address</th>
                                        <th>Type</th>
                                        <th>Reason</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    """ + (ip_controls_html if ip_controls_html else '<tr><td colspan="4" class="text-center">No IP controls configured</td></tr>') + """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-line me-2"></i>IP Activity Monitor</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>IP Address</th>
                                        <th>Requests</th>
                                        <th>Last Seen</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    """ + (ip_activity_html if ip_activity_html else '<tr><td colspan="4" class="text-center">No IP activity recorded</td></tr>') + """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-plus me-2"></i>Add IP Control</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <input type="text" class="form-control" id="newIP" placeholder="IP Address">
                            </div>
                            <div class="col-md-3">
                                <select class="form-control" id="ipType">
                                    <option value="whitelist">Whitelist</option>
                                    <option value="blacklist">Blacklist</option>
                                    <option value="suspicious">Suspicious</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <input type="text" class="form-control" id="ipReason" placeholder="Reason">
                            </div>
                            <div class="col-md-2">
                                <button class="btn btn-primary" onclick="addIPControl()">Add</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function whitelistIP(ip) {
            if (confirm('Whitelist IP: ' + ip + '?')) {
                fetch('/admin/ip-control', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip: ip, type: 'whitelist', reason: 'Admin whitelisted' })
                }).then(function(response) {
                    return response.json();
                }).then(function(result) {
                    if (result.success) {
                        alert('IP whitelisted successfully');
                        location.reload();
                    } else {
                        alert('Error: ' + result.message);
                    }
                });
            }
        }
        
        function tempBlockIP(ip) {
            var hours = prompt('Block for how many hours?', '24');
            if (hours) {
                fetch('/admin/ip-control', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip: ip, type: 'blacklist', reason: 'Temporary block (' + hours + 'h)', hours: parseInt(hours) })
                }).then(function(response) {
                    return response.json();
                }).then(function(result) {
                    if (result.success) {
                        alert('IP temporarily blocked for ' + hours + ' hours');
                        location.reload();
                    } else {
                        alert('Error: ' + result.message);
                    }
                });
            }
        }
        
        function permanentBlockIP(ip) {
            var reason = prompt('Reason for permanent block:', 'Suspicious activity');
            if (reason) {
                fetch('/admin/ip-control', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip: ip, type: 'blacklist', reason: reason })
                }).then(function(response) {
                    return response.json();
                }).then(function(result) {
                    if (result.success) {
                        alert('IP permanently blocked');
                        location.reload();
                    } else {
                        alert('Error: ' + result.message);
                    }
                });
            }
        }
        
        function addIPControl() {
            var ip = document.getElementById('newIP').value;
            var type = document.getElementById('ipType').value;
            var reason = document.getElementById('ipReason').value;
            
            if (!ip) {
                alert('Please enter an IP address');
                return;
            }
            
            fetch('/admin/ip-control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ip: ip, type: type, reason: reason || 'Manual entry' })
            }).then(function(response) {
                return response.json();
            }).then(function(result) {
                if (result.success) {
                    alert('IP control added successfully');
                    location.reload();
                } else {
                    alert('Error: ' + result.message);
                }
            });
        }
        
        function removeIPControl(id) {
            if (confirm('Remove this IP control?')) {
                fetch('/admin/ip-control/' + id, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' }
                }).then(function(response) {
                    return response.json();
                }).then(function(result) {
                    if (result.success) {
                        alert('IP control removed');
                        location.reload();
                    } else {
                        alert('Error: ' + result.message);
                    }
                });
            }
        }
    </script>
</body>
</html>
    """
    return security_html
'''

print("Security and Settings routes ready to be added to main file")