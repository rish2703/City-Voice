"""
User Authentication Functions
Handles user registration, login, and session management
"""

import mysql.connector
from database.db import get_connection
import hashlib

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """Register a new user"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            raise Exception("Database connection failed")
        
        cursor = connection.cursor()
        
        # Strip whitespace from inputs
        username = username.strip()
        email = email.strip()
        password = password.strip()
        
        # Validate inputs
        if not username or not email or not password:
            return {"success": False, "message": "All fields are required"}
        
        if len(password) < 6:
            return {"success": False, "message": "Password must be at least 6 characters"}
        
        # Check if username already exists
        check_query = "SELECT user_id FROM users WHERE username = %s OR email = %s"
        cursor.execute(check_query, (username, email))
        if cursor.fetchone():
            return {"success": False, "message": "Username or email already exists"}
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Insert new user
        insert_query = """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(insert_query, (username, email, hashed_password))
        connection.commit()
        
        user_id = cursor.lastrowid
        return {"success": True, "user_id": user_id, "message": "User registered successfully"}
        
    except Exception as e:
        if connection:
            connection.rollback()
        return {"success": False, "message": f"Registration failed: {str(e)}"}
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def login_user(username, password):
    """Authenticate user login"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            raise Exception("Database connection failed")
        
        cursor = connection.cursor()
        
        # Strip whitespace from inputs
        username = username.strip()
        password = password.strip()
        
        # Validate inputs
        if not username or not password:
            return {"success": False, "message": "Username and password are required"}
        
        # Hash password and check
        hashed_password = hash_password(password)
        
        # Try exact match first
        query = "SELECT user_id, username, email FROM users WHERE username = %s AND password_hash = %s"
        cursor.execute(query, (username, hashed_password))
        result = cursor.fetchone()
        
        if result:
            return {
                "success": True,
                "user_id": result[0],
                "username": result[1].strip(),  # Return cleaned username
                "email": result[2]
            }
        else:
            # Check if username exists (for better error message)
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return {"success": False, "message": "Invalid password"}
            else:
                return {"success": False, "message": "Invalid username or password"}
            
    except Exception as e:
        return {"success": False, "message": f"Login failed: {str(e)}"}
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_user_by_id(user_id):
    """Get user information by user_id"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            return None
        
        cursor = connection.cursor()
        query = "SELECT user_id, username, email, created_at FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        
        if result:
            return {
                "user_id": result[0],
                "username": result[1],
                "email": result[2],
                "created_at": result[3]
            }
        return None
        
    except Exception as e:
        return None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

