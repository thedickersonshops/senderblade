// Message Spinner functionality
class MessageSpinner {
    constructor() {
        this.baseUrl = 'http://localhost:5001/api';
        this.templates = [];
    }

    // Process content with spinning syntax
    async processContent(content, subject = '', personalization = {}, count = 1) {
        try {
            const response = await fetch(`${this.baseUrl}/spinner/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content,
                    subject,
                    personalization,
                    count
                })
            });

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || 'Failed to process spinner content');
            }

            return data;
        } catch (error) {
            console.error('Error processing spinner content:', error);
            throw error;
        }
    }

    // Generate preview variations
    async generatePreviews(content, subject = '', count = 3) {
        try {
            const response = await fetch(`${this.baseUrl}/spinner/preview`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content,
                    subject,
                    count
                })
            });

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || 'Failed to generate previews');
            }

            return data;
        } catch (error) {
            console.error('Error generating previews:', error);
            throw error;
        }
    }

    // Analyze content for variations
    async analyzeContent(content) {
        try {
            const response = await fetch(`${this.baseUrl}/spinner/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content
                })
            });

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || 'Failed to analyze content');
            }

            return data.data;
        } catch (error) {
            console.error('Error analyzing content:', error);
            throw error;
        }
    }
    
    // Auto-spinner methods
    async autoSpin(content, subject = '', level = 'medium') {
        try {
            const response = await fetch(`${this.baseUrl}/spinner/auto`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content,
                    subject,
                    level
                })
            });

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || 'Failed to auto-spin content');
            }

            return data.data;
        } catch (error) {
            console.error('Error auto-spinning content:', error);
            throw error;
        }
    }
    
    // Encryption methods
    async encryptMessage(content, password) {
        try {
            const response = await fetch(`${this.baseUrl}/spinner/encrypt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content,
                    password
                })
            });

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || 'Failed to encrypt message');
            }

            return data.data;
        } catch (error) {
            console.error('Error encrypting message:', error);
            throw error;
        }
    }
    
    async decryptMessage(encryptedContent, password) {
        try {
            const response = await fetch(`${this.baseUrl}/spinner/decrypt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    encrypted_content: encryptedContent,
                    password
                })
            });

            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || 'Failed to decrypt message');
            }

            return data.data;
        } catch (error) {
            console.error('Error decrypting message:', error);
            throw error;
        }
    }
    
    // Template management methods
    async getTemplates() {
        try {
            const response = await fetch(`${this.baseUrl}/spinner/templates`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to fetch templates');
            }
            
            this.templates = data.data;
            return this.templates;
        } catch (error) {
            console.error('Error fetching templates:', error);
            throw error;
        }
    }
    
    async createTemplate(name, content, subject = '', description = '') {
        try {
            const response = await fetch(`${this.baseUrl}/spinner/templates`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    content,
                    subject,
                    description
                })
            });
            
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.message || 'Failed to create template');
            }
            
            return data.data;
        } catch (error) {
            console.error('Error creating template:', error);
            throw error;
        }
    }
}

// Create a singleton instance if it doesn't already exist
if (!window.spinner) {
    window.spinner = new MessageSpinner();
}

