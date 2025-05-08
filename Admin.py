from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import re


app = Flask(__name__)


CORS(app, origins=["https://login-system-lac-three.vercel.app", "http://localhost:5173"])

client = MongoClient("mongodb://loginsystembackend-1.onrender.com")
db = client.mydatabase  
users_collection = db.users 


def validate_email(email):
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email)

# Route to handle user sign-up
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()  # Get data from request

    # Extract form data
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    confirm_email = data.get('confirmEmail')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    # Validation
    if not first_name or not last_name or not email or not confirm_email or not password or not confirm_password:
        return jsonify({"message": "All fields are required."}), 400

    if email != confirm_email:
        return jsonify({"message": "Emails do not match."}), 400

    if password != confirm_password:
        return jsonify({"message": "Passwords do not match."}), 400

    if not validate_email(email):
        return jsonify({"message": "Invalid email format."}), 400

    # Check if the user already exists in the database
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({"message": "User with this email already exists."}), 400

    # Hash the password using bcrypt for security
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert the new user into the MongoDB database
    users_collection.insert_one({
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": hashed_password
    })

    return jsonify({"message": "User successfully signed up!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Find user in the MongoDB database
    user = users_collection.find_one({"email": email})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    elif user:
        return jsonify({"status": "error", "message": "Invalid password."}), 401
    else:
        return jsonify({"status": "error", "message": "User not found."}), 404
    
@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('adminName') == "admin@gmail.com" and data.get('password') == "admin123":
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    return jsonify({"status": "error", "message": "Invalid credentials."}), 401

# Route to get all users (admin only)
@app.route('/users', methods=['GET'])
def get_users():
    users = users_collection.find()
    user_list = [{
        "id": str(u["_id"]),
        "firstName": u["first_name"],
        "lastName": u["last_name"],
        "email": u["email"],
        "isApproved": u.get("is_approved", False)
    } for u in users]
    return jsonify({"status": "success", "data": user_list}), 200

# Route to edit a user's email (admin only)
@app.route('/admin/edit-user', methods=['PUT'])
def edit_user():
    data = request.get_json()
    old_email = data.get('oldEmail')
    new_email = data.get('newEmail')

    # Update user email in the database
    result = users_collection.update_one(
        {'email': old_email},
        {'$set': {'email': new_email}}
    )

    if result.modified_count > 0:
        return jsonify({"status": "success", "message": "User email updated successfully."}), 200
    return jsonify({"status": "error", "message": "Failed to update user."}), 400

# Run server (only for local development)
if __name__ == '__main__':
    app.run(debug=True)
