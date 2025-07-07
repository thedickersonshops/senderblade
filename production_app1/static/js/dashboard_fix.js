// Dashboard fix script
document.addEventListener('DOMContentLoaded', function() {
    // Load dashboard on page load with error handling
    try {
        loadDashboard().catch(error => {
            console.error('Error loading dashboard:', error);
            // Show a fallback dashboard if there's an error
            document.getElementById('pageTitle').textContent = 'Dashboard';
            document.getElementById('pageActions').innerHTML = '';
            document.getElementById('pageContent').innerHTML = `
                <div class="row">
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5>Email Lists</h5>
                                <h2>0</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5>SMTP Servers</h5>
                                <h2>0</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5>Proxies</h5>
                                <h2>0</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5>Campaigns</h5>
                                <h2>0</h2>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        console.error('Error in dashboard initialization:', error);
    }
});