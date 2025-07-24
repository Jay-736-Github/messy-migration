# init_db.py
import sqlite3
from werkzeug.security import generate_password_hash

def initialize_database():
    """Wipes and re-populates the database with sample data."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Drop the table if it exists to ensure a clean slate
    cursor.execute("DROP TABLE IF EXISTS users")

    # Recreate the table
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Hash the passwords before inserting
    users_to_add = [
        ('John Doe', 'john@example.com', generate_password_hash('password123')),
        ('Jane Smith', 'jane@example.com', generate_password_hash('secret456')),
        ('Bob Johnson', 'bob@example.com', generate_password_hash('qwerty789'))
    ]

    cursor.executemany("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", users_to_add)

    conn.commit()
    conn.close()

# This part allows you to still run `python init_db.py` from the command line
if __name__ == '__main__':
    initialize_database()
    print("Database initialized with sample data (with hashed passwords).")