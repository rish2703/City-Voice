"""
Database Migration Script - Add AI Columns to complaints table

This script adds new columns to support AI-generated insights:
- ai_summary: AI-generated summary of the complaint
- priority_reasoning: Explanation for why AI assigned the priority
- is_ai_processed: Flag indicating if AI was used (vs fallback)
- model_used: Track which AI model processed it
- processing_time: Time taken for AI analysis

Run this ONCE before using the AI features.
"""

import mysql.connector
from database.db import get_connection

def run_migration():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        print("Starting database migration...")
        
        # Add ai_summary column
        try:
            cursor.execute("""
                ALTER TABLE complaints 
                ADD COLUMN ai_summary TEXT DEFAULT NULL
            """)
            print("✓ Added ai_summary column")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("• ai_summary column already exists")
            else:
                raise
        
        # Add priority_reasoning column
        try:
            cursor.execute("""
                ALTER TABLE complaints 
                ADD COLUMN priority_reasoning TEXT DEFAULT NULL
            """)
            print("✓ Added priority_reasoning column")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("• priority_reasoning column already exists")
            else:
                raise
        
        # Add is_ai_processed column
        try:
            cursor.execute("""
                ALTER TABLE complaints 
                ADD COLUMN is_ai_processed BOOLEAN DEFAULT TRUE
            """)
            print("✓ Added is_ai_processed column")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("• is_ai_processed column already exists")
            else:
                raise
        
        # Add model_used column
        try:
            cursor.execute("""
                ALTER TABLE complaints 
                ADD COLUMN model_used VARCHAR(50) DEFAULT 'gpt-4o-mini'
            """)
            print("✓ Added model_used column")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("• model_used column already exists")
            else:
                raise
        
        # Add processing_time column
        try:
            cursor.execute("""
                ALTER TABLE complaints 
                ADD COLUMN processing_time FLOAT DEFAULT NULL
            """)
            print("✓ Added processing_time column")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("• processing_time column already exists")
            else:
                raise
        
        connection.commit()
        print("\n✅ Migration completed successfully!")
        print("\nYou can now use AI features in your City Voice app.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if connection:
            connection.rollback()
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


if __name__ == "__main__":
    print("=" * 50)
    print("City Voice - AI Database Migration")
    print("=" * 50)
    run_migration()
