"""
Upvote Management Functions
Handles upvoting complaints
"""

from database.db import get_connection

def upvote_complaint(complaint_id, user_id):
    """Add an upvote to a complaint"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            raise Exception("Database connection failed")
        
        cursor = connection.cursor()
        
        # Check if user already upvoted
        check_query = "SELECT upvote_id FROM upvotes WHERE complaint_id = %s AND user_id = %s"
        cursor.execute(check_query, (complaint_id, user_id))
        if cursor.fetchone():
            return {"success": False, "message": "You have already upvoted this complaint"}
        
        # Insert upvote
        insert_query = """
            INSERT INTO upvotes (complaint_id, user_id, created_at)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(insert_query, (complaint_id, user_id))
        connection.commit()
        
        return {"success": True, "message": "Upvoted successfully"}
        
    except Exception as e:
        if connection:
            connection.rollback()
        return {"success": False, "message": f"Upvote failed: {str(e)}"}
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def remove_upvote(complaint_id, user_id):
    """Remove an upvote from a complaint"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            raise Exception("Database connection failed")
        
        cursor = connection.cursor()
        
        delete_query = "DELETE FROM upvotes WHERE complaint_id = %s AND user_id = %s"
        cursor.execute(delete_query, (complaint_id, user_id))
        connection.commit()
        
        return {"success": True, "message": "Upvote removed"}
        
    except Exception as e:
        if connection:
            connection.rollback()
        return {"success": False, "message": f"Remove upvote failed: {str(e)}"}
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_upvote_count(complaint_id):
    """Get total upvote count for a complaint"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            return 0
        
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM upvotes WHERE complaint_id = %s"
        cursor.execute(query, (complaint_id,))
        result = cursor.fetchone()
        
        return result[0] if result else 0
        
    except Exception as e:
        return 0
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def has_user_upvoted(complaint_id, user_id):
    """Check if user has upvoted a complaint"""
    if not user_id:
        return False
    
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            return False
        
        cursor = connection.cursor()
        query = "SELECT upvote_id FROM upvotes WHERE complaint_id = %s AND user_id = %s"
        cursor.execute(query, (complaint_id, user_id))
        result = cursor.fetchone()
        
        return result is not None
        
    except Exception as e:
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def get_complaints_with_upvotes(user_id=None):
    """Get all complaints with their upvote counts"""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            return []
        
        cursor = connection.cursor()
        
        # Get complaints with upvote counts
        if user_id:
            query = """
                SELECT 
                    c.complaint_id, c.citizen_name, c.location, c.complaint_text, c.clean_text,
                    c.category, c.priority, c.status, c.zone, c.created_at, c.photo_after,
                    c.ai_summary, c.priority_reasoning, c.is_ai_processed, c.model_used, c.processing_time,
                    COALESCE(COUNT(DISTINCT u.upvote_id), 0) as upvote_count,
                    CASE WHEN EXISTS (
                        SELECT 1 FROM upvotes uv WHERE uv.complaint_id = c.complaint_id AND uv.user_id = %s
                    ) THEN 1 ELSE 0 END as user_upvoted
                FROM complaints c
                LEFT JOIN upvotes u ON c.complaint_id = u.complaint_id
                GROUP BY c.complaint_id
                ORDER BY upvote_count DESC, c.created_at DESC
            """
            cursor.execute(query, (user_id,))
        else:
            query = """
                SELECT 
                    c.complaint_id, c.citizen_name, c.location, c.complaint_text, c.clean_text,
                    c.category, c.priority, c.status, c.zone, c.created_at, c.photo_after,
                    c.ai_summary, c.priority_reasoning, c.is_ai_processed, c.model_used, c.processing_time,
                    COALESCE(COUNT(DISTINCT u.upvote_id), 0) as upvote_count,
                    0 as user_upvoted
                FROM complaints c
                LEFT JOIN upvotes u ON c.complaint_id = u.complaint_id
                GROUP BY c.complaint_id
                ORDER BY upvote_count DESC, c.created_at DESC
            """
            cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            complaint = dict(zip(columns, row))
            # Ensure upvote_count is an integer
            complaint['upvote_count'] = int(complaint.get('upvote_count', 0) or 0)
            results.append(complaint)
        
        return results
        
    except Exception as e:
        return []
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