// UI Functions for Message Spinner
function loadSpinnerUI() {
    document.getElementById('pageTitle').textContent = 'Message Spinner';
    document.getElementById('pageActions').innerHTML = `
        <button class="btn btn-success me-2" onclick="saveMessage()">Save Message</button>
        <button class="btn btn-outline-secondary me-2" onclick="clearMessage()">Clear Message</button>
        <button class="btn btn-primary" onclick="showSaveTemplateModal()">Save as Template</button>
    `;
    
    document.getElementById('pageContent').innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Message Spinner Editor</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="spinnerSubject" class="form-label">Subject</label>
                            <input type="text" class="form-control" id="spinnerSubject" placeholder="Enter email subject">
                        </div>
                        <div class="mb-3">
                            <label for="messageFormat" class="form-label">Message Format</label>
                            <select class="form-select" id="messageFormat" onchange="toggleEditor()">
                                <option value="text">Plain Text</option>
                                <option value="html">HTML Code</option>
                                <option value="visual">Visual Editor</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="spinnerContent" class="form-label">Message Content</label>
                            
                            <!-- Rich Text Toolbar -->
                            <div class="editor-toolbar mb-2" id="richTextToolbar" style="display: none;">
                                <div class="btn-group me-2" role="group">
                                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="formatText('bold')" title="Bold">
                                        <i class="fas fa-bold"></i>
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="formatText('italic')" title="Italic">
                                        <i class="fas fa-italic"></i>
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="formatText('underline')" title="Underline">
                                        <i class="fas fa-underline"></i>
                                    </button>
                                </div>
                                
                                <div class="btn-group me-2" role="group">
                                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="formatText('justifyLeft')" title="Align Left">
                                        <i class="fas fa-align-left"></i>
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="formatText('justifyCenter')" title="Align Center">
                                        <i class="fas fa-align-center"></i>
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="formatText('justifyRight')" title="Align Right">
                                        <i class="fas fa-align-right"></i>
                                    </button>
                                </div>
                                
                                <div class="btn-group me-2" role="group">
                                    <select class="form-select form-select-sm" onchange="changeFontSize(this.value)" style="width: auto;">
                                        <option value="">Font Size</option>
                                        <option value="1">Small</option>
                                        <option value="3">Normal</option>
                                        <option value="5">Large</option>
                                        <option value="7">Extra Large</option>
                                    </select>
                                </div>
                                
                                <div class="btn-group me-2" role="group">
                                    <input type="color" class="form-control form-control-sm" id="textColor" onchange="changeTextColor(this.value)" title="Text Color" style="width: 40px; height: 32px;">
                                </div>
                                
                                <div class="btn-group" role="group">
                                    <button type="button" class="btn btn-outline-info btn-sm" onclick="showSignatureModal()" title="Add Signature">
                                        <i class="fas fa-signature"></i> Signature
                                    </button>
                                </div>
                            </div>
                            
                            <div id="textEditor">
                                <textarea class="form-control" id="spinnerContent" rows="10" 
                                    placeholder="Enter your message with personalization variables like {first_name}"></textarea>
                            </div>
                            
                            <!-- Rich Text Editor for HTML mode -->
                            <div id="richTextEditor" style="display: none;">
                                <div id="messageEditor" contenteditable="true" class="form-control rich-editor" style="min-height: 300px; padding: 15px;">
                                    <p>Start typing your message here...</p>
                                </div>
                            </div>
                            <div id="visualEditor" style="display: none;">
                                <div class="card">
                                    <div class="card-header bg-light">
                                        <div class="btn-toolbar" role="toolbar">
                                            <div class="btn-group me-2" role="group">
                                                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="insertVisualElement('heading')">📝 Heading</button>
                                                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="insertVisualElement('text')">📄 Text</button>
                                                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="insertVisualElement('button')">🔘 Button</button>
                                            </div>
                                            <div class="btn-group me-2" role="group">
                                                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="insertVisualElement('image')">🖼️ Image</button>
                                                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="insertVisualElement('link')">🔗 Link</button>
                                                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="insertVisualElement('divider')">➖ Divider</button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="card-body" id="visualCanvas" style="min-height: 300px; border: 2px dashed #ddd; position: relative;" contenteditable="false">
                                        <div class="visual-canvas-help">Click elements to select • Use alignment buttons above</div>
                                        <p class="text-muted text-center">Click buttons above to add elements to your email</p>
                                    </div>
                                </div>
                                <textarea id="visualHtmlOutput" style="display: none;"></textarea>
                            </div>
                        </div>
                        <div class="mb-3">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="enableSpinner" checked>
                                        <label class="form-check-label" for="enableSpinner">Enable Message Spinning</label>
                                    </div>
                                    <div class="mt-2" id="spinnerStrength">
                                        <label class="form-label">Spinning Strength</label>
                                        <select class="form-select form-select-sm" id="spinnerLevel">
                                            <option value="light">Light (Few variations)</option>
                                            <option value="medium" selected>Medium (Balanced)</option>
                                            <option value="heavy">Heavy (Maximum variations)</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-check form-switch">
                                        <input class="form-check-input" type="checkbox" id="enableEncryption">
                                        <label class="form-check-label" for="enableEncryption">Enable Encryption</label>
                                    </div>
                                    <div class="mt-2" id="encryptionStrength" style="display: none;">
                                        <label class="form-label">Encryption Strength</label>
                                        <select class="form-select form-select-sm" id="encryptionLevel">
                                            <option value="light">Light (Fast)</option>
                                            <option value="medium" selected>Medium (Balanced)</option>
                                            <option value="heavy">Heavy (Maximum)</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <div class="d-flex flex-wrap gap-2">
                                <button class="btn btn-primary" onclick="analyzeSpinnerContent()">
                                    <i class="fas fa-chart-bar me-1"></i>Analyze
                                </button>
                                <button class="btn btn-success" onclick="previewSpinnerContent()">
                                    <i class="fas fa-eye me-1"></i>Preview
                                </button>
                                <div class="dropdown">
                                    <button class="btn btn-secondary dropdown-toggle" type="button" id="autoSpinDropdown" data-bs-toggle="dropdown">
                                        <i class="fas fa-magic me-1"></i>Auto-Spin
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="#" onclick="autoSpin('low')">Low Variation</a></li>
                                        <li><a class="dropdown-item" href="#" onclick="autoSpin('medium')">Medium Variation</a></li>
                                        <li><a class="dropdown-item" href="#" onclick="autoSpin('high')">High Variation</a></li>
                                    </ul>
                                </div>
                                <button class="btn btn-info" onclick="showSignatureModal()">
                                    <i class="fas fa-signature me-1"></i>Signature
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5><i class="fas fa-lock me-2"></i>Message Encryption</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <strong>🔒 What is Message Encryption?</strong><br>
                            <small>Encrypts your message content with a password for extra security. The encrypted message looks like random text and can only be read by someone with the correct password. Useful for sensitive campaigns or storing confidential templates.</small>
                        </div>
                        <div class="mb-3">
                            <label for="encryptionPassword" class="form-label">Encryption Password</label>
                            <input type="password" class="form-control" id="encryptionPassword" placeholder="Enter password for encryption/decryption">
                            <small class="text-muted">Choose a strong password - you'll need it to decrypt the message later</small>
                        </div>
                        <div class="mb-3 d-flex gap-2">
                            <button class="btn btn-warning" onclick="encryptMessage()">
                                <i class="fas fa-lock me-1"></i>Encrypt Message
                            </button>
                            <button class="btn btn-info" onclick="decryptMessage()">
                                <i class="fas fa-unlock me-1"></i>Decrypt Message
                            </button>
                        </div>
                        <div class="alert alert-warning">
                            <small><strong>⚠️ Important:</strong> Keep your password safe! If you lose it, the encrypted message cannot be recovered.</small>
                        </div>
                    </div>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Personalization Variables</h5>
                    </div>
                    <div class="card-body">
                        <p>Use these variables in your message:</p>
                        <ul>
                            <li><code>{first_name}</code> - Recipient's first name</li>
                            <li><code>{last_name}</code> - Recipient's last name</li>
                            <li><code>{email}</code> - Recipient's email address</li>
                            <li><code>{company}</code> - Recipient's company (if available)</li>
                            <li><code>{job_title}</code> - Recipient's job title (if available)</li>
                            <li><code>{sender_name}</code> - Your name</li>
                            <li><code>{sender_email}</code> - Your email address</li>
                        </ul>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-secondary" onclick="insertVariable('first_name', false)">Insert First Name</button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="insertVariable('last_name', false)">Insert Last Name</button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="insertVariable('email', false)">Insert Email</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <!-- Enhanced Template Management -->
                <div class="card mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5><i class="fas fa-file-alt me-2"></i>Templates</h5>
                        <button class="btn btn-primary btn-sm" onclick="showCreateTemplateModal()">
                            <i class="fas fa-plus me-1"></i>New Template
                        </button>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Professional Template Management:</strong> Use the new Template Manager tab for full template control - create, edit, delete, and organize all your templates in one place!
                        </div>
                        <div id="templateCards" class="row">
                            <!-- Template cards will be loaded here -->
                        </div>
                    </div>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Analysis Results</h5>
                    </div>
                    <div class="card-body" id="analysisResults">
                        <div class="alert alert-info">
                            Enter your message and click "Analyze Variations" to see details.
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h5>Live Preview</h5>
                    </div>
                    <div class="card-body" id="livePreview">
                        <div class="alert alert-info">
                            Your message preview will appear here as you type.
                        </div>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h5>Message Previews</h5>
                    </div>
                    <div class="card-body" id="previewResults">
                        <div class="alert alert-info">
                            Enter your message and click "Generate Previews" to see examples.
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Spinner Syntax Guide</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Basic Syntax</h6>
                                <ul>
                                    <li><code>{option1|option2|option3}</code> - Randomly selects one option</li>
                                    <li><code>{Hello|Hi|Hey}</code> - Random greeting</li>
                                    <li><code>{{first_name}}</code> - Inserts personalization variable</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Advanced Examples</h6>
                                <ul>
                                    <li><code>{I am|I'm} {excited|happy|pleased} to {connect with you|reach out|get in touch}</code></li>
                                    <li><code>Our {new|latest} {product|service|offering} will {help you|enable you to|allow you to} {increase|improve|boost} your {results|performance|productivity}</code></li>
                                </ul>
                            </div>
                        </div>
                        <div class="alert alert-info mt-3">
                            <strong>Tip:</strong> Use the Auto-Spin feature to automatically add spinning syntax to your message!
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Load templates immediately and with retries
    loadTemplatesList();
    
    // Also retry after delay
    setTimeout(() => {
        loadTemplatesList();
    }, 2000);
    
    // Add CSS for enhanced features
    const style = document.createElement('style');
    style.textContent = `
        .rich-editor {
            border: 1px solid #ced4da;
            border-radius: 0.375rem;
            background-color: white;
        }
        .rich-editor:focus {
            border-color: #86b7fe;
            outline: 0;
            box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
        }
        .editor-toolbar {
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 0.375rem;
        }
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
    `;
    document.head.appendChild(style);
    
    // Add live preview listener
    document.getElementById('spinnerContent').addEventListener('input', updateLivePreview);
    document.getElementById('spinnerSubject').addEventListener('input', updateLivePreview);
    document.getElementById('messageFormat').addEventListener('change', function() {
        toggleEditor();
        updateLivePreview();
    });
    document.getElementById('enableEncryption').addEventListener('change', toggleEncryptionOptions);
    document.getElementById('enableSpinner').addEventListener('change', toggleSpinnerOptions);
    
    // Initial live preview
    updateLivePreview();
    toggleEncryptionOptions();
    toggleSpinnerOptions();
    
    // Load saved message if exists
    loadSavedMessage();
}

// Analyze spinner content
async function analyzeSpinnerContent() {
    const content = document.getElementById('spinnerContent').value;
    
    if (!content) {
        showAlert('Please enter some content to analyze', 'warning');
        return;
    }
    
    try {
        const results = await window.spinner.analyzeContent(content);
        
        let html = '';
        
        // Show total combinations
        html += `<div class="alert alert-success">
            <strong>Total possible variations:</strong> ${results.total_combinations.toLocaleString()}
        </div>`;
        
        // Show variation blocks
        if (Object.keys(results.variations).length > 0) {
            html += '<h6>Spinner Blocks:</h6>';
            html += '<div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>Block</th><th>Options</th><th>Variations</th></tr></thead><tbody>';
            
            for (const [key, block] of Object.entries(results.variations)) {
                html += `<tr>
                    <td>${key}</td>
                    <td><code>${block.original}</code></td>
                    <td>${block.count} options</td>
                </tr>`;
            }
            
            html += '</tbody></table></div>';
        } else {
            html += '<div class="alert alert-warning">No spinner blocks found. Use {option1|option2} syntax or click Auto-Spin.</div>';
        }
        
        // Show personalization variables
        if (results.personalization_variables && results.personalization_variables.length > 0) {
            html += '<h6>Personalization Variables:</h6>';
            html += '<ul>';
            results.personalization_variables.forEach(variable => {
                html += `<li><code>{{${variable}}}</code></li>`;
            });
            html += '</ul>';
        }
        
        document.getElementById('analysisResults').innerHTML = html;
    } catch (error) {
        showAlert(`Error analyzing content: ${error.message}`, 'danger');
    }
}

// Preview spinner content (fixed)
async function previewSpinnerContent() {
    const content = document.getElementById('spinnerContent').value;
    const subject = document.getElementById('spinnerSubject').value;
    const format = document.getElementById('messageFormat').value;
    
    if (!content) {
        showAlert('Please enter some content to preview', 'warning');
        return;
    }
    
    try {
        // Clear previous results first
        const previewContainer = document.getElementById('previewResults');
        previewContainer.innerHTML = '<div class="alert alert-info">Generating previews...</div>';
        
        const result = await window.spinner.generatePreviews(content, subject, 3);
        
        let html = '<h6>Preview Variations:</h6>';
        
        // Check if we have content variations
        if (result.content_variations && result.content_variations.length > 0) {
            for (let i = 0; i < result.content_variations.length; i++) {
                let contentHtml = result.content_variations[i];
                
                // Clean up visual editor artifacts
                if (format === 'visual') {
                    // Remove control elements from preview
                    contentHtml = contentHtml.replace(/<div class="element-controls"[^>]*>.*?<\/div>/gs, '');
                    contentHtml = contentHtml.replace(/data-align="[^"]*"/g, '');
                }
                
                // For HTML/Visual content, render as HTML
                if (format === 'html' || format === 'visual') {
                    // Clean HTML for preview
                    contentHtml = contentHtml;
                } else {
                    // For plain text, convert newlines to breaks
                    contentHtml = contentHtml.replace(/\n/g, '<br>');
                }
                
                html += `
                    <div class="card mb-3">
                        <div class="card-header py-1">
                            <small><strong>Variation ${i + 1}</strong></small>
                            ${result.subject_variations && result.subject_variations[i] ? 
                                `<div class="mt-1"><strong>Subject:</strong> ${result.subject_variations[i]}</div>` : ''}
                        </div>
                        <div class="card-body py-2" style="font-family: Arial, sans-serif; background: #f8f9fa;">
                            ${contentHtml}
                        </div>
                    </div>
                `;
            }
        } else {
            html += '<div class="alert alert-warning">No preview variations generated. Please check your content.</div>';
        }
        
        previewContainer.innerHTML = html;
    } catch (error) {
        showAlert(`Error generating previews: ${error.message}`, 'danger');
        document.getElementById('previewResults').innerHTML = `<div class="alert alert-danger">Error generating previews: ${error.message}</div>`;
    }
}

// Auto-spin content
async function autoSpin(level) {
    const content = document.getElementById('spinnerContent').value;
    const subject = document.getElementById('spinnerSubject').value;
    
    if (!content) {
        showAlert('Please enter some content before auto-spinning', 'warning');
        return;
    }
    
    try {
        const result = await window.spinner.autoSpin(content, subject, level);
        document.getElementById('spinnerContent').value = result.spun;
        if (result.spun_subject) {
            document.getElementById('spinnerSubject').value = result.spun_subject;
        }
        showAlert(`Content auto-spun with ${level} variation level`, 'success');
    } catch (error) {
        showAlert(`Error auto-spinning content: ${error.message}`, 'danger');
    }
}

// Encrypt message
async function encryptMessage() {
    const content = document.getElementById('spinnerContent').value;
    const password = document.getElementById('encryptionPassword').value;
    
    if (!content) {
        showAlert('Please enter some content before encrypting', 'warning');
        return;
    }
    
    if (!password) {
        showAlert('Please enter an encryption password', 'warning');
        return;
    }
    
    try {
        const result = await window.spinner.encryptMessage(content, password);
        document.getElementById('spinnerContent').value = result.encrypted_content;
        showAlert('Message encrypted successfully', 'success');
    } catch (error) {
        showAlert(`Error encrypting message: ${error.message}`, 'danger');
    }
}

// Decrypt message
async function decryptMessage() {
    const encryptedContent = document.getElementById('spinnerContent').value;
    const password = document.getElementById('encryptionPassword').value;
    
    if (!encryptedContent) {
        showAlert('Please enter encrypted content to decrypt', 'warning');
        return;
    }
    
    if (!password) {
        showAlert('Please enter the decryption password', 'warning');
        return;
    }
    
    try {
        const result = await window.spinner.decryptMessage(encryptedContent, password);
        document.getElementById('spinnerContent').value = result.decrypted_content;
        showAlert('Message decrypted successfully', 'success');
    } catch (error) {
        showAlert('Error decrypting message: Invalid password or corrupted content', 'danger');
    }
}

// Load templates list (FIXED)
async function loadTemplatesList() {
    try {
        console.log('Loading templates...');
        
        // Direct API call with cache busting
        const response = await fetch('/api/spinner/templates?' + Date.now());
        const result = await response.json();
        
        console.log('Template API response:', result);
        
        if (!result.success) {
            console.error('Template API failed:', result.message);
            return;
        }
        
        const templates = result.data || [];
        console.log('Templates loaded:', templates.length);
        
        const templateSelect = document.getElementById('templateSelect');
        
        if (templateSelect) {
            // Clear existing options except the first one
            while (templateSelect.options.length > 1) {
                templateSelect.remove(1);
            }
            
            // Add templates to select
            templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.id;
                option.textContent = template.name;
                templateSelect.appendChild(option);
            });
            
            console.log('Added templates to dropdown:', templates.length);
        }
        
        // Also load template cards if container exists
        loadTemplateCards(templates);
        
    } catch (error) {
        console.error('Error loading templates:', error);
        showAlert('Error loading templates: ' + error.message, 'warning');
    }
}

