import sqlite3

def upsert_user(user_id):
    # Connect to the SQLite database
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()

    # Single query to insert or update message_count
    cursor.execute('''
        INSERT INTO user_messages (user_id, message_count)
        VALUES (?, 1)
        ON CONFLICT(user_id) 
        DO UPDATE SET message_count = message_count + 1
    ''', (user_id,))

    # Commit and close the connection
    conn.commit()
    conn.close()

    print(f"User {user_id} updated successfully!")

def get_message_count(user_id):
    # Connect to the SQLite database
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()

    # Query to get the message_count for the given user_id
    cursor.execute("SELECT message_count FROM user_messages WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()  # Fetch the result

    conn.close()

    if result:  # If user exists, return the count
        return result[0]
    else:  # If user does not exist, return None or 0
        return 0  
