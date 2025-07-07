// Campaign Message Spinner Integration
// Wait for the page to be fully loaded before setting up campaign spinner
document.addEventListener('DOMContentLoaded', function() {
    // Wait a short time to ensure other scripts have initialized
    setTimeout(function() {
        // Check if we're on the campaign creation page
        if (document.getElementById('createCampaignModal')) {
            setupCampaignSpinner();
        }
    }, 500);
});

function setupCampaignSpinner() {
    // Add spinner buttons to campaign modal
    const subjectField = document.getElementById('campaignSubject');
    const bodyField = document.getElementById('campaignBody');
    
    if (subjectField && bodyField) {
        // Add spinner buttons after the subject field
        const subjectContainer = subjectField.parentNode;
        const spinSubjectBtn = document.createElement('button');
        spinSubjectBtn.className = 'btn btn-sm btn-outline-secondary mt-2';
        spinSubjectBtn.type = 'button'; // Ensure it doesn't submit the form
        spinSubjectBtn.innerHTML = '<i class="fas fa-random me-1"></i> Auto-Spin Subject';
        spinSubjectBtn.onclick = function(e) { 
            e.preventDefault(); 
            spinCampaignField('subject'); 
        };
        subjectContainer.appendChild(spinSubjectBtn);
        
        // Add spinner buttons after the body field
        const bodyContainer = bodyField.parentNode;
        const spinnerButtonGroup = document.createElement('div');
        spinnerButtonGroup.className = 'btn-group mt-2';
        
        // Auto-spin button
        const spinBodyBtn = document.createElement('button');
        spinBodyBtn.className = 'btn btn-sm btn-outline-secondary';
        spinBodyBtn.type = 'button'; // Ensure it doesn't submit the form
        spinBodyBtn.innerHTML = '<i class="fas fa-random me-1"></i> Auto-Spin Message';
        spinBodyBtn.onclick = function(e) { 
            e.preventDefault(); 
            spinCampaignField('body'); 
        };
        spinnerButtonGroup.appendChild(spinBodyBtn);
        
        // Template button
        const templateBtn = document.createElement('button');
        templateBtn.className = 'btn btn-sm btn-outline-primary';
        templateBtn.type = 'button'; // Ensure it doesn't submit the form
        templateBtn.innerHTML = '<i class="fas fa-file-alt me-1"></i> Load Template';
        templateBtn.onclick = function(e) {
            e.preventDefault();
            loadSpinnerTemplate();
        };
        spinnerButtonGroup.appendChild(templateBtn);
        
        // Add the button group to the container
        bodyContainer.appendChild(spinnerButtonGroup);
        
        // Add a note about personalization variables
        const helpText = document.createElement('small');
        helpText.className = 'form-text text-muted mt-1';
        helpText.innerHTML = 'Use {option1|option2} for spinning and {first_name} for personalization';
        bodyContainer.appendChild(helpText);
    }
}

// Spin campaign field (subject or body)
async function spinCampaignField(fieldType) {
    try {
        const field = fieldType === 'subject' ? 
            document.getElementById('campaignSubject') : 
            document.getElementById('campaignBody');
        
        if (!field || !field.value) {
            showAlert('Please enter content before spinning', 'warning');
            return;
        }
        
        // Show spinner
        field.disabled = true;
        showAlert('Spinning content...', 'info');
        
        // Call auto-spin API
        let result;
        if (fieldType === 'subject') {
            result = await window.spinner.autoSpin('', field.value, 'medium');
            field.value = result.spun_subject || result.spun;
        } else {
            result = await window.spinner.autoSpin(field.value, '', 'medium');
            field.value = result.spun;
        }
        
        // Re-enable field
        field.disabled = false;
        
        // Show success message
        showAlert('Content auto-spun successfully', 'success');
    } catch (error) {
        console.error('Error spinning campaign field:', error);
        showAlert('Error spinning content: ' + error.message, 'danger');
        
        // Make sure to re-enable the field even if there's an error
        const field = fieldType === 'subject' ? 
            document.getElementById('campaignSubject') : 
            document.getElementById('campaignBody');
        if (field) field.disabled = false;
    }
}

// Load spinner template into campaign
async function loadSpinnerTemplate() {
    try {
        // Get templates
        const templates = await window.spinner.getTemplates();
        
        if (!templates || templates.length === 0) {
            showAlert('No templates available. Create templates in the Message Spinner section.', 'warning');
            return;
        }
        
        // Create template selection modal
        const modalHtml = `
            <div class="modal fade" id="selectTemplateModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Select Template</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <label for="campaignTemplateSelect" class="form-label">Choose a template</label>
                                <select class="form-select" id="campaignTemplateSelect">
                                    <option value="">-- Select Template --</option>
                                    ${templates.map(t => `<option value="${t.id}">${t.name}</option>`).join('')}
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="applyCampaignTemplate()">Apply Template</button>
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
        const modal = new bootstrap.Modal(document.getElementById('selectTemplateModal'));
        modal.show();
        
        // Remove modal from DOM when hidden
        document.getElementById('selectTemplateModal').addEventListener('hidden.bs.modal', function () {
            document.body.removeChild(modalContainer);
        });
    } catch (error) {
        console.error('Error loading templates:', error);
        showAlert('Error loading templates: ' + error.message, 'danger');
    }
}

// Apply selected template to campaign
async function applyCampaignTemplate() {
    const templateId = document.getElementById('campaignTemplateSelect').value;
    
    if (!templateId) {
        showAlert('Please select a template', 'warning');
        return;
    }
    
    try {
        // Get templates
        const templates = await window.spinner.getTemplates();
        const template = templates.find(t => t.id == templateId);
        
        if (template) {
            // Apply template to campaign fields
            document.getElementById('campaignBody').value = template.content;
            
            if (template.subject) {
                document.getElementById('campaignSubject').value = template.subject;
            }
            
            // Close the modal
            bootstrap.Modal.getInstance(document.getElementById('selectTemplateModal')).hide();
            
            showAlert('Template applied successfully', 'success');
        }
    } catch (error) {
        console.error('Error applying template:', error);
        showAlert('Error applying template: ' + error.message, 'danger');
    }
}

// Show alert in campaign modal
function showAlert(message, type = 'info') {
    // Check if alertContainer exists, if not create one
    let alertContainer = document.getElementById('campaignAlertContainer');
    
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'campaignAlertContainer';
        alertContainer.className = 'mt-3';
        
        // Insert after the first element in the modal body
        const modalBody = document.querySelector('#createCampaignModal .modal-body');
        if (modalBody) {
            modalBody.insertBefore(alertContainer, modalBody.firstChild);
        }
    }
    
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