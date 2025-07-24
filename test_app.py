import pytest
import json
from app import app
from init_db import initialize_database # Import our initialization function

# This pytest fixture sets up a test client for the Flask app.
# It runs before each test function that uses it as an argument.
@pytest.fixture
def client():
    """Setup the test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Before each test, we initialize a clean database to ensure tests are independent of each other so that they will not cause any conflicts in case.
        initialize_database()
        yield client

# Below are the test cases are created for each endpoint ensuring their proper functioning

def test_home(client):
    """Test to see if the home page is running."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"User Management System API is running." in response.data

def test_get_all_users(client):
    """Test to get all the users from /users."""
    response = client.get('/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    # The init_db script contains 3 users for now, so we expect 3 here.
    assert len(data) == 3
    assert data[0]['name'] == 'John Doe'

def test_get_specific_user_success(client):
    """Test to get one user that exists in the database."""
    response = client.get('/user/1') # John Doe(from init_db.py)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'John Doe'
    assert data['email'] == 'john@example.com'
    assert 'password' not in data # Ensuring that the password hash must not exposed.

def test_get_user_not_found(client):
    """Test to get a user that doesn't exist."""
    response = client.get('/user/9999') # If the id doesn't exists in the database
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == 'User not found'

def test_create_user_success(client):
    """Test to create a new user successfully."""
    new_user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "a-secure-password"
    }
    response = client.post('/users', json=new_user_data)
    assert response.status_code == 201 # 201 Created
    data = json.loads(response.data)
    assert data['name'] == new_user_data['name']
    assert data['email'] == new_user_data['email']

def test_create_user_failures(client):
    """Testing the cases where creating a user might fail."""
    # Case 1: Any missing data
    response = client.post('/users', json={"name": "Only Name"})
    assert response.status_code == 400 # Bad Request
    data = json.loads(response.data)
    assert "Missing data" in data['error']

    # Case 2: Duplicate email
    duplicate_user_data = {
        "name": "Another John",
        "email": "john@example.com", # If the email exists already in the database
        "password": "password123"
    }
    response = client.post('/users', json=duplicate_user_data)
    assert response.status_code == 409 # Reflecting Conflict 
    data = json.loads(response.data)
    assert data['error'] == 'Email already exists'

def test_update_user_success(client):
    """Test to update a user successfully."""
    update_data = {"name": "Johnathan Doe", "email": "john.doe@new.com"}
    response = client.put('/user/1', json=update_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == 1
    assert data['name'] == "Johnathan Doe"
    assert data['email'] == "john.doe@new.com"

def test_update_user_failures(client):
    """Testing the cases where updating a user might fail."""
    # Case 1: User not found
    response = client.put('/user/9999', json={"name": "Ghost", "email": "ghost@example.com"})
    assert response.status_code == 404

    # Case 2: Any missing data
    response = client.put('/user/1', json={"name": "Just a name"})
    assert response.status_code == 400

def test_delete_user_success(client):
    """Test to delete a user successfully."""
    # First, confirm the user exists
    get_response = client.get('/user/2')
    assert get_response.status_code == 200

    # Now, delete the user
    delete_response = client.delete('/user/2')
    assert delete_response.status_code == 204 # No Content

    # Finally, confirm the user is gone
    get_response_after_delete = client.get('/user/2')
    assert get_response_after_delete.status_code == 404

def test_delete_user_not_found(client):
    """Test to delete a user that doesn't exist."""
    response = client.delete('/user/9999')
    assert response.status_code == 404

def test_search_user(client):
    """Testing the search function."""
    # Search for "Smith", should find Jane Smith
    response = client.get('/search?name=Smith')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['name'] == 'Jane Smith'

    # Search for "John", should find John Doe and Bob Johnson
    response = client.get('/search?name=John')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2

def test_login_success(client):
    """Testing a smooth/successfull login."""
    login_data = {"email": "jane@example.com", "password": "secret456"}
    response = client.post('/login', json=login_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['user']['email'] == 'jane@example.com'

def test_login_failures(client):
    """Testing a failed/unsuccessfull login."""
    # Case 1: Wrong password
    response = client.post('/login', json={"email": "jane@example.com", "password": "wrongpassword"})
    assert response.status_code == 401 # Unauthorized

    # Case 2: User does not exist
    response = client.post('/login', json={"email": "ghost@example.com", "password": "password"})
    assert response.status_code == 401

    # Case 3: Any missing credentials
    response = client.post('/login', json={"email": "jane@example.com"})
    assert response.status_code == 400
