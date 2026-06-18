import sqlite3

def initialize_radar_database():
    """
    Constructs the core relational database schema to manage subscriber profiles,
    billing state tiers ($9.99/mo access), and personalized user watchlists.
    """
    # Connect to local database file (it will be created automatically)
    conn = sqlite3.connect('liquid_radar.db')
    cursor = conn.cursor()
    
    print("🗄️ Initializing schema architecture...")

    # 1. Create Users Table (Handles authentication and subscription states)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            subscription_status TEXT DEFAULT 'active', -- 'active', 'canceled', 'past_due'
            billing_tier TEXT DEFAULT 'retail_standard', -- matches our $9.99 model
            signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Create Watchlist Table (Saves what assets each unique user wants to monitor)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_watchlists (
            watchlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            asset_ticker TEXT NOT NULL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # 3. Inject a Mock Premium User so we can test the subscription gate immediately
    try:
        cursor.execute('''
            INSERT INTO users (email, password_hash, subscription_status, billing_tier)
            VALUES ('founder@liquidradar.com', 'hashed_secure_password_123', 'active', 'retail_standard')
        ''')
        print("👤 Seeded mock subscriber profile: founder@liquidradar.com")
    except sqlite3.IntegrityError:
        # Mock user already exists from a previous run, safe to ignore
        pass

    conn.commit()
    conn.close()
    print("✅ Database 'liquid_radar.db' built and optimized successfully!")

if __name__ == "__main__":
    initialize_radar_database()