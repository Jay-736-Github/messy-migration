## Overall Structure Change

### Problem:
All the code was in a single file (`app.py`). This makes it messy and hard to manage as the project grows. The way the database was accessed wasn’t safe for a real-world application.

### Solution:

The code was split into two files for better organization. `app.py` now exclusively manages API routes and request/response logic. All database interactions were moved into a new `db.py` module. This module also handles creating a fresh, safe database connection for each request and closing it afterward, preventing data corruption.

> This was entirely my idea; AI did not suggest this structure — I only used it to help rectify the functions in `db.py`.

## Endpoint by Endpoint Fixes

### Get All Users & Get Specific User (`GET /users`, `GET /user/<id>`)

#### Problem:
- The database queries were unsafe and could be attacked (SQL Injection).
- The API sent back data as a plain string, not the standard JSON format.
- If a user wasn’t found, it didn’t return a proper error code.

#### Solution:
- The unsafe queries were replaced with parameterized queries (using `?` placeholders) to prevent SQL Injection.
- API responses were changed from plain strings to proper JSON format using `jsonify`.
- The endpoint now correctly returns a `404 Not Found` error if a user ID does not exist.

### Create User (`POST /users`)

#### Problem:
- Passwords were saved as plain text.
- The database query was unsafe.
- It didn’t check if the user provided all the required information (`name`, `email`, `password`).
- It also didn’t handle cases where an email was already in use.

#### Solution:
- Plain-text passwords are now hashed using `generate_password_hash` from the `werkzeug` library before being stored.
- The database `INSERT` query was secured using parameterization.
- Added a check to validate that the incoming JSON contains all required fields, returning a `400 Bad Request` if not.
- The code now handles `IntegrityError` to return a `409 Conflict` status if the email already exists.
- Returns a `201 Created` status on success.

### Update User (`PUT /user/<id>`)

#### Problem:
- The database query was unsafe.
- It didn’t check if the user sent the data needed for the update.

#### Solution:
- The `UPDATE` query was secured using parameterization.
- Added validation to ensure the required fields are present.
- Returns a `404 Not Found` error if the user ID to be updated does not exist.

### Delete User (`DELETE /user/<id>`)

#### Problem:
- The database query was unsafe.

#### Solution:
- The `DELETE` query was secured using parameterization.
- Returns the standard `204 No Content` status code upon successful deletion to indicate success without a message body.

### Search Users (`GET /search`)

#### Problem:
- The search query was not safe and was a high risk for SQL injection.

#### Solution:
- The `SELECT` query using the `LIKE` clause was secured with a parameterized query, which is crucial for preventing injection in search fields.

### Login (`POST /login`)

#### Problem:
- The app checked for the real password directly from the database, which is very insecure.
- The query was also unsafe.
- A failed login didn’t return the correct error code.

#### Solution:
- The login logic was completely rewritten. It now first safely fetches a user by their email.
- If a user is found, it uses `check_password_hash` to compare the provided password against the stored hash.
- A failed attempt now correctly returns a `401 Unauthorized` error.

## Other Important Fixes

### Database Setup (`init_db.py`)

- The initial setup script was updated to save hashed passwords for the sample users, so they can actually log in.
- It also now cleans the database before adding the sample data to prevent errors.

### Testing (`test_app.py`)

- The original project had no tests.
- I created a full test file that checks every single API endpoint for both success and failure cases.
- This proves that the refactored code works correctly and is reliable.

### Any assumptions or trade-offs
#### Assumption : 
I assumed the database schema didn’t need any changes — like adding new fields or modifying table structure. The main goal was to clean up and secure the existing application code, not redesign the data model.

#### Trade-off :
I chose to open a fresh database connection for every operation. It’s not the most optimized approach for large-scale apps, but for this small project, it keeps things simple and avoids issues like shared connections or locks. In real-world high-traffic systems, I’d use a proper connection pool — but here, clarity and safety felt more important than squeezing out extra performance.

## AI Usage

For this assignment, I have used GEMINI as a collaborative tool and guide. Here is how it helped:

### Identifying Problems:
I used the AI to do an initial analysis of the code, which helped me quickly identify the major security risks like SQL injection and plain-text passwords.

### Guidance and Examples:
When I needed to fix a problem, I asked the AI for guidance. For example, it provided clear code examples for how to fix SQL injection using parameterized queries and how to properly hash passwords.

### Debugging:
When my tests failed, the AI helped me understand the error messages and suggested the correct fix.

### This File:
Of course, this file was created by GEMINI, but the formatting was done by me because it had used some random emojis and was a little unorganized.

## Final Note

- Essentially, the AI acted as a pair programmer and a knowledgeable mentor, helping me work through the codebase efficiently and ensuring the final result was high quality. However, I made sure to thoroughly understand the codebase myself—how each function operates, how to approach and solve problems, and which parts of the code need to be rectified. I believe this is an effective way of learning, and I’m confident that it will strengthen my coding and debugging skills even further in the future.
  
- I’ve completed the core requirements, and I’ll continue to make thoughtful improvements if any new ideas come to mind before the deadline.