// Load template cards (new enhanced feature)
function loadTemplateCards(templates) {
    const container = document.getElementById('templateCards');
    if (!container) return;
    
    if (templates.length === 0) {
        container.innerHTML = '<div class="col-12"><p class="text-muted text-center">No templates found. Create your first template!</p></div>';
        return;
    }
    
    let html = '';
    templates.forEach(template => {
        html += `
        <div class="col-md-4 mb-3">
            <div class="card template-card h-100" onclick="loadTemplateFromCard(${template.id})">
                <div class="template-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); editTemplate(${template.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger ms-1" onclick="event.stopPropagation(); deleteTemplate(${template.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                <div class="card-body">
                    <h6 class="card-title">${template.name}</h6>
                    <p class="card-text text-muted small">${template.description || 'No description'}</p>
                    <small class="text-muted">Created: ${new Date(template.created_at).toLocaleDateString()}</small>
                </div>
            </div>
        </div>
        `;
    });
    
    container.innerHTML = html;
}

// Load template from card click
function loadTemplateFromCard(templateId) {
    // Set the select dropdown
    const templateSelect = document.getElementById('templateSelect');
    if (templateSelect) {
        templateSelect.value = templateId;
    }
    
    // Load the template
    loadTemplate();
}

// Edit template function
function editTemplate(templateId) {
    // Load template into editor for editing
    loadTemplateFromCard(templateId);
    showAlert('Template loaded for editing. Make changes and save as new template.', 'info');
}

