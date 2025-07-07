// Direct fix for upload button

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Direct upload fix loaded');
    
    // Fix for upload contacts modal
    const uploadModal = document.getElementById('uploadContactsModal');
    if (uploadModal) {
        uploadModal.addEventListener('shown.bs.modal', function() {
            console.log('Upload modal shown, attaching event listener');
            
            // Get the upload button
            const uploadBtn = document.getElementById('uploadContactsBtn');
            
            // Remove existing event listeners by cloning
            const newUploadBtn = uploadBtn.cloneNode(true);
            uploadBtn.parentNode.replaceChild(newUploadBtn, uploadBtn);
            
            // Add direct event listener
            document.getElementById('uploadContactsBtn').addEventListener('click', function() {
                console.log('Upload button clicked');
                directUploadContacts();
            });
        });
    }
});

// Direct upload contacts function
async function directUploadContacts() {
    try {
        console.log('Direct upload contacts function called');
        
        const listId = document.getElementById('uploadListId').value;
        const fileInput = document.getElementById('contactsFile');
        const enrichContacts = document.getElementById('enrichContacts').checked;
        
        console.log('List ID:', listId);
        console.log('File selected:', fileInput.files.length > 0);
        console.log('Enrich contacts:', enrichContacts);
        
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
                console.log('File content length:', content.length);
                
                const contacts = parseCSV(content);
                console.log('Parsed contacts:', contacts.length);
                
                if (contacts.length === 0) {
                    showAlert('No valid contacts found in the file', 'danger');
                    uploadBtn.disabled = false;
                    uploadBtn.innerHTML = 'Upload';
                    return;
                }
                
                // Upload contacts
                console.log('Sending contacts to API:', contacts);
                const addedCount = await api.addContacts(listId, contacts);
                console.log('Added contacts count:', addedCount);
                
                // Enrich contacts if needed
                if (enrichContacts) {
                    uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enriching...';
                    
                    console.log('Enriching contacts...');
                    const enrichedData = await api.enrichContacts(contacts);
                    console.log('Enriched data received:', Object.keys(enrichedData).length);
                    
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
                    
                    console.log('Enriched contacts to update:', enrichedContacts.length);
                    
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
                const nextBtn = document.getElementById('nextStepBtn');
                const newNextBtn = nextBtn.cloneNode(true);
                nextBtn.parentNode.replaceChild(newNextBtn, nextBtn);
                
                document.getElementById('nextStepBtn').addEventListener('click', function() {
                    console.log('Next button clicked');
                    
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