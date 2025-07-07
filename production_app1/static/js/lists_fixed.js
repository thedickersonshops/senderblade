// Lists functionality - Fixed version

// Global variables
let lists = [];

// Load lists page
async function loadListsPage() {
    // Update page title
    document.getElementById('pageTitle').textContent = 'Email Lists';
    
    // Add action buttons
    document.getElementById('pageActions').innerHTML = `
        <button class="btn btn-primary" id="createListBtn">
            <i class="fas fa-plus me-1"></i> Create List
        </button>
    `;
    
    // Add event listener for create list button
    document.getElementById('createListBtn').addEventListener('click', showCreateListModal);
    
    // Load lists
    await loadLists();
}

// Load lists
async function loadLists() {
    try {
        // Show loading
        document.getElementById('pageContent').innerHTML = `
            <div class="d-flex justify-content-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        // Get lists
        lists = await api.getLists();
        
        // Build HTML
        let html = '';
        
        if (lists.length === 0) {
            html = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i> No email lists found. Create your first list to get started.
                </div>
            `;
        } else {
            html = `
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Email Lists</h5>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Contacts</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${lists.map(list => `
                                    <tr>
                                        <td>${list.name}</td>
                                        <td>${list.contact_count}</td>
                                        <td>${formatDate(list.created_at)}</td>
                                        <td>
                                            <button class="btn btn-sm btn-primary view-list" data-id="${list.id}">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button class="btn btn-sm btn-danger delete-list" data-id="${list.id}" data-name="${list.name}">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
        
        // Set content
        document.getElementById('pageContent').innerHTML = html;
        
        // Add event listeners
        document.querySelectorAll('.view-list').forEach(button => {
            button.addEventListener('click', function() {
                const listId = this.getAttribute('data-id');
                viewList(listId);
            });
        });
        
        document.querySelectorAll('.delete-list').forEach(button => {
            button.addEventListener('click', function() {
                const listId = this.getAttribute('data-id');
                const listName = this.getAttribute('data-name');
                deleteList(listId, listName);
            });
        });
    } catch (error) {
        console.error('Error loading lists:', error);
        showAlert('Error loading lists: ' + error.message, 'danger');
    }
}

// Show create list modal
function showCreateListModal() {
    // Reset form
    document.getElementById('createListForm').reset();
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('createListModal'));
    modal.show();
    
    // Add event listener for save button
    document.getElementById('saveListBtn').onclick = saveList;
}

// Save list
async function saveList() {
    try {
        const name = document.getElementById('listName').value.trim();
        const description = document.getElementById('listDescription').value.trim();
        
        if (!name) {
            showAlert('Please enter a list name', 'danger');
            return;
        }
        
        // Disable button
        const saveBtn = document.getElementById('saveListBtn');
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
        
        // Create list
        const list = await api.createList(name, description);
        
        // Hide modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('createListModal'));
        modal.hide();
        
        // Show success message
        showAlert('List created successfully', 'success');
        
        // Reload lists
        await loadLists();
    } catch (error) {
        console.error('Error saving list:', error);
        showAlert('Error saving list: ' + error.message, 'danger');
    } finally {
        // Reset button
        const saveBtn = document.getElementById('saveListBtn');
        saveBtn.disabled = false;
        saveBtn.innerHTML = 'Create List';
    }
}

