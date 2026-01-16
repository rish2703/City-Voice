"""
Create user and upvote tables for Reddit-like features
Run this script to set up the database tables
"""

import mysql.connector
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from database.db import get_connection

def create_user_tables():
    """Create users and upvotes tables"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            print("ERROR: Database connection failed!")
            return False
        
        cursor = connection.cursor()
        
        print("Creating tables...")
        
        # Create users table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_username (username),
                    INDEX idx_email (email)
                )
            """)
            print("[OK] Users table created")
        except mysql.connector.Error as e:
            if "already exists" in str(e).lower() or "Duplicate" in str(e):
                print("[INFO] Users table already exists")
            else:
                raise
        
        # Create upvotes table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS upvotes (
                    upvote_id INT AUTO_INCREMENT PRIMARY KEY,
                    complaint_id INT NOT NULL,
                    user_id INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    UNIQUE KEY unique_upvote (complaint_id, user_id),
                    INDEX idx_complaint (complaint_id),
                    INDEX idx_user (user_id)
                )
            """)
            print("[OK] Upvotes table created")
        except mysql.connector.Error as e:
            if "already exists" in str(e).lower() or "Duplicate" in str(e):
                print("[INFO] Upvotes table already exists")
            else:
                raise
        
        connection.commit()
        print("\n[SUCCESS] All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error creating tables: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Creating User Authentication and Upvote Tables")
    print("=" * 60)
    create_user_tables()
    print("=" * 60)

