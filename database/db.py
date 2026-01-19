import mysql.connector

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",            # change if your username is different
            password="newpassword", # your MySQL password
            database="cityvoice"
        )
        
        return connection
    except Exception as e:
        print("Database connection failed:", e)
        return None


def insert_complaint(name, location, original_text, clean_text, category, priority, 
                     zone=None, ai_summary=None, priority_reasoning=None, is_ai_processed=True, address=None):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        if not connection:
            raise Exception("Database connection failed. Check MySQL is running and credentials are correct.")
        
        cursor = connection.cursor()

        sql = """
        INSERT INTO complaints 
        (citizen_name, location, complaint_text, clean_text, category, priority, zone,
         ai_summary, priority_reasoning, is_ai_processed, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (name, location, original_text, clean_text, category, priority, zone,
                  ai_summary, priority_reasoning, is_ai_processed, address)
        cursor.execute(sql, values)
        connection.commit()
        
        # Return the inserted complaint_id
        complaint_id = cursor.lastrowid
        print(f"Complaint inserted successfully! ID: {complaint_id}")
        return complaint_id

    except Exception as e:
        error_msg = f"Failed to insert complaint: {str(e)}"
        print(error_msg)
        # Re-raise exception so it can be caught and displayed in Streamlit
        raise Exception(error_msg)

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def update_status(complaint_id, new_status, image_path=None):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        if image_path:
            sql = "UPDATE complaints SET status = %s, photo_after = %s WHERE complaint_id = %s"
            cursor.execute(sql, (new_status, image_path, complaint_id))
        else:
            sql = "UPDATE complaints SET status = %s WHERE complaint_id = %s"
            cursor.execute(sql, (new_status, complaint_id))

        connection.commit()

        print("Status updated successfully!")

    except Exception as e:
        print("Failed to update status:", e)

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


def log_action(complaint_id, officer_id, action_text, image_path=None):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        sql = """
        INSERT INTO action_log (complaint_id, officer_id, action, image_path)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (complaint_id, officer_id, action_text, image_path))
        connection.commit()

        print("Action logged!")

    except Exception as e:
        print("Failed to log action:", e)

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

