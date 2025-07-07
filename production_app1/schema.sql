-- Database schema for production app

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
    custom_fields TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES lists (id)
);

-- SMTP servers table
CREATE TABLE IF NOT EXISTS smtp_servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    host TEXT NOT NULL,
    port INTEGER NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    from_email TEXT NOT NULL,
    from_name TEXT,
    max_emails_per_day INTEGER DEFAULT 500,
    current_count INTEGER DEFAULT 0,
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
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES lists (id),
    FOREIGN KEY (smtp_id) REFERENCES smtp_servers (id)
);