-- Database schema for sender app

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lists table
CREATE TABLE IF NOT EXISTS lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contacts table
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    email TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES lists (id)
);

-- SMTP servers table
CREATE TABLE IF NOT EXISTS smtp_servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    host TEXT NOT NULL,
    port INTEGER NOT NULL,
    username TEXT,
    password TEXT,
    from_email TEXT,
    from_name TEXT,
    max_emails_per_day INTEGER DEFAULT 500,
    current_count INTEGER DEFAULT 0,
    require_auth BOOLEAN DEFAULT 1,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Proxies table
CREATE TABLE IF NOT EXISTS proxies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host TEXT NOT NULL,
    port INTEGER NOT NULL,
    username TEXT,
    password TEXT,
    proxy_type TEXT DEFAULT 'http',
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    list_id INTEGER NOT NULL,
    smtp_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    from_name TEXT DEFAULT '',
    from_email TEXT DEFAULT '',
    reply_to TEXT DEFAULT '',
    priority TEXT DEFAULT 'normal',
    enable_ip_rotation BOOLEAN DEFAULT 0,
    enable_random_subdomains BOOLEAN DEFAULT 0,
    enable_auto_spin BOOLEAN DEFAULT 1,
    delivery_mode TEXT DEFAULT 'normal',
    status TEXT DEFAULT 'draft',
    sent_emails INTEGER DEFAULT 0,
    total_emails INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES lists (id),
    FOREIGN KEY (smtp_id) REFERENCES smtp_servers (id)
);

-- Activity logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    campaign_name TEXT,
    action TEXT,
    details TEXT,
    status TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);