// Delete template function
async function deleteTemplate(templateId) {
    if (!confirm('Are you sure you want to delete this template?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/spinner/templates/${templateId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (result.success) {
            showAlert('Template deleted successfully!', 'success');
            loadTemplatesList(); // Reload templates
        } else {
            showAlert('Error deleting template: ' + result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error deleting template: ' + error.message, 'danger');
    }
}

// Load a template
async function loadTemplate() {
    const templateId = document.getElementById('templateSelect').value;
    
    if (!templateId) return;
    
    try {
        const templates = window.spinner.templates;
        const template = templates.find(t => t.id == templateId);
        
        if (template) {
            // Load content into textarea
            document.getElementById('spinnerContent').value = template.content || '';
            
            // Load subject
            if (template.subject) {
                document.getElementById('spinnerSubject').value = template.subject;
            }
            
            // Detect and set correct format
            const messageFormat = document.getElementById('messageFormat');
            if (template.content) {
                // Check if it's visual editor content (has visual-element class or email container)
                if (template.content.includes('max-width: 600px') || template.content.includes('font-family: Arial')) {
                    messageFormat.value = 'visual';
                } else if (template.content.includes('<')) {
                    messageFormat.value = 'html';
                } else {
                    messageFormat.value = 'text';
                }
            }
            
            // Trigger editor toggle to show correct interface
            toggleEditor();
            
            // If visual format, populate the visual canvas
            if (messageFormat.value === 'visual' && template.content) {
                restoreVisualEditor(template.content);
            }
            
            // Update live preview
            updateLivePreview();
            
            showAlert('Template loaded successfully', 'success');
        } else {
            showAlert('Template not found', 'warning');
        }
    } catch (error) {
        showAlert(`Error loading template: ${error.message}`, 'danger');
    }
}

// Insert a variable into the editor
function insertVariable(variableName, useDoubleBraces = false) {
    // Get the active textarea (either spinner content or campaign body)
    let textarea = document.getElementById('spinnerContent');
    
    // If we're in the campaign modal, use that textarea instead
    if (document.getElementById('campaignBody') && 
        document.activeElement.id === 'campaignBody') {
        textarea = document.getElementById('campaignBody');
    } else if (document.getElementById('campaignSubject') && 
               document.activeElement.id === 'campaignSubject') {
        textarea = document.getElementById('campaignSubject');
    }
    
    if (!textarea) return;
    
    const cursorPos = textarea.selectionStart;
    const textBefore = textarea.value.substring(0, cursorPos);
    const textAfter = textarea.value.substring(cursorPos);
    
    // Format the variable (single or double braces)
    // For campaign fields, always use single braces
    const isCampaignField = textarea.id === 'campaignBody' || textarea.id === 'campaignSubject';
    const variableBlock = (useDoubleBraces && !isCampaignField) ? 
        `{{${variableName}}}` : `{${variableName}}`;
    
    textarea.value = textBefore + variableBlock + textAfter;
    textarea.focus();
    textarea.selectionStart = cursorPos + variableBlock.length;
    textarea.selectionEnd = cursorPos + variableBlock.length;
}

// Show save template modal
function showSaveTemplateModal() {
    const content = document.getElementById('spinnerContent').value;
    const subject = document.getElementById('spinnerSubject').value;
    
    if (!content) {
        showAlert('Please enter some content before saving as a template', 'warning');
        return;
    }
    
    // Create modal HTML
    const modalHtml = `
        <div class="modal fade" id="saveTemplateModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Save as Template</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="templateName" class="form-label">Template Name</label>
                            <input type="text" class="form-control" id="templateName" required>
                        </div>
                        <div class="mb-3">
                            <label for="templateDescription" class="form-label">Description</label>
                            <textarea class="form-control" id="templateDescription" rows="3"></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="saveTemplate()">Save Template</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to the page
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('saveTemplateModal'));
    modal.show();
    
    // Remove modal from DOM when hidden
    document.getElementById('saveTemplateModal').addEventListener('hidden.bs.modal', function () {
        document.body.removeChild(modalContainer);
    });
}

// Save template from Message Spinner page
async function saveTemplate() {
    const name = document.getElementById('templateName').value;
    const description = document.getElementById('templateDescription').value;
    const content = document.getElementById('spinnerContent').value;
    const subject = document.getElementById('spinnerSubject').value;
    
    if (!name) {
        showAlert('Please enter a template name', 'warning');
        return;
    }
    
    if (!content) {
        showAlert('Please enter template content', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/spinner/templates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description, subject, content })
        });
        
        const result = await response.json();
        if (result.success) {
            showAlert('Template saved successfully!', 'success');
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('saveTemplateModal'));
            if (modal) modal.hide();
            
            // Reload templates list
            setTimeout(() => {
                loadTemplatesList();
            }, 500);
        } else {
            showAlert('Error saving template: ' + result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error saving template: ' + error.message, 'danger');
    }
}

// Create new template (fixed version)
async function createNewTemplate() {
    const name = document.getElementById('newTemplateName').value;
    const description = document.getElementById('newTemplateDescription').value;
    const subject = document.getElementById('newTemplateSubject').value;
    const content = document.getElementById('newTemplateContent').value;
    
    if (!name || !content) {
        showAlert('Please fill in template name and content', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/spinner/templates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description, subject, content })
        });
        
        const result = await response.json();
        if (result.success) {
            showAlert('Template created successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createTemplateModal')).hide();
            
            // Force reload templates list with delay
            setTimeout(async () => {
                await loadTemplatesList();
            }, 500);
        } else {
            showAlert('Error creating template: ' + result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error creating template: ' + error.message, 'danger');
    }
}

// Enhanced visual element functions
function alignVisualElements(alignment) {
    const selectedElements = document.querySelectorAll('.visual-element.selected');
    if (selectedElements.length === 0) {
        showAlert('Please select elements to align by clicking on them', 'info');
        return;
    }
    
    selectedElements.forEach(element => {
        element.setAttribute('data-align', alignment);
        const contentElements = element.querySelectorAll('h1, h2, h3, h4, h5, h6, p, div:not(.element-controls)');
        contentElements.forEach(content => {
            if (content.style) {
                content.style.textAlign = alignment;
            }
        });
    });
    
    syncVisualToText();
    showAlert(`Elements aligned to ${alignment}`, 'success');
}

function changeElementStyle(button, property, value) {
    const element = button.closest('.visual-element');
    const contentElement = element.querySelector('[contenteditable="true"], img, hr, div:not(.element-controls)');
    
    if (contentElement && contentElement.style) {
        contentElement.style[property] = value;
        syncVisualToText();
    }
}

function changeButtonColor(button, color) {
    const element = button.closest('.visual-element');
    const buttonElement = element.querySelector('div[onclick="return false;"]');
    
    if (buttonElement) {
        buttonElement.style.background = color;
        syncVisualToText();
    }
}

function changeQuoteColor(button, color) {
    const element = button.closest('.visual-element');
    const quoteElement = element.querySelector('blockquote');
    
    if (quoteElement) {
        quoteElement.style.borderLeftColor = color;
        syncVisualToText();
    }
}

function changeColumnLayout(button, layout) {
    const element = button.closest('.visual-element');
    const columns = element.querySelectorAll('div[style*="flex:"]');
    
    if (columns.length >= 2) {
        if (layout === '1-1') {
            columns[0].style.flex = '1';
            columns[1].style.flex = '1';
        } else if (layout === '2-1') {
            columns[0].style.flex = '2';
            columns[1].style.flex = '1';
        } else if (layout === '1-2') {
            columns[0].style.flex = '1';
            columns[1].style.flex = '2';
        }
        syncVisualToText();
    }
}

// Toggle editor mode
function toggleEditor() {
    const format = document.getElementById('messageFormat').value;
    const textEditor = document.getElementById('textEditor');
    const visualEditor = document.getElementById('visualEditor');
    const richTextEditor = document.getElementById('richTextEditor');
    const richTextToolbar = document.getElementById('richTextToolbar');
    const textarea = document.getElementById('spinnerContent');
    
    // Hide all editors first
    if (textEditor) textEditor.style.display = 'none';
    if (visualEditor) visualEditor.style.display = 'none';
    if (richTextEditor) richTextEditor.style.display = 'none';
    if (richTextToolbar) richTextToolbar.style.display = 'none';
    
    if (format === 'visual') {
        if (visualEditor) {
            visualEditor.style.display = 'block';
            syncVisualToText();
        }
    } else if (format === 'html') {
        // Show rich text editor for HTML mode
        if (richTextEditor && richTextToolbar) {
            richTextEditor.style.display = 'block';
            richTextToolbar.style.display = 'block';
            
            // Sync content between textarea and rich editor
            const messageEditor = document.getElementById('messageEditor');
            if (messageEditor && textarea) {
                if (textarea.value) {
                    messageEditor.innerHTML = textarea.value;
                }
                
                // Add event listener for rich editor changes
                messageEditor.addEventListener('input', function() {
                    textarea.value = messageEditor.innerHTML;
                    updateLivePreview();
                });
            }
        }
        if (textarea) {
            textarea.placeholder = 'Enter HTML content with spinning syntax like {Hello|Hi} and variables like {first_name}';
        }
    } else {
        // Plain text mode
        if (textEditor) {
            textEditor.style.display = 'block';
        }
        if (textarea) {
            textarea.placeholder = 'Enter plain text with spinning syntax like {Hello|Hi} and variables like {first_name}';
        }
    }
    
    updateLivePreview();
}

// Rich text formatting functions
function formatText(command) {
    document.execCommand(command, false, null);
    const messageEditor = document.getElementById('messageEditor');
    if (messageEditor) {
        messageEditor.focus();
        // Update textarea
        const textarea = document.getElementById('spinnerContent');
        if (textarea) {
            textarea.value = messageEditor.innerHTML;
            updateLivePreview();
        }
    }
}

function changeFontSize(size) {
    if (size) {
        document.execCommand('fontSize', false, size);
        const messageEditor = document.getElementById('messageEditor');
        if (messageEditor) {
            messageEditor.focus();
            // Update textarea
            const textarea = document.getElementById('spinnerContent');
            if (textarea) {
                textarea.value = messageEditor.innerHTML;
                updateLivePreview();
            }
        }
    }
}

function changeTextColor(color) {
    document.execCommand('foreColor', false, color);
    const messageEditor = document.getElementById('messageEditor');
    if (messageEditor) {
        messageEditor.focus();
        // Update textarea
        const textarea = document.getElementById('spinnerContent');
        if (textarea) {
            textarea.value = messageEditor.innerHTML;
            updateLivePreview();
        }
    }
}

// Show signature modal
function showSignatureModal() {
    const modalHtml = `
        <div class="modal fade" id="signatureModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add Signature</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Signature Content</label>
                            <textarea class="form-control" id="signatureContent" rows="6" placeholder="Best regards,\nYour Name\nYour Title\nCompany Name\nPhone: (123) 456-7890\nEmail: your.email@company.com"></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="insertSignature()">Insert Signature</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('signatureModal'));
    modal.show();
    
    // Remove modal when hidden
    document.getElementById('signatureModal').addEventListener('hidden.bs.modal', function () {
        document.body.removeChild(modalContainer);
    });
}

// Insert signature
function insertSignature() {
    const signature = document.getElementById('signatureContent').value;
    if (signature) {
        const format = document.getElementById('messageFormat').value;
        const textarea = document.getElementById('spinnerContent');
        
        if (format === 'html') {
            // Insert into rich editor
            const messageEditor = document.getElementById('messageEditor');
            if (messageEditor) {
                const signatureHtml = `<br><br>---<br>${signature.replace(/\n/g, '<br>')}`;
                messageEditor.innerHTML += signatureHtml;
                textarea.value = messageEditor.innerHTML;
            }
        } else {
            // Insert into textarea
            const signatureText = `\n\n---\n${signature}`;
            textarea.value += signatureText;
        }
        
        updateLivePreview();
        bootstrap.Modal.getInstance(document.getElementById('signatureModal')).hide();
    }
}

// Show create template modal
function showCreateTemplateModal() {
    const modalHtml = `
        <div class="modal fade" id="createTemplateModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Create New Template</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Template Name</label>
                            <input type="text" class="form-control" id="newTemplateName" placeholder="Enter template name">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <input type="text" class="form-control" id="newTemplateDescription" placeholder="Brief description">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Subject</label>
                            <input type="text" class="form-control" id="newTemplateSubject" placeholder="Email subject">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Content</label>
                            <textarea class="form-control" id="newTemplateContent" rows="8" placeholder="Template content"></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="createNewTemplate()">Create Template</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
    
    // Pre-fill with current content
    setTimeout(() => {
        const currentContent = document.getElementById('spinnerContent').value;
        const currentSubject = document.getElementById('spinnerSubject').value;
        
        if (currentContent) {
            document.getElementById('newTemplateContent').value = currentContent;
        }
        if (currentSubject) {
            document.getElementById('newTemplateSubject').value = currentSubject;
        }
    }, 100);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('createTemplateModal'));
    modal.show();
    
    // Remove modal when hidden
    document.getElementById('createTemplateModal').addEventListener('hidden.bs.modal', function () {
        document.body.removeChild(modalContainer);
    });
}

// Create new template
async function createNewTemplate() {
    const name = document.getElementById('newTemplateName').value;
    const description = document.getElementById('newTemplateDescription').value;
    const subject = document.getElementById('newTemplateSubject').value;
    const content = document.getElementById('newTemplateContent').value;
    
    if (!name || !content) {
        showAlert('Please fill in template name and content', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/spinner/templates', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description, subject, content })
        });
        
        const result = await response.json();
        if (result.success) {
            showAlert('Template created successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createTemplateModal')).hide();
            loadTemplatesList(); // Reload templates
        } else {
            showAlert('Error creating template: ' + result.message, 'danger');
        }
    } catch (error) {
        showAlert('Error creating template: ' + error.message, 'danger');
    }
}

// Toggle encryption options
function toggleEncryptionOptions() {
    const enableEncryption = document.getElementById('enableEncryption').checked;
    const encryptionStrength = document.getElementById('encryptionStrength');
    
    if (enableEncryption) {
        encryptionStrength.style.display = 'block';
    } else {
        encryptionStrength.style.display = 'none';
    }
    
    updateLivePreview();
}

// Toggle spinner options
function toggleSpinnerOptions() {
    const enableSpinner = document.getElementById('enableSpinner').checked;
    const spinnerStrength = document.getElementById('spinnerStrength');
    
    if (enableSpinner) {
        spinnerStrength.style.display = 'block';
    } else {
        spinnerStrength.style.display = 'none';
    }
    
    updateLivePreview();
}

// Insert visual elements
function insertVisualElement(type) {
    const canvas = document.getElementById('visualCanvas');
    let elementHtml = '';
    
    switch(type) {
        case 'heading':
            elementHtml = '<div class="visual-element mb-3" data-align="left"><h2 contenteditable="true" style="text-align: left;">Hello {first_name}!</h2><div class="element-controls"><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'fontSize\', \'24px\')" title="Large">L</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'fontSize\', \'18px\')" title="Medium">M</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'fontSize\', \'14px\')" title="Small">S</button><button class="btn btn-sm btn-danger" onclick="removeElement(this)">×</button></div></div>';
            break;
        case 'text':
            elementHtml = '<div class="visual-element mb-3" data-align="left"><p contenteditable="true" style="text-align: left; line-height: 1.6;">Enter your message here with {first_name} variables. You can add multiple paragraphs and format your text as needed.</p><div class="element-controls"><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'lineHeight\', \'2\')" title="Double Space">2x</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'lineHeight\', \'1.6\')" title="Normal Space">1.6x</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'lineHeight\', \'1.2\')" title="Tight Space">1.2x</button><button class="btn btn-sm btn-danger" onclick="removeElement(this)">×</button></div></div>';
            break;
        case 'button':
            elementHtml = '<div class="visual-element mb-3" data-align="center"><div style="text-align: center;"><div onclick="return false;" style="display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; cursor: text; margin: 10px 0;"><span contenteditable="true">Click Here</span></div><br><small class="text-muted mt-1">Link: <span contenteditable="true" style="color: #007bff;">https://example.com</span></small></div><div class="element-controls"><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeButtonColor(this, \'#007bff\')" style="background: #007bff; color: white;" title="Blue">■</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeButtonColor(this, \'#28a745\')" style="background: #28a745; color: white;" title="Green">■</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeButtonColor(this, \'#dc3545\')" style="background: #dc3545; color: white;" title="Red">■</button><button class="btn btn-sm btn-danger" onclick="removeElement(this)">×</button></div></div>';
            break;
        case 'image':
            elementHtml = '<div class="visual-element mb-3" data-align="center"><div style="text-align: center; padding: 20px 0;"><img src="https://via.placeholder.com/400x200" style="max-width: 100%; height: auto; border-radius: 8px;"><br><small class="text-muted mt-2">Image URL: <span contenteditable="true" style="color: #007bff;">https://via.placeholder.com/400x200</span></small></div><div class="element-controls"><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'width\', \'100%\')" title="Full Width">100%</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'width\', \'50%\')" title="Half Width">50%</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'width\', \'25%\')" title="Quarter Width">25%</button><button class="btn btn-sm btn-danger" onclick="removeElement(this)">×</button></div></div>';
            break;
        case 'link':
            elementHtml = '<div class="visual-element mb-3" data-align="left"><p style="text-align: left;"><span onclick="return false;" style="color: #007bff; text-decoration: underline; cursor: text;"><span contenteditable="true">Visit our website</span></span><br><small class="text-muted">Link: <span contenteditable="true" style="color: #007bff;">https://example.com</span></small></p><div class="element-controls"><button class="btn btn-sm btn-danger" onclick="removeElement(this)">×</button></div></div>';
            break;
        case 'divider':
            elementHtml = '<div class="visual-element mb-4" data-align="center"><hr style="border: 1px solid #dee2e6; margin: 20px 0;"><div class="element-controls"><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'borderWidth\', \'3px\')" title="Thick">Thick</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'borderWidth\', \'1px\')" title="Thin">Thin</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'borderStyle\', \'dashed\')" title="Dashed">Dash</button><button class="btn btn-sm btn-danger" onclick="removeElement(this)">×</button></div></div>';
            break;
        case 'spacer':
            elementHtml = '<div class="visual-element mb-3" data-align="center"><div style="height: 30px; background: linear-gradient(90deg, transparent 0%, #e9ecef 50%, transparent 100%); display: flex; align-items: center; justify-content: center; font-size: 12px; color: #6c757d;">--- Spacing ---</div><div class="element-controls"><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'height\', \'50px\')" title="Large Space">L</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'height\', \'30px\')" title="Medium Space">M</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeElementStyle(this, \'height\', \'15px\')" title="Small Space">S</button><button class="btn btn-sm btn-danger" onclick="removeElement(this)">×</button></div></div>';
            break;
        case 'columns':
            elementHtml = '<div class="visual-element mb-3" data-align="left"><div style="display: flex; gap: 20px;"><div style="flex: 1; padding: 15px; border: 1px dashed #dee2e6;"><p contenteditable="true">Left column content with {first_name}</p></div><div style="flex: 1; padding: 15px; border: 1px dashed #dee2e6;"><p contenteditable="true">Right column content</p></div></div><div class="element-controls"><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeColumnLayout(this, \'1-1\')" title="Equal Columns">1:1</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeColumnLayout(this, \'2-1\')" title="Wide Left">2:1</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeColumnLayout(this, \'1-2\')" title="Wide Right">1:2</button><button class="btn btn-sm btn-danger" onclick="removeElement(this)">×</button></div></div>';
            break;
        case 'quote':
            elementHtml = '<div class="visual-element mb-3" data-align="left"><blockquote style="border-left: 4px solid #007bff; padding-left: 20px; margin: 20px 0; font-style: italic; color: #6c757d;"><p contenteditable="true">"This is a great quote that will inspire your readers, {first_name}!"</p><footer style="font-size: 14px; margin-top: 10px;">— <cite contenteditable="true">Your Name</cite></footer></blockquote><div class="element-controls"><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeQuoteColor(this, \'#007bff\')" style="background: #007bff; color: white;" title="Blue">■</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeQuoteColor(this, \'#28a745\')" style="background: #28a745; color: white;" title="Green">■</button><button class="btn btn-sm btn-outline-secondary me-1" onclick="changeQuoteColor(this, \'#ffc107\')" style="background: #ffc107; color: black;" title="Yellow">■</button><button class="btn btn-sm btn-danger" onclick="removeElement(this)">×</button></div></div>';
            break;
    }
    
    if (canvas.children.length === 1 && canvas.children[0].classList.contains('text-muted')) {
        canvas.innerHTML = '';
    }
    
    canvas.insertAdjacentHTML('beforeend', elementHtml);
    
    // Add event listeners to contenteditable elements
    const newElement = canvas.lastElementChild;
    const editableElements = newElement.querySelectorAll('[contenteditable="true"]');
    editableElements.forEach(el => {
        el.addEventListener('input', function() {
            syncLinkUrls(newElement);
            syncVisualToText();
        });
        el.addEventListener('blur', function() {
            syncLinkUrls(newElement);
            syncVisualToText();
        });
    });
    
    syncVisualToText();
}

// Remove visual element
function removeElement(button) {
    button.closest('.visual-element').remove();
    const canvas = document.getElementById('visualCanvas');
    if (canvas.children.length === 0) {
        canvas.innerHTML = '<p class="text-muted text-center">Click buttons above to add elements</p>';
    }
    syncVisualToText();
}

// Sync link URLs
function syncLinkUrls(element) {
    // Find all editable link URLs and sync them with actual href attributes
    const linkElements = element.querySelectorAll('a');
    linkElements.forEach(link => {
        const parent = link.closest('.visual-element');
        if (parent) {
            const editableUrl = parent.querySelector('small span[contenteditable="true"]');
            if (editableUrl && editableUrl.textContent.trim()) {
                link.href = editableUrl.textContent.trim();
            }
        }
    });
}

// Sync visual to text
function syncVisualToText() {
    const canvas = document.getElementById('visualCanvas');
    const textarea = document.getElementById('spinnerContent');
    let html = '';
    
    // Get all visual elements and extract their content
    canvas.querySelectorAll('.visual-element').forEach(element => {
        const clone = element.cloneNode(true);
        
        // Remove all control elements
        const controls = clone.querySelector('.element-controls');
        if (controls) controls.remove();
        
        // Convert button divs back to proper links
        const buttonDivs = clone.querySelectorAll('div[onclick="return false;"]');
        buttonDivs.forEach(buttonDiv => {
            const parent = buttonDiv.closest('.visual-element') || element;
            const urlSpan = parent.querySelector('small span[contenteditable="true"]');
            const url = urlSpan ? urlSpan.textContent.trim() : 'https://example.com';
            const buttonText = buttonDiv.querySelector('span').innerHTML;
            
            const newButton = document.createElement('a');
            newButton.href = url;
            newButton.style.cssText = buttonDiv.style.cssText.replace('cursor: text;', '');
            newButton.innerHTML = buttonText;
            buttonDiv.parentNode.replaceChild(newButton, buttonDiv);
        });
        
        // Convert link spans back to proper links
        const linkSpans = clone.querySelectorAll('span[onclick="return false;"]');
        linkSpans.forEach(linkSpan => {
            const parent = linkSpan.closest('.visual-element') || element;
            const urlSpan = parent.querySelector('small span[contenteditable="true"]');
            const url = urlSpan ? urlSpan.textContent.trim() : 'https://example.com';
            const linkText = linkSpan.querySelector('span').innerHTML;
            
            const newLink = document.createElement('a');
            newLink.href = url;
            newLink.style.cssText = 'color: #007bff; text-decoration: underline;';
            newLink.innerHTML = linkText;
            linkSpan.parentNode.replaceChild(newLink, linkSpan);
        });
        
        // Remove URL display elements
        const editableUrlDisplays = clone.querySelectorAll('small');
        editableUrlDisplays.forEach(small => small.remove());
        
        // Get clean content
        html += clone.innerHTML;
    });
    
    // Only wrap if we have content
    if (html.trim()) {
        html = `<div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">${html}</div>`;
        textarea.value = html;
    } else {
        textarea.value = '';
    }
    
    // Trigger input event to update preview
    textarea.dispatchEvent(new Event('input'));
}

