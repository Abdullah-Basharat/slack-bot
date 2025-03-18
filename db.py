import sqlite3

# Connect to SQLite (or create the database if it doesn't exist)
conn = sqlite3.connect("messages.db")

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table with user_id and message_count fields
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE,
        message_count INTEGER DEFAULT 0
    )
''')

# Commit and close connection
conn.commit()
conn.close()

print("Database and table created successfully!")
