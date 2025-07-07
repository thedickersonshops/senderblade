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
                            <div id="textEditor">
                                <textarea class="form-control" id="spinnerContent" rows="10" 
                                    placeholder="Enter your message with personalization variables like {first_name}"></textarea>
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
                                    <div class="card-body" id="visualCanvas" style="min-height: 300px; border: 2px dashed #ddd;" contenteditable="false">
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
                        <div class="mb-3 d-flex gap-2">
                            <button class="btn btn-primary" onclick="analyzeSpinnerContent()">Analyze Variations</button>
                            <button class="btn btn-success" onclick="previewSpinnerContent()">Generate Previews</button>
                            <div class="dropdown">
                                <button class="btn btn-secondary dropdown-toggle" type="button" id="autoSpinDropdown" data-bs-toggle="dropdown">
                                    Auto-Spin
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item" href="#" onclick="autoSpin('low')">Low Variation</a></li>
                                    <li><a class="dropdown-item" href="#" onclick="autoSpin('medium')">Medium Variation</a></li>
                                    <li><a class="dropdown-item" href="#" onclick="autoSpin('high')">High Variation</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Message Encryption</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="encryptionPassword" class="form-label">Encryption Password</label>
                            <input type="password" class="form-control" id="encryptionPassword" placeholder="Enter password for encryption/decryption">
                        </div>
                        <div class="mb-3 d-flex gap-2">
                            <button class="btn btn-warning" onclick="encryptMessage()">Encrypt Message</button>
                            <button class="btn btn-info" onclick="decryptMessage()">Decrypt Message</button>
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
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Templates</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label for="templateSelect" class="form-label">Select a template</label>
                            <select class="form-select" id="templateSelect" onchange="loadTemplate()">
                                <option value="">-- Select Template --</option>
                                <!-- Templates will be loaded here -->
                            </select>
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
    
    // Load templates
    loadTemplatesList();
    
    // Add live preview listener
    document.getElementById('spinnerContent').addEventListener('input', updateLivePreview);
    document.getElementById('spinnerSubject').addEventListener('input', updateLivePreview);
    document.getElementById('messageFormat').addEventListener('change', updateLivePreview);
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

