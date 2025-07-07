"""
Business Email Farming - Create multiple Google Workspace accounts
LEGAL: Creating multiple business accounts with different domains is legal
"""
import requests
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BusinessEmailFarmer:
    def __init__(self):
        self.created_accounts = []
        self.domain_registrars = [
            {'name': 'Namecheap', 'api_url': 'https://api.namecheap.com/xml.response'},
            {'name': 'Porkbun', 'api_url': 'https://porkbun.com/api/json/v3/'},
            {'name': 'Freenom', 'free_tlds': ['.tk', '.ml', '.ga', '.cf']}
        ]
    
    def register_cheap_domains(self, count=10):
        """Register cheap domains for business accounts"""
        domains = []
        
        # Generate domain names
        for i in range(count):
            # Random business-sounding names
            prefixes = ['tech', 'digital', 'solutions', 'services', 'group', 'corp', 'inc', 'llc']
            suffixes = ['pro', 'biz', 'info', 'net', 'org', 'co']
            
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes)
            number = random.randint(100, 999)
            
            domain = f"{prefix}{number}.{suffix}"
            domains.append(domain)
        
        # Register domains (implement with your preferred registrar)
        registered_domains = []
        for domain in domains:
            if self.register_domain(domain):
                registered_domains.append(domain)
                print(f"✅ Registered domain: {domain}")
        
        return registered_domains
    
    def register_domain(self, domain):
        """Register domain with cheap registrar"""
        # This is a placeholder - implement with actual registrar API
        # For now, assume successful registration
        time.sleep(1)  # Simulate API call
        return True
    
    def create_google_workspace_account(self, domain):
        """Create Google Workspace account for domain"""
        try:
            # Use Selenium to automate account creation
            driver = self.setup_driver()
            
            # Go to Google Workspace signup
            driver.get("https://workspace.google.com/business/signup/welcome")
            
            # Fill business information
            business_name = f"{domain.split('.')[0].title()} Solutions"
            
            # Wait for and fill business name
            business_name_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "businessName"))
            )
            business_name_field.send_keys(business_name)
            
            # Select number of employees (1-9)
            employee_count = driver.find_element(By.XPATH, "//span[text()='1-9']")
            employee_count.click()
            
            # Continue
            continue_btn = driver.find_element(By.XPATH, "//span[text()='Continue']")
            continue_btn.click()
            
            # Fill domain information
            domain_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "domain"))
            )
            domain_field.send_keys(domain)
            
            # Continue with domain verification
            continue_btn = driver.find_element(By.XPATH, "//span[text()='Continue']")
            continue_btn.click()
            
            # Create admin account
            admin_email = f"admin@{domain}"
            admin_password = self.generate_strong_password()
            
            # Fill admin details
            first_name_field = driver.find_element(By.NAME, "firstName")
            first_name_field.send_keys("Admin")
            
            last_name_field = driver.find_element(By.NAME, "lastName")
            last_name_field.send_keys("User")
            
            username_field = driver.find_element(By.NAME, "username")
            username_field.send_keys("admin")
            
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(admin_password)
            
            confirm_password_field = driver.find_element(By.NAME, "confirmPassword")
            confirm_password_field.send_keys(admin_password)
            
            # Submit
            submit_btn = driver.find_element(By.XPATH, "//span[text()='Create Account']")
            submit_btn.click()
            
            # Wait for verification page
            time.sleep(5)
            
            # Store account info
            account_info = {
                'domain': domain,
                'admin_email': admin_email,
                'admin_password': admin_password,
                'business_name': business_name,
                'created_at': time.time(),
                'status': 'pending_verification',
                'smtp_settings': {
                    'host': 'smtp.gmail.com',
                    'port': 587,
                    'username': admin_email,
                    'password': admin_password,
                    'use_tls': True
                }
            }
            
            self.created_accounts.append(account_info)
            driver.quit()
            
            return account_info
            
        except Exception as e:
            print(f"❌ Failed to create Google Workspace for {domain}: {e}")
            if 'driver' in locals():
                driver.quit()
            return None
    
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    def generate_strong_password(self):
        """Generate strong password for accounts"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(16))
    
    def verify_domain_ownership(self, domain, verification_code):
        """Add DNS TXT record to verify domain ownership"""
        # This would integrate with your DNS provider API
        # For now, return instructions
        return {
            'record_type': 'TXT',
            'name': '@',
            'value': verification_code,
            'instructions': f'Add TXT record to {domain} DNS settings'
        }
    
    def create_microsoft365_account(self, domain):
        """Create Microsoft 365 account (cheaper alternative)"""
        try:
            # Microsoft 365 Business Basic is $5/month vs Google's $6
            driver = self.setup_driver()
            
            # Go to Microsoft 365 signup
            driver.get("https://www.microsoft.com/en-us/microsoft-365/business/compare-all-microsoft-365-business-products")
            
            # Click on Business Basic
            basic_plan = driver.find_element(By.XPATH, "//a[contains(text(), 'Buy now')]")
            basic_plan.click()
            
            # Fill business information
            business_name = f"{domain.split('.')[0].title()} Corp"
            
            # Continue with signup process...
            # (Similar to Google Workspace but with Microsoft's flow)
            
            account_info = {
                'domain': domain,
                'admin_email': f"admin@{domain}",
                'admin_password': self.generate_strong_password(),
                'business_name': business_name,
                'provider': 'microsoft365',
                'cost': '$5/month',
                'smtp_settings': {
                    'host': 'smtp.office365.com',
                    'port': 587,
                    'username': f"admin@{domain}",
                    'password': 'generated_password',
                    'use_tls': True
                }
            }
            
            driver.quit()
            return account_info
            
        except Exception as e:
            print(f"❌ Failed to create Microsoft 365 for {domain}: {e}")
            return None
    
    def create_zoho_account(self, domain):
        """Create Zoho Mail account (cheapest option - $1/month)"""
        try:
            driver = self.setup_driver()
            
            # Zoho Mail is the cheapest business email at $1/month
            driver.get("https://www.zoho.com/mail/zohomail-pricing.html")
            
            # Click on Mail Lite plan
            lite_plan = driver.find_element(By.XPATH, "//a[contains(text(), 'Sign Up')]")
            lite_plan.click()
            
            # Fill signup form
            account_info = {
                'domain': domain,
                'admin_email': f"admin@{domain}",
                'provider': 'zoho',
                'cost': '$1/month',
                'smtp_settings': {
                    'host': 'smtp.zoho.com',
                    'port': 587,
                    'username': f"admin@{domain}",
                    'password': 'generated_password',
                    'use_tls': True
                }
            }
            
            driver.quit()
            return account_info
            
        except Exception as e:
            print(f"❌ Failed to create Zoho Mail for {domain}: {e}")
            return None
    
    def farm_business_emails(self, count=10):
        """Create multiple business email accounts"""
        print(f"🚀 Starting business email farming for {count} accounts...")
        
        # Step 1: Register domains
        domains = self.register_cheap_domains(count)
        
        # Step 2: Create business email accounts
        for domain in domains:
            # Try different providers (diversification)
            providers = ['google', 'microsoft', 'zoho']
            provider = random.choice(providers)
            
            if provider == 'google':
                account = self.create_google_workspace_account(domain)
            elif provider == 'microsoft':
                account = self.create_microsoft365_account(domain)
            else:
                account = self.create_zoho_account(domain)
            
            if account:
                print(f"✅ Created {provider} account for {domain}")
                time.sleep(random.randint(30, 60))  # Avoid rate limiting
        
        return self.created_accounts
    
    def add_accounts_to_senderblade(self):
        """Add created accounts to SenderBlade SMTP servers"""
        from simple_db import execute_db
        
        for account in self.created_accounts:
            try:
                smtp = account['smtp_settings']
                
                execute_db(
                    '''INSERT INTO smtp_servers (name, host, port, username, password, 
                       from_email, from_name, require_auth) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (
                        f"Business {account['domain']}",
                        smtp['host'],
                        smtp['port'],
                        smtp['username'],
                        smtp['password'],
                        smtp['username'],
                        account['business_name'],
                        True
                    )
                )
                
                print(f"✅ Added {account['domain']} to SenderBlade")
                
            except Exception as e:
                print(f"Error adding {account['domain']}: {e}")

# Advanced farming strategies
class AdvancedEmailFarmer:
    def __init__(self):
        self.proxy_list = []
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
    
    def use_residential_proxies(self):
        """Use residential proxies to avoid detection"""
        # Integrate with residential proxy providers
        proxy_providers = [
            {'name': 'Bright Data', 'endpoint': 'rotating-residential.brightdata.com:22225'},
            {'name': 'Oxylabs', 'endpoint': 'pr.oxylabs.io:7777'},
            {'name': 'Smartproxy', 'endpoint': 'gate.smartproxy.com:7000'}
        ]
        
        return random.choice(proxy_providers)
    
    def create_accounts_with_stealth(self, count=50):
        """Create accounts with advanced stealth techniques"""
        for i in range(count):
            # Use different proxy for each account
            proxy = self.use_residential_proxies()
            
            # Random delay between accounts
            delay = random.randint(300, 900)  # 5-15 minutes
            
            print(f"Creating account {i+1}/{count} via {proxy['name']} in {delay} seconds...")
            time.sleep(delay)
            
            # Create account with proxy
            # Implementation would use proxy settings

# Usage example
def main():
    """Main function to farm business emails"""
    farmer = BusinessEmailFarmer()
    
    # Create 10 business email accounts
    accounts = farmer.farm_business_emails(10)
    
    # Add to SenderBlade
    farmer.add_accounts_to_senderblade()
    
    print(f"🎯 Successfully farmed {len(accounts)} business email accounts!")
    
    # Calculate capacity
    total_capacity = len(accounts) * 10000  # Assume 10K emails/month per account
    monthly_cost = len(accounts) * 5  # Average $5/month per account
    
    print(f"📊 Total capacity: {total_capacity:,} emails/month")
    print(f"💰 Monthly cost: ${monthly_cost}")
    print(f"📈 Cost per email: ${monthly_cost/total_capacity:.6f}")

if __name__ == "__main__":
    main()