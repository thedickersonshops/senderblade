"""
Template Manager - Professional Template Management System
Protecting all existing functionality while adding management features
"""
from flask import Blueprint, request, jsonify
import sqlite3

template_manager = Blueprint('template_manager', __name__)

def query_db(query, args=(), one=False):
    """Query database and return results"""
    try:
        conn = sqlite3.connect('sender.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, args)
        
        if one:
            result = cursor.fetchone()
            conn.close()
            return dict(result) if result else None
        else:
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
    except Exception as e:
        print(f"Database query error: {e}")
        return None if one else []

def execute_db(query, args=()):
    """Execute database query and return last row id"""
    try:
        conn = sqlite3.connect('sender.db')
        cursor = conn.cursor()
        cursor.execute(query, args)
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return last_id
    except Exception as e:
        print(f"Database execute error: {e}")
        return None

@template_manager.route('/templates/manage', methods=['GET'])
def get_template_management():
    """Get template management page"""
    try:
        templates = query_db('SELECT * FROM spinner_templates ORDER BY created_at DESC')
        
        html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Template Management - SenderBlade</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .template-card {
            transition: transform 0.2s;
            cursor: pointer;
            position: relative;
        }
        .template-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .template-actions {
            position: absolute;
            top: 10px;
            right: 10px;
            opacity: 0;
            transition: opacity 0.2s;
        }
        .template-card:hover .template-actions {
            opacity: 1;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <a href="/" class="navbar-brand">🎨 Template Management</a>
            <a href="/" class="btn btn-outline-light btn-sm">Back to SenderBlade</a>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2><i class="fas fa-file-alt me-2"></i>Template Management</h2>
                    <div>
                        <button class="btn btn-warning me-2" onclick="cleanupDuplicates()">
                            <i class="fas fa-broom me-1"></i>Clean Duplicates
                        </button>
                        <button class="btn btn-primary" onclick="showCreateModal()">
                            <i class="fas fa-plus me-1"></i>Create New Template
                        </button>
                    </div>
                </div>
                
                <div class="row" id="templateContainer">
        '''
        
        if templates:
            for template in templates:
                html += f'''
                    <div class="col-md-4 mb-4">
                        <div class="card template-card h-100">
                            <div class="template-actions">
                                <button class="btn btn-sm btn-outline-primary me-1" onclick="editTemplate({template['id']})" title="Edit">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-warning me-1" onclick="renameTemplate({template['id']})" title="Rename">
                                    <i class="fas fa-tag"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteTemplate({template['id']})" title="Delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                            <div class="card-body">
                                <h5 class="card-title">{template['name']}</h5>
                                <p class="card-text text-muted small">{template.get('description', 'No description')}</p>
                                <div class="mb-2">
                                    <small class="text-muted">
                                        <strong>Subject:</strong> {template.get('subject', 'No subject')[:50]}{'...' if len(template.get('subject', '')) > 50 else ''}
                                    </small>
                                </div>
                                <div class="mb-2">
                                    <small class="text-muted">
                                        <strong>Content:</strong> {template['content'][:100]}{'...' if len(template['content']) > 100 else ''}
                                    </small>
                                </div>
                                <small class="text-muted">Created: {template['created_at']}</small>
                            </div>
                            <div class="card-footer">
                                <button class="btn btn-success btn-sm" onclick="useTemplate({template['id']})">
                                    <i class="fas fa-paper-plane me-1"></i>Use in Campaign
                                </button>
                                <button class="btn btn-info btn-sm" onclick="previewTemplate({template['id']})">
                                    <i class="fas fa-eye me-1"></i>Preview
                                </button>
                            </div>
                        </div>
                    </div>
                '''
        else:
            html += '''
                    <div class="col-12">
                        <div class="alert alert-info text-center">
                            <h4><i class="fas fa-file-alt fa-3x mb-3"></i></h4>
                            <h5>No Templates Found</h5>
                            <p>Create your first template to get started with professional email campaigns.</p>
                            <button class="btn btn-primary" onclick="showCreateModal()">
                                <i class="fas fa-plus me-1"></i>Create First Template
                            </button>
                        </div>
                    </div>
            '''
        
        html += '''
                </div>
            </div>
        </div>
    </div>
    
    <!-- Create/Edit Template Modal -->
    <div class="modal fade" id="templateModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="modalTitle">Create New Template</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="templateForm">
                        <input type="hidden" id="templateId" value="">
                        <div class="mb-3">
                            <label class="form-label">Template Name</label>
                            <input type="text" class="form-control" id="templateName" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <input type="text" class="form-control" id="templateDescription">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Subject</label>
                            <input type="text" class="form-control" id="templateSubject">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Content</label>
                            <textarea class="form-control" id="templateContent" rows="10" required></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="saveTemplate()">Save Template</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Preview Modal -->
    <div class="modal fade" id="previewModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Template Preview</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="previewContent">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentTemplateId = null;
        
        function showCreateModal() {
            document.getElementById('modalTitle').textContent = 'Create New Template';
            document.getElementById('templateForm').reset();
            document.getElementById('templateId').value = '';
            currentTemplateId = null;
            new bootstrap.Modal(document.getElementById('templateModal')).show();
        }
        
        async function editTemplate(id) {
            try {
                const response = await fetch(`/api/spinner/templates/${id}`);
                const result = await response.json();
                
                if (result.success) {
                    const template = result.data;
                    document.getElementById('modalTitle').textContent = 'Edit Template';
                    document.getElementById('templateId').value = template.id;
                    document.getElementById('templateName').value = template.name;
                    document.getElementById('templateDescription').value = template.description || '';
                    document.getElementById('templateSubject').value = template.subject || '';
                    document.getElementById('templateContent').value = template.content;
                    currentTemplateId = id;
                    new bootstrap.Modal(document.getElementById('templateModal')).show();
                } else {
                    alert('Error loading template: ' + result.message);
                }
            } catch (error) {
                alert('Error loading template: ' + error.message);
            }
        }
        
        async function saveTemplate() {
            const id = document.getElementById('templateId').value;
            const name = document.getElementById('templateName').value;
            const description = document.getElementById('templateDescription').value;
            const subject = document.getElementById('templateSubject').value;
            const content = document.getElementById('templateContent').value;
            
            if (!name || !content) {
                alert('Please fill in template name and content');
                return;
            }
            
            try {
                const url = id ? `/api/spinner/templates/${id}` : '/api/spinner/templates';
                const method = id ? 'PUT' : 'POST';
                
                const response = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, description, subject, content })
                });
                
                const result = await response.json();
                if (result.success) {
                    alert(id ? 'Template updated successfully!' : 'Template created successfully!');
                    bootstrap.Modal.getInstance(document.getElementById('templateModal')).hide();
                    location.reload();
                } else {
                    alert('Error saving template: ' + result.message);
                }
            } catch (error) {
                alert('Error saving template: ' + error.message);
            }
        }
        
        async function deleteTemplate(id) {
            if (confirm('Are you sure you want to delete this template? This action cannot be undone.')) {
                try {
                    const response = await fetch(`/api/spinner/templates/${id}`, {
                        method: 'DELETE'
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        alert('Template deleted successfully!');
                        location.reload();
                    } else {
                        alert('Error deleting template: ' + result.message);
                    }
                } catch (error) {
                    alert('Error deleting template: ' + error.message);
                }
            }
        }
        
        async function renameTemplate(id) {
            const newName = prompt('Enter new template name:');
            if (newName && newName.trim()) {
                try {
                    // Get current template data
                    const response = await fetch(`/api/spinner/templates/${id}`);
                    const result = await response.json();
                    
                    if (result.success) {
                        const template = result.data;
                        template.name = newName.trim();
                        
                        const updateResponse = await fetch(`/api/spinner/templates/${id}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(template)
                        });
                        
                        const updateResult = await updateResponse.json();
                        if (updateResult.success) {
                            alert('Template renamed successfully!');
                            location.reload();
                        } else {
                            alert('Error renaming template: ' + updateResult.message);
                        }
                    }
                } catch (error) {
                    alert('Error renaming template: ' + error.message);
                }
            }
        }
        
        async function previewTemplate(id) {
            try {
                const response = await fetch(`/api/spinner/templates/${id}`);
                const result = await response.json();
                
                if (result.success) {
                    const template = result.data;
                    const previewHtml = `
                        <div class="mb-3">
                            <h6>Template Name:</h6>
                            <p class="fw-bold">${template.name}</p>
                        </div>
                        <div class="mb-3">
                            <h6>Description:</h6>
                            <p>${template.description || 'No description'}</p>
                        </div>
                        <div class="mb-3">
                            <h6>Subject:</h6>
                            <p class="fw-bold">${template.subject || 'No subject'}</p>
                        </div>
                        <div class="mb-3">
                            <h6>Content:</h6>
                            <div class="border p-3" style="background: #f8f9fa;">
                                ${template.content.replace(/\\n/g, '<br>')}
                            </div>
                        </div>
                    `;
                    
                    document.getElementById('previewContent').innerHTML = previewHtml;
                    new bootstrap.Modal(document.getElementById('previewModal')).show();
                } else {
                    alert('Error loading template preview: ' + result.message);
                }
            } catch (error) {
                alert('Error loading template preview: ' + error.message);
            }
        }
        
        function useTemplate(id) {
            // Redirect to main app with template selected
            window.location.href = `/?template=${id}`;
        }
    </script>
</body>
</html>
        '''
        
        return html
        
    except Exception as e:
        return f"Error loading template management: {str(e)}", 500

if __name__ == "__main__":
    print("Template Manager - Professional Template Management System")
    print("Features:")
    print("✅ Visual template cards")
    print("✅ Edit/Rename/Delete templates")
    print("✅ Template preview")
    print("✅ Professional interface")
    print("✅ Protected existing functionality")