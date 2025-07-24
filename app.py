from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import db # To import our new database module

app = Flask(__name__)

@app.route('/')
def home():
    """Health check endpoint."""
    return "User Management System API is running."

@app.route('/users', methods=['GET'])
def get_all_users():
    """Gets all users."""
    users = db.get_all_users_db()
    return jsonify(users)

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Gets a specific user by their ID."""
    user = db.get_user_by_id_db(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/users', methods=['POST'])
def create_user():
    """Creates a new user."""
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'email', 'password')):
        return jsonify({"error": "Missing data. Required fields: name, email, password"}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = db.create_user_db(data['name'], data['email'], hashed_password)
    
    if new_user is None:
        return jsonify({"error": "Email already exists"}), 409 # Conflict 

    return jsonify(new_user), 201 # For successfull creation

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Updates a user's name and email."""
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'email')):
        return jsonify({"error": "Missing data. Required fields: name, email"}), 400
    
    updated_user = db.update_user_db(user_id, data['name'], data['email'])
    
    if updated_user:
        return jsonify(updated_user)
    return jsonify({"error": "User not found"}), 404

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deletes a user."""
    if db.delete_user_db(user_id):
        return '', 204 # No Content
    return jsonify({"error": "User not found"}), 404

@app.route('/search', methods=['GET'])
def search_users():
    """Searches for users by name."""
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Query parameter 'name' is required"}), 400
    
    users = db.search_users_by_name_db(name)
    return jsonify(users)

@app.route('/login', methods=['POST'])
def login():
    """Handles user login."""
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({"error": "Missing email or password"}), 400

    user = db.get_user_by_email_for_auth_db(data['email'])

    if user and check_password_hash(user['password'], data['password']):
        # Important Safety Step : Not to send the password hash back to the client
        user_data = db.user_to_dict(user)
        return jsonify({"status": "success", "user": user_data})
    
    return jsonify({"status": "failed", "error": "Invalid credentials"}), 401 # Unauthorized

if __name__ == '__main__':
    # Debug mode should be False in production
    app.run(host='0.0.0.0', port=5009, debug=True)