// Update live preview
function updateLivePreview() {
    const content = document.getElementById('spinnerContent').value;
    const subject = document.getElementById('spinnerSubject').value;
    const format = document.getElementById('messageFormat').value;
    const enableSpinner = document.getElementById('enableSpinner').checked;
    const enableEncryption = document.getElementById('enableEncryption').checked;
    const encryptionLevel = document.getElementById('encryptionLevel').value;
    const spinnerLevel = document.getElementById('spinnerLevel').value;
    
    let previewContent = content;
    let previewSubject = subject;
    
    // Apply spinning if enabled - process both manual and auto spinning
    if (enableSpinner && content) {
        previewContent = processSpinnerSyntax(content);
    }
    if (enableSpinner && subject) {
        previewSubject = processSpinnerSyntax(subject);
    }
    
    // Replace variables with sample data
    const sampleData = {
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'john.smith@example.com',
        'company': 'Acme Inc'
    };
    
    for (const [key, value] of Object.entries(sampleData)) {
        const regex = new RegExp(`\\{${key}\\}`, 'g');
        previewContent = previewContent.replace(regex, value);
        previewSubject = previewSubject.replace(regex, value);
    }
    
    // Show status badges
    let statusText = '';
    if (enableEncryption) {
        statusText = `<div class="badge bg-warning mb-2">🔒 Encryption: ${encryptionLevel}</div><br>`;
    }
    if (enableSpinner) {
        statusText += `<div class="badge bg-info mb-2">🔄 Spinning: ${spinnerLevel}</div><br>`;
    }
    
    // Update preview
    const previewDiv = document.getElementById('livePreview');
    if (previewContent || previewSubject) {
        let html = statusText;
        if (previewSubject) {
            html += `<strong>Subject:</strong> ${previewSubject}<br><br>`;
        }
        
        if (format === 'html' || format === 'visual') {
            // For HTML/Visual content, render as HTML but in a contained preview
            html += `<div style="border: 1px solid #ddd; padding: 15px; background: #f9f9f9; font-family: Arial, sans-serif;">${previewContent}</div>`;
        } else {
            html += `<pre style="white-space: pre-wrap; background: #f9f9f9; padding: 10px; border: 1px solid #ddd;">${previewContent}</pre>`;
        }
        
        previewDiv.innerHTML = html;
    } else {
        previewDiv.innerHTML = '<div class="alert alert-info">Your message preview will appear here as you type.</div>';
    }
}

