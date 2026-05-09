import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="ebay_saas.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """SaaS 상용화를 위한 테이블 스키마 초기화"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. 사용자 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    plan_type TEXT DEFAULT 'free',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 2. 상품(리스팅) 정보 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    source_url TEXT,
                    title TEXT,
                    description TEXT,
                    price_usd REAL,
                    category TEXT,
                    ebay_listing_id TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES Users(user_id)
                )
            ''')

            # 3. 이미지 관리 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ProductImages (
                    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    original_path TEXT,
                    processed_path TEXT,
                    is_main BOOLEAN DEFAULT 0,
                    sort_order INTEGER DEFAULT 0,
                    FOREIGN KEY(product_id) REFERENCES Products(product_id)
                )
            ''')

            # 4. 활동 로그
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ActivityLogs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 5. 비동기 작업 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS SourcingTasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task_type TEXT, 
                    status TEXT DEFAULT 'pending',
                    total_count INTEGER DEFAULT 0,
                    current_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def create_user(self, email):
        """신규 사용자 생성"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO Users (email) VALUES (?)", (email,))
                conn.commit()
                return True
        except Exception as e:
            print(f"DB User Error: {e}")
            return False

    def save_product(self, user_id, product_data):
        """수집된 상품 정보 및 이미지 경로 저장"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO Products (user_id, source_url, title, price_usd, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, product_data['url'], product_data['title'], 
                      product_data['price'], product_data['category']))
                
                product_id = cursor.lastrowid
                
                if 'image_paths' in product_data:
                    for idx, path in enumerate(product_data['image_paths']):
                        cursor.execute('''
                            INSERT INTO ProductImages (product_id, processed_path, sort_order, is_main)
                            VALUES (?, ?, ?, ?)
                        ''', (product_id, path, idx, 1 if idx == 0 else 0))
                
                conn.commit()
                return product_id
        except Exception as e:
            print(f"DB Save Error: {e}")
            return None

    def log_activity(self, user_id, action, details):
        """사용자의 모든 행동을 데이터로 기록"""
        with self._get_connection() as conn:
            conn.execute("INSERT INTO ActivityLogs (user_id, action, details) VALUES (?, ?, ?)",
                         (user_id, action, details))
            conn.commit()

    def get_analytics(self):
        """통계 데이터 추출"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            categories = cursor.execute("SELECT category, COUNT(*) as count FROM Products GROUP BY category ORDER BY count DESC LIMIT 5").fetchall()
            sources = cursor.execute("SELECT source_url, COUNT(*) as count FROM Products GROUP BY source_url ORDER BY count DESC LIMIT 5").fetchall()
            return {"categories": [dict(c) for c in categories], "sources": [dict(s) for s in sources]}

    def update_ebay_listing(self, product_id, listing_id):
        """최종 리스팅 성공 시 이베이 ID 업데이트"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Products SET ebay_listing_id = ?, status = 'listed' WHERE product_id = ?", 
                           (listing_id, product_id))
            conn.commit()

    def create_task(self, user_id, task_type, total_count=0):
        """신규 비동기 작업 등록"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO SourcingTasks (user_id, task_type, total_count, status)
                VALUES (?, ?, ?, 'processing')
            ''', (user_id, task_type, total_count))
            conn.commit()
            return cursor.lastrowid

    def update_task_progress(self, task_id, current_count):
        """작업 진행률 업데이트"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE SourcingTasks 
                SET current_count = ?, updated_at = CURRENT_TIMESTAMP
                WHERE task_id = ?
            ''', (current_count, task_id))
            conn.commit()

    def complete_task(self, task_id):
        """작업 완료 처리"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE SourcingTasks SET status = 'completed' WHERE task_id = ?", (task_id,))
            conn.commit()
