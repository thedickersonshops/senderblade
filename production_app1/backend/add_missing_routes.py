"""
Add missing routes to complete admin system
This will be appended to the main file
"""

# User Management Routes
@app.route('/admin/users')
def admin_users():
    if 'admin_email' not in session:
        return redirect('/admin/login')
    
    try:
        result = enterprise_auth.get_all_users(1)
        users = result.get('users', []) if result['success'] else []
    except:
        users = []
    
    users_html = ""
    for user in users:
        status_badge = {
            'pending': 'warning',
            'approved': 'success', 
            'blocked': 'danger',
            'suspended': 'secondary'
        }.get(user.get('status', 'pending'), 'secondary')
        
        user_id = user.get('id', 0)
        username = user.get('username', 'N/A')
        email = user.get('email', 'N/A')
        status = user.get('status', 'unknown')
        created_at = user.get('created_at', 'N/A')
        
        users_html += f'''
        <tr>
            <td>{user_id}</td>
            <td>{username}</td>
            <td>{email}</td>
            <td><span class="badge bg-{status_badge}">{status}</span></td>
            <td>{created_at}</td>
            <td>
                <button class="btn btn-success btn-sm" onclick="approveUser({user_id})">
                    <i class="fas fa-check"></i> Approve
                </button>
                <button class="btn btn-warning btn-sm" onclick="blockUser({user_id})">
                    <i class="fas fa-ban"></i> Block
                </button>
                <button class="btn btn-danger btn-sm" onclick="deleteUser({user_id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </td>
        </tr>
        '''
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <title>User Management - SenderBlade Admin</title>
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
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2><i class="fas fa-users me-2"></i>User Management</h2>
            <button class="btn btn-primary" onclick="createTestUser()">
                <i class="fas fa-plus me-1"></i>Create Test User
            </button>
        </div>
        
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Status</th>
                                <th>Created</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users_html if users_html else '<tr><td colspan="6" class="text-center">No users found</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function approveUser(userId) {{
            if (confirm('Approve this user?')) {{
                fetch('/admin/approve-user/' + userId, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }}
                }}).then(function(response) {{
                    return response.json();
                }}).then(function(result) {{
                    if (result.success) {{
                        alert('User approved successfully');
                        location.reload();
                    }} else {{
                        alert('Error: ' + result.message);
                    }}
                }}).catch(function(error) {{
                    alert('Error: ' + error.message);
                }});
            }}
        }}
        
        function blockUser(userId) {{
            var reason = prompt('Reason for blocking:');
            if (reason) {{
                fetch('/admin/block-user/' + userId, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ reason: reason }})
                }}).then(function(response) {{
                    return response.json();
                }}).then(function(result) {{
                    if (result.success) {{
                        alert('User blocked successfully');
                        location.reload();
                    }} else {{
                        alert('Error: ' + result.message);
                    }}
                }}).catch(function(error) {{
                    alert('Error: ' + error.message);
                }});
            }}
        }}
        
        function deleteUser(userId) {{
            if (confirm('DELETE this user permanently? This cannot be undone!')) {{
                fetch('/admin/delete-user/' + userId, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }}
                }}).then(function(response) {{
                    return response.json();
                }}).then(function(result) {{
                    if (result.success) {{
                        alert('User deleted successfully');
                        location.reload();
                    }} else {{
                        alert('Error: ' + result.message);
                    }}
                }}).catch(function(error) {{
                    alert('Error: ' + error.message);
                }});
            }}
        }}
        
        function createTestUser() {{
            if (confirm('Create a test user for demonstration?')) {{
                fetch('/admin/create-test-user', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }}
                }}).then(function(response) {{
                    return response.json();
                }}).then(function(result) {{
                    if (result.success) {{
                        alert('Test user created successfully!');
                        location.reload();
                    }} else {{
                        alert('Error: ' + result.message);
                    }}
                }}).catch(function(error) {{
                    alert('Error: ' + error.message);
                }});
            }}
        }}
    </script>
</body>
</html>
    '''

# User Management Actions
@app.route('/admin/approve-user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    if 'admin_email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    try:
        result = enterprise_auth.approve_user(1, user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/block-user/<int:user_id>', methods=['POST'])
def block_user(user_id):
    if 'admin_email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Blocked by admin')
        result = enterprise_auth.block_user(1, user_id, reason)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'admin_email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    try:
        result = enterprise_auth.delete_user(1, user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/create-test-user', methods=['POST'])
def create_test_user():
    if 'admin_email' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    try:
        import random
        test_id = random.randint(1000, 9999)
        result = enterprise_auth.register_user(
            username=f'testuser{test_id}',
            email=f'test{test_id}@example.com',
            password='testpass123',
            full_name=f'Test User {test_id}',
            phone=f'555-{test_id}'
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

print("Missing routes defined - ready to append to main file")