// Show alert
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.appendChild(alertElement);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertElement.parentNode) {
            alertElement.parentNode.removeChild(alertElement);
        }
    }, 5000);
}

// Save message function
function saveMessage() {
    const subject = document.getElementById('spinnerSubject').value;
    const content = document.getElementById('spinnerContent').value;
    const format = document.getElementById('messageFormat').value;
    const enableSpinner = document.getElementById('enableSpinner').checked;
    const enableEncryption = document.getElementById('enableEncryption').checked;
    const spinnerLevel = document.getElementById('spinnerLevel').value;
    const encryptionLevel = document.getElementById('encryptionLevel').value;
    
    if (!content) {
        showAlert('Please enter message content', 'warning');
        return;
    }
    
    // Store message for workflow
    localStorage.setItem('currentMessage', JSON.stringify({
        subject,
        content,
        format,
        enableSpinner,
        enableEncryption,
        spinnerLevel,
        encryptionLevel
    }));
    
    showAlert('Message saved successfully', 'success');
    
    // Check if we're in workflow
    const selectedListId = localStorage.getItem('selectedListId');
    const selectedSmtpId = localStorage.getItem('selectedSmtpId');
    
    if (selectedListId && selectedSmtpId) {
        // Go to campaigns
        loadCampaigns();
    }
}

