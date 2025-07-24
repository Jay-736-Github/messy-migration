import sqlite3

DATABASE_NAME = 'users.db'

def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect(DATABASE_NAME)
    # This makes the connection return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row
    return conn

def user_to_dict(user_row):
    """Converts a user row from the database into a dictionary, omitting the password."""
    if user_row is None:
        return None
    return {
        'id': user_row['id'],
        'name': user_row['name'],
        'email': user_row['email']
    }

# Here I have create one function for each database operation

def get_all_users_db():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [user_to_dict(user) for user in users]

def get_user_by_id_db(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user_to_dict(user)

def get_user_by_email_for_auth_db(email):
    """Special function for authentication that returns the full user row, including hash."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

def create_user_db(name, email, hashed_password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
        new_user_id = cursor.lastrowid
        conn.commit()
        return get_user_by_id_db(new_user_id)
    except sqlite3.IntegrityError:
        return None # Indicates that the email already exists
    finally:
        conn.close()

def update_user_db(user_id, name, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()
    if updated_rows > 0:
        return get_user_by_id_db(user_id)
    return None

def delete_user_db(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()
    return deleted_rows > 0

def search_users_by_name_db(name):
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users WHERE name LIKE ?", ('%' + name + '%',)).fetchall()
    conn.close()
    return [user_to_dict(user) for user in users]