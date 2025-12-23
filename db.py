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
                     ai_summary=None, priority_reasoning=None, is_ai_processed=True):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        sql = """
        INSERT INTO complaints 
        (citizen_name, location, complaint_text, clean_text, category, priority, 
         ai_summary, priority_reasoning, is_ai_processed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (name, location, original_text, clean_text, category, priority,
                  ai_summary, priority_reasoning, is_ai_processed)
        cursor.execute(sql, values)
        connection.commit()

        print("Complaint inserted successfully!")

    except Exception as e:
        print("Failed to insert complaint:", e)

    finally:
        if connection and connection.is_connected():
            cursor.close()
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


def log_action(complaint_id, officer_id, action_text):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        sql = """
        INSERT INTO action_log (complaint_id, officer_id, action)
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (complaint_id, officer_id, action_text))
        connection.commit()

        print("Action logged!")

    except Exception as e:
        print("Failed to log action:", e)

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

