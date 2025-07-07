// Dashboard functionality

// Load dashboard page
async function loadDashboardPage() {
    // Update page title
    document.getElementById('pageTitle').textContent = 'Dashboard';
    
    // Clear page actions
    document.getElementById('pageActions').innerHTML = '';
    
    // Build dashboard HTML
    const html = `
        <div class="row">
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Email Lists</h5>
                        <div class="d-flex align-items-center">
                            <div class="display-4 me-3" id="listCount">-</div>
                            <div>
                                <div class="text-muted">Total Lists</div>
                                <a href="#" class="btn btn-sm btn-primary mt-2" onclick="loadPage('lists')">
                                    <i class="fas fa-plus me-1"></i> Create List
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">SMTP Servers</h5>
                        <div class="d-flex align-items-center">
                            <div class="display-4 me-3" id="smtpCount">-</div>
                            <div>
                                <div class="text-muted">Active Servers</div>
                                <a href="#" class="btn btn-sm btn-primary mt-2" onclick="loadPage('smtp')">
                                    <i class="fas fa-plus me-1"></i> Add Server
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Proxies</h5>
                        <div class="d-flex align-items-center">
                            <div class="display-4 me-3" id="proxyCount">-</div>
                            <div>
                                <div class="text-muted">Active Proxies</div>
                                <a href="#" class="btn btn-sm btn-primary mt-2" onclick="loadPage('proxies')">
                                    <i class="fas fa-plus me-1"></i> Add Proxy
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6 col-lg-3 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">Campaigns</h5>
                        <div class="d-flex align-items-center">
                            <div class="display-4 me-3" id="campaignCount">-</div>
                            <div>
                                <div class="text-muted">Total Campaigns</div>
                                <a href="#" class="btn btn-sm btn-primary mt-2" onclick="loadPage('campaigns')">
                                    <i class="fas fa-plus me-1"></i> New Campaign
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Set content
    document.getElementById('pageContent').innerHTML = html;
    
    // Load dashboard data
    loadDashboardData();
}

// Load dashboard data
async function loadDashboardData() {
    try {
        // Get lists
        const lists = await api.getLists();
        document.getElementById('listCount').textContent = lists.length;
        
        // Get SMTP servers
        const smtpServers = await api.getSmtpServers();
        document.getElementById('smtpCount').textContent = smtpServers.length;
        
        // Get proxies
        const proxies = await api.getProxies();
        document.getElementById('proxyCount').textContent = proxies.length;
        
        // Campaigns not implemented yet
        document.getElementById('campaignCount').textContent = '0';
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Error loading dashboard data', 'danger');
    }
}