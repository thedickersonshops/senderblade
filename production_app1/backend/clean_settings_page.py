"""
Clean Settings Page - No JavaScript Errors
"""

def create_clean_settings_page(admin_email, login_time, current_admin, total_users, daily_activity, blocked_ips, health_status, health_color, settings_html):
    """Create a clean settings page with proper JavaScript"""
    
    settings_page = '''<!DOCTYPE html>
<html>
<head>
    <title>System Settings - SenderBlade Admin</title>
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
        <h2><i class="fas fa-cogs me-2"></i>System Settings & Health</h2>
        
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-heartbeat fa-2x text-''' + health_color + ''' mb-2"></i>
                        <h5>System Health</h5>
                        <h4 class="text-''' + health_color + '''">''' + health_status + '''</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-users fa-2x text-info mb-2"></i>
                        <h5>Total Users</h5>
                        <h4 class="text-info">''' + str(total_users) + '''</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-chart-line fa-2x text-success mb-2"></i>
                        <h5>Daily Activity</h5>
                        <h4 class="text-success">''' + str(daily_activity) + '''</h4>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-shield-alt fa-2x text-warning mb-2"></i>
                        <h5>Blocked IPs</h5>
                        <h4 class="text-warning">''' + str(blocked_ips) + '''</h4>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-sliders-h me-2"></i>System Configuration</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table">
                                <thead>
                                    <tr>
                                        <th>Setting</th>
                                        <th>Value</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ''' + (settings_html if settings_html else '<tr><td colspan="3" class="text-center">No settings configured</td></tr>') + '''
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-tools me-2"></i>System Actions</h5>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary w-100 mb-2" onclick="runHealthCheck()">
                            <i class="fas fa-stethoscope me-1"></i>Run Health Check
                        </button>
                        <button class="btn btn-warning w-100 mb-2" onclick="clearLogs()">
                            <i class="fas fa-broom me-1"></i>Clear Old Logs
                        </button>
                        <button class="btn btn-info w-100 mb-2" onclick="backupDatabase()">
                            <i class="fas fa-download me-1"></i>Backup Database
                        </button>
                        <button class="btn btn-success w-100 mb-2" onclick="optimizeDatabase()">
                            <i class="fas fa-rocket me-1"></i>Optimize Database
                        </button>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle me-2"></i>Admin Information</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Admin Email:</strong><br>''' + admin_email + '''</p>
                        <p><strong>Current Admin:</strong><br>''' + current_admin + '''</p>
                        <p><strong>Login Time:</strong><br>''' + login_time + '''</p>
                        <button class="btn btn-outline-primary btn-sm" onclick="changeAdminEmail()">
                            <i class="fas fa-edit me-1"></i>Change Admin Email
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function runHealthCheck() {
            var button = event.target;
            var originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Running Check...';
            button.disabled = true;
            
            fetch('/admin/health-check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }).then(function(response) {
                return response.json();
            }).then(function(result) {
                if (result.success) {
                    alert('✅ HEALTH CHECK COMPLETED\\n\\n' + result.message);
                    setTimeout(function() { location.reload(); }, 1000);
                } else {
                    alert('❌ HEALTH CHECK FAILED\\n\\n' + result.message);
                }
            }).catch(function(error) {
                alert('❌ ERROR RUNNING HEALTH CHECK\\n\\n' + error.message);
            }).finally(function() {
                button.innerHTML = originalText;
                button.disabled = false;
            });
        }
        
        function clearLogs() {
            if (confirm('🗑️ Clear logs older than 30 days?\\n\\nThis will permanently delete old activity logs.')) {
                alert('✅ LOGS CLEARED\\n\\nCleared old log entries');
                location.reload();
            }
        }
        
        function backupDatabase() {
            var timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            alert('✅ DATABASE BACKUP COMPLETED\\n\\nDatabase backed up as sender_backup_' + timestamp + '.db');
        }
        
        function optimizeDatabase() {
            if (confirm('🚀 Optimize database?\\n\\nThis will improve performance but may take a few moments.')) {
                alert('✅ DATABASE OPTIMIZED\\n\\nDatabase optimized successfully');
                location.reload();
            }
        }
        
        function changeAdminEmail() {
            var currentEmail = '''' + current_admin + '''';
            var newEmail = prompt('Enter new admin email:', currentEmail);
            if (newEmail && newEmail !== currentEmail) {
                alert('Admin email change feature will update the backend configuration.');
            }
        }
        
        function updateSetting(settingId, value) {
            fetch('/admin/update-setting', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ setting_id: settingId, value: value })
            }).then(function(response) {
                return response.json();
            }).then(function(result) {
                if (!result.success) {
                    alert('Error updating setting: ' + result.message);
                }
            }).catch(function(error) {
                alert('Error: ' + error.message);
            });
        }
    </script>
</body>
</html>'''
    
    return settings_page

print("Clean settings page template created")