// Process spinner syntax for preview
function processSpinnerSyntax(text) {
    // Process spinning syntax {option1|option2} and replace with random choice
    let processed = text.replace(/\{([^{}]*\|[^{}]*)\}/g, function(match, content) {
        const options = content.split('|');
        const randomIndex = Math.floor(Math.random() * options.length);
        return options[randomIndex].trim();
    });
    
    // Apply auto-spinning to common words (50% chance)
    const autoSpinWords = {
        'good': ['good', 'great', 'excellent', 'wonderful'],
        'great': ['great', 'excellent', 'wonderful', 'fantastic'],
        'day': ['day', 'time', 'moment'],
        'try': ['try', 'attempt', 'work'],
        'friend': ['friend', 'buddy', 'pal'],
        'started': ['started', 'begun', 'initiated']
    };
    
    const words = processed.split(' ');
    for (let i = 0; i < words.length; i++) {
        if (Math.random() < 0.5) { // 50% chance to spin
            const cleanWord = words[i].replace(/[^a-zA-Z]/g, '').toLowerCase();
            if (autoSpinWords[cleanWord]) {
                const replacement = autoSpinWords[cleanWord][Math.floor(Math.random() * autoSpinWords[cleanWord].length)];
                const punctuation = words[i].replace(/[a-zA-Z]/g, '');
                words[i] = (words[i][0] === words[i][0].toUpperCase() ? 
                    replacement.charAt(0).toUpperCase() + replacement.slice(1) : replacement) + punctuation;
            }
        }
    }
    
    return words.join(' ');
}