// Preview spinner content
async function previewSpinnerContent() {
    const content = document.getElementById('spinnerContent').value;
    const subject = document.getElementById('spinnerSubject').value;
    const format = document.getElementById('messageFormat').value;
    
    if (!content) {
        showAlert('Please enter some content to preview', 'warning');
        return;
    }
    
    try {
        // Show loading message
        document.getElementById('previewResults').innerHTML = '<div class="alert alert-info">Generating previews...</div>';
        
        const result = await window.spinner.generatePreviews(content, subject, 3);
        
        let html = '<h6>Preview Variations:</h6>';
        
        // Check if we have content variations
        if (result.content_variations && result.content_variations.length > 0) {
            for (let i = 0; i < result.content_variations.length; i++) {
                let contentHtml = result.content_variations[i];
                
                // For HTML/Visual content, render as HTML
                if (format === 'html' || format === 'visual') {
                    // Don't escape HTML, render it directly
                    contentHtml = contentHtml;
                } else {
                    // For plain text, convert newlines to breaks
                    contentHtml = contentHtml.replace(/\n/g, '<br>');
                }
                
                html += `
                    <div class="card mb-3">
                        <div class="card-header py-1">
                            <small>Variation ${i + 1}</small>
                            ${result.subject_variations && result.subject_variations[i] ? 
                                `<div><strong>Subject:</strong> ${result.subject_variations[i]}</div>` : ''}
                        </div>
                        <div class="card-body py-2" style="font-family: Arial, sans-serif;">
                            ${contentHtml}
                        </div>
                    </div>
                `;
            }
        } else {
            html += '<div class="alert alert-warning">No preview variations generated. Please check your content.</div>';
        }
        
        document.getElementById('previewResults').innerHTML = html;
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

// Load templates list
async function loadTemplatesList() {
    try {
        const templates = await window.spinner.getTemplates();
        const templateSelect = document.getElementById('templateSelect');
        
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
    } catch (error) {
        console.error('Error loading templates:', error);
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

// Save template
async function saveTemplate() {
    const name = document.getElementById('templateName').value;
    const description = document.getElementById('templateDescription').value;
    const content = document.getElementById('spinnerContent').value;
    const subject = document.getElementById('spinnerSubject').value;
    
    if (!name) {
        showAlert('Please enter a template name', 'warning');
        return;
    }
    
    try {
        await window.spinner.createTemplate(name, content, subject, description);
        showAlert('Template saved successfully', 'success');
        
        // Close the modal
        bootstrap.Modal.getInstance(document.getElementById('saveTemplateModal')).hide();
        
        // Reload templates list
        loadTemplatesList();
    } catch (error) {
        showAlert(`Error saving template: ${error.message}`, 'danger');
    }
}

// Toggle editor mode
function toggleEditor() {
    const format = document.getElementById('messageFormat').value;
    const textEditor = document.getElementById('textEditor');
    const visualEditor = document.getElementById('visualEditor');
    const textarea = document.getElementById('spinnerContent');
    
    if (format === 'visual') {
        textEditor.style.display = 'none';
        visualEditor.style.display = 'block';
        syncVisualToText();
    } else {
        textEditor.style.display = 'block';
        visualEditor.style.display = 'none';
        
        if (format === 'html') {
            textarea.placeholder = 'Enter HTML content with spinning syntax like {Hello|Hi} and variables like {first_name}';
        } else {
            textarea.placeholder = 'Enter plain text with spinning syntax like {Hello|Hi} and variables like {first_name}';
        }
    }
    
    updateLivePreview();
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
            elementHtml = '<div class="visual-element mb-3"><h2 contenteditable="true">Hello {first_name}!</h2><button class="btn btn-sm btn-danger float-end" onclick="removeElement(this)">×</button></div>';
            break;
        case 'text':
            elementHtml = '<div class="visual-element mb-3"><p contenteditable="true">Enter your message here with {first_name} variables.</p><button class="btn btn-sm btn-danger float-end" onclick="removeElement(this)">×</button></div>';
            break;
        case 'button':
            elementHtml = '<div class="visual-element mb-3"><div style="text-align: center;"><div onclick="return false;" style="display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; cursor: text;"><span contenteditable="true">Click Here</span></div><br><small class="text-muted mt-1">Link: <span contenteditable="true" style="color: #007bff;">https://example.com</span></small></div><button class="btn btn-sm btn-danger float-end" onclick="removeElement(this)">×</button></div>';
            break;
        case 'image':
            elementHtml = '<div class="visual-element mb-3"><div style="text-align: center;"><img src="https://via.placeholder.com/400x200" style="max-width: 100%; height: auto;"></div><button class="btn btn-sm btn-danger float-end" onclick="removeElement(this)">×</button></div>';
            break;
        case 'link':
            elementHtml = '<div class="visual-element mb-3"><p><span onclick="return false;" style="color: #007bff; text-decoration: underline; cursor: text;"><span contenteditable="true">Visit our website</span></span><br><small class="text-muted">Link: <span contenteditable="true" style="color: #007bff;">https://example.com</span></small></p><button class="btn btn-sm btn-danger float-end" onclick="removeElement(this)">×</button></div>';
            break;
        case 'divider':
            elementHtml = '<div class="visual-element mb-3"><hr><button class="btn btn-sm btn-danger float-end" onclick="removeElement(this)">×</button></div>';
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
        const deleteBtn = clone.querySelector('.btn-danger');
        if (deleteBtn) deleteBtn.remove();
        
        // Don't apply auto-spinning in visual editor - let backend handle it
        
        // Convert button divs back to proper links
        const buttonDivs = clone.querySelectorAll('div[onclick="return false;"]');
        buttonDivs.forEach(buttonDiv => {
            const parent = buttonDiv.closest('.visual-element');
            const urlSpan = parent ? parent.querySelector('small span[contenteditable="true"]') : null;
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
            const parent = linkSpan.closest('.visual-element');
            const urlSpan = parent ? parent.querySelector('small span[contenteditable="true"]') : null;
            const url = urlSpan ? urlSpan.textContent.trim() : 'https://example.com';
            const linkText = linkSpan.querySelector('span').innerHTML;
            
            const newLink = document.createElement('a');
            newLink.href = url;
            newLink.style.cssText = 'color: #007bff; text-decoration: underline;';
            newLink.innerHTML = linkText;
            linkSpan.parentNode.replaceChild(newLink, linkSpan);
        });
        
        // Remove the editable URL display
        const editableUrlDisplay = clone.querySelector('small');
        if (editableUrlDisplay) editableUrlDisplay.remove();
        
        // Get the actual content without the wrapper div
        const content = clone.innerHTML;
        html += content;
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