// View list
async function viewList(listId) {
    try {
        // Show loading
        document.getElementById('pageContent').innerHTML = `
            <div class="d-flex justify-content-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        
        // Get list
        const list = await api.getList(listId);
        
        // Update page title
        document.getElementById('pageTitle').textContent = list.name;
        
        // Update action buttons
        document.getElementById('pageActions').innerHTML = `
            <button class="btn btn-primary" id="uploadContactsBtn" data-id="${list.id}" data-name="${list.name}">
                <i class="fas fa-upload me-1"></i> Upload Contacts
            </button>
            <button class="btn btn-danger" id="deleteListBtn" data-id="${list.id}" data-name="${list.name}">
                <i class="fas fa-trash me-1"></i> Delete List
            </button>
        `;
        
        // Add event listeners
        document.getElementById('uploadContactsBtn').addEventListener('click', function() {
            const listId = this.getAttribute('data-id');
            const listName = this.getAttribute('data-name');
            showUploadContactsModal(listId, listName);
        });
        
        document.getElementById('deleteListBtn').addEventListener('click', function() {
            const listId = this.getAttribute('data-id');
            const listName = this.getAttribute('data-name');
            deleteList(listId, listName);
        });
        
        // Get contacts
        const contacts = await api.getContacts(listId);
        
        // Build HTML
        let html = `
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="mb-0">List Details</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Name:</strong> ${list.name}</p>
                            <p><strong>Description:</strong> ${list.description || 'N/A'}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Contacts:</strong> ${list.contact_count}</p>
                            <p><strong>Created:</strong> ${formatDate(list.created_at)}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        if (contacts.length === 0) {
            html += `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i> No contacts in this list. Upload contacts to get started.
                </div>
            `;
        } else {
            html += `
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Contacts</h5>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>Email</th>
                                    <th>First Name</th>
                                    <th>Last Name</th>
                                    <th>Added</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${contacts.map(contact => `
                                    <tr>
                                        <td>${contact.email}</td>
                                        <td>${contact.first_name || '-'}</td>
                                        <td>${contact.last_name || '-'}</td>
                                        <td>${formatDate(contact.created_at)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
        
        // Set content
        document.getElementById('pageContent').innerHTML = html;
    } catch (error) {
        console.error('Error viewing list:', error);
        showAlert('Error viewing list: ' + error.message, 'danger');
    }
}

// Delete list
async function deleteList(listId, listName) {
    try {
        // Confirm deletion
        if (!confirm(`Are you sure you want to delete "${listName}"? This cannot be undone.`)) {
            return;
        }
        
        // Delete list
        await api.deleteList(listId);
        
        // Show success message
        showAlert('List deleted successfully', 'success');
        
        // Reload lists
        await loadLists();
    } catch (error) {
        console.error('Error deleting list:', error);
        showAlert('Error deleting list: ' + error.message, 'danger');
    }
}

// Show upload contacts modal
function showUploadContactsModal(listId, listName) {
    // Reset form
    document.getElementById('uploadContactsForm').reset();
    
    // Set list ID
    document.getElementById('uploadListId').value = listId;
    
    // Update modal title
    document.getElementById('uploadContactsModalLabel').textContent = `Upload Contacts to ${listName}`;
    
    // Reset buttons
    document.getElementById('uploadContactsBtn').style.display = 'block';
    document.getElementById('nextStepBtn').style.display = 'none';
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('uploadContactsModal'));
    modal.show();
    
    // Add event listener for upload button
    document.getElementById('uploadContactsBtn').onclick = uploadContacts;
}

// Upload contacts
async function uploadContacts() {
    try {
        const listId = document.getElementById('uploadListId').value;
        const fileInput = document.getElementById('contactsFile');
        const enrichContacts = document.getElementById('enrichContacts').checked;
        
        if (!fileInput.files || fileInput.files.length === 0) {
            showAlert('Please select a file', 'danger');
            return;
        }
        
        // Disable button
        const uploadBtn = document.getElementById('uploadContactsBtn');
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
        
        // Read file
        const file = fileInput.files[0];
        const reader = new FileReader();
        
        reader.onload = async function(e) {
            try {
                const content = e.target.result;
                const contacts = parseCSV(content);
                
                if (contacts.length === 0) {
                    showAlert('No valid contacts found in the file', 'danger');
                    uploadBtn.disabled = false;
                    uploadBtn.innerHTML = 'Upload';
                    return;
                }
                
                console.log('Parsed contacts:', contacts);
                
                // Upload contacts
                const addedCount = await api.addContacts(listId, contacts);
                
                // Enrich contacts if needed
                if (enrichContacts) {
                    uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enriching...';
                    
                    const enrichedData = await api.enrichContacts(contacts);
                    
                    // Update contacts with enriched data
                    const enrichedContacts = [];
                    
                    for (const email in enrichedData) {
                        const enriched = enrichedData[email];
                        const contact = {
                            email: email,
                            first_name: enriched.first_name,
                            last_name: enriched.last_name,
                            custom_fields: {
                                company: enriched.company,
                                job_title: enriched.job_title,
                                social_profiles: enriched.social_profiles,
                                source: enriched.source,
                                confidence_score: enriched.confidence_score
                            }
                        };
                        enrichedContacts.push(contact);
                    }
                    
                    console.log('Enriched contacts:', enrichedContacts);
                    
                    if (enrichedContacts.length > 0) {
                        await api.addContacts(listId, enrichedContacts);
                    }
                }
                
                // Show success message
                showAlert(`${addedCount} contacts added successfully`, 'success');
                
                // Update buttons
                uploadBtn.style.display = 'none';
                document.getElementById('nextStepBtn').style.display = 'block';
                
                // Add event listener for next button
                document.getElementById('nextStepBtn').addEventListener('click', function() {
                    // Hide modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('uploadContactsModal'));
                    modal.hide();
                    
                    // View list
                    viewList(listId);
                });
            } catch (error) {
                console.error('Error processing file:', error);
                showAlert('Error processing file: ' + error.message, 'danger');
                
                // Reset button
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = 'Upload';
            }
        };
        
        reader.readAsText(file);
    } catch (error) {
        console.error('Error uploading contacts:', error);
        showAlert('Error uploading contacts: ' + error.message, 'danger');
        
        // Reset button
        const uploadBtn = document.getElementById('uploadContactsBtn');
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = 'Upload';
    }
}