// Load saved message
function loadSavedMessage() {
    try {
        const savedMessage = localStorage.getItem('currentMessage');
        if (savedMessage) {
            const message = JSON.parse(savedMessage);
            
            // Load content and subject
            if (message.content) {
                document.getElementById('spinnerContent').value = message.content;
            }
            if (message.subject) {
                document.getElementById('spinnerSubject').value = message.subject;
            }
            
            // Load format and restore correct editor
            if (message.format) {
                document.getElementById('messageFormat').value = message.format;
                toggleEditor();
                
                // If visual format, populate the visual canvas
                if (message.format === 'visual' && message.content) {
                    restoreVisualEditor(message.content);
                }
            }
            
            // Load spinner settings
            if (message.enableSpinner !== undefined) {
                document.getElementById('enableSpinner').checked = message.enableSpinner;
            }
            if (message.spinnerLevel) {
                document.getElementById('spinnerLevel').value = message.spinnerLevel;
            }
            
            // Load encryption settings
            if (message.enableEncryption !== undefined) {
                document.getElementById('enableEncryption').checked = message.enableEncryption;
            }
            if (message.encryptionLevel) {
                document.getElementById('encryptionLevel').value = message.encryptionLevel;
            }
            
            // Update toggles and preview
            toggleEncryptionOptions();
            toggleSpinnerOptions();
            updateLivePreview();
        }
    } catch (error) {
        console.log('No saved message to load');
    }
}

// Restore visual editor from HTML content
function restoreVisualEditor(htmlContent) {
    const canvas = document.getElementById('visualCanvas');
    if (!canvas) return;
    
    // Clear existing content
    canvas.innerHTML = '';
    
    // Simple restoration - convert HTML back to editable visual elements
    // This is a basic implementation that handles common elements
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlContent;
    
    // Find and convert elements back to visual editor format
    const elements = tempDiv.querySelectorAll('h1, h2, h3, p, a, div, hr');
    
    elements.forEach(el => {
        let visualElement = '';
        
        if (el.tagName === 'H2') {
            visualElement = `<div class="visual-element mb-3"><h2 contenteditable="true">${el.innerHTML}</h2><button class="btn btn-sm btn-danger float-end" onclick="removeElement(this)">×</button></div>`;
        } else if (el.tagName === 'P' && !el.querySelector('a')) {
            visualElement = `<div class="visual-element mb-3"><p contenteditable="true">${el.innerHTML}</p><button class="btn btn-sm btn-danger float-end" onclick="removeElement(this)">×</button></div>`;
        } else if (el.tagName === 'A' && el.style.display === 'inline-block') {
            // Button
            visualElement = `<div class="visual-element mb-3"><div style="text-align: center;"><div onclick="return false;" style="display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; cursor: text;"><span contenteditable="true">${el.innerHTML}</span></div><br><small class="text-muted mt-1">Link: <span contenteditable="true" style="color: #007bff;">${el.href}</span></small></div><button class="btn btn-sm btn-danger float-end" onclick="removeElement(this)">×</button></div>`;
        } else if (el.tagName === 'HR') {
            visualElement = `<div class="visual-element mb-3"><hr><button class="btn btn-sm btn-danger float-end" onclick="removeElement(this)">×</button></div>`;
        }
        
        if (visualElement) {
            canvas.insertAdjacentHTML('beforeend', visualElement);
        }
    });
    
    // Add event listeners to new elements
    const editableElements = canvas.querySelectorAll('[contenteditable="true"]');
    editableElements.forEach(el => {
        el.addEventListener('input', function() {
            const element = el.closest('.visual-element');
            syncLinkUrls(element);
            syncVisualToText();
        });
        el.addEventListener('blur', function() {
            const element = el.closest('.visual-element');
            syncLinkUrls(element);
            syncVisualToText();
        });
    });
    
    // If no elements were restored, show placeholder
    if (canvas.children.length === 0) {
        canvas.innerHTML = '<p class="text-muted text-center">Click buttons above to add elements to your email</p>';
    }
}

// Apply auto-spinning to text (disabled - backend handles this)
function applyAutoSpinning(text) {
    // Let backend handle auto-spinning to avoid double processing
    return text;
}

// Clear message function
function clearMessage() {
    // Clear all fields
    document.getElementById('spinnerContent').value = '';
    document.getElementById('spinnerSubject').value = '';
    document.getElementById('messageFormat').value = 'text';
    document.getElementById('enableSpinner').checked = true;
    document.getElementById('enableEncryption').checked = false;
    document.getElementById('spinnerLevel').value = 'medium';
    document.getElementById('encryptionLevel').value = 'medium';
    
    // Clear visual editor
    const canvas = document.getElementById('visualCanvas');
    if (canvas) {
        canvas.innerHTML = '<p class="text-muted text-center">Click buttons above to add elements to your email</p>';
    }
    
    // Clear saved message
    localStorage.removeItem('currentMessage');
    
    // Reset interface
    toggleEditor();
    toggleEncryptionOptions();
    toggleSpinnerOptions();
    updateLivePreview();
    
    showAlert('Message cleared', 'info');
}

// Update the loadSpinner function in the main script to use our new UI
function loadSpinner() {
    loadSpinnerUI();
}