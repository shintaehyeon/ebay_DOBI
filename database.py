import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="dashboard/saas_data.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Users table (Plan management & Auth)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                plan TEXT DEFAULT 'Free', -- 'Free', 'Pro', 'Enterprise'
                ebay_token TEXT,
                shopify_shop_url TEXT,
                shopify_access_token TEXT,
                created_at DATETIME
            )
        ''')
        
        # 2. Sourcing logs (Market trend analysis)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS source_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp DATETIME,
                url TEXT,
                store_name TEXT, -- 'Musinsa', 'KREAM', 'Aebly', etc.
                category TEXT,
                price REAL,
                status TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # 3. Multi-channel listing status
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                channel TEXT, -- 'eBay', 'Shopify'
                external_id TEXT, -- ID from eBay/Shopify
                title TEXT,
                sku TEXT,
                timestamp DATETIME,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def register_user(self, email, plan='Free'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (email, plan, created_at) VALUES (?, ?, ?)', 
                           (email, plan, datetime.now()))
            conn.commit()
        except sqlite3.IntegrityError:
            print("User already exists.")
        conn.close()

    def log_activity(self, user_id, url, store_name, category, price):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO source_logs (user_id, timestamp, url, store_name, category, price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, datetime.now(), url, store_name, category, price, 'success'))
        conn.commit()
        conn.close()
