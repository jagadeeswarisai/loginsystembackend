from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt
import re

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="https://login-system-lac-three.vercel.app")

# Load environment variables from .env file
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["mydatabase"]
users_collection = db.users

# Email validation
def validate_email(email):
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email)

# User signup route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    confirm_email = data.get('confirmEmail')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    if not all([first_name, last_name, email, confirm_email, password, confirm_password]):
        return jsonify({"message": "All fields are required."}), 400
    if email != confirm_email:
        return jsonify({"message": "Emails do not match."}), 400
    if password != confirm_password:
        return jsonify({"message": "Passwords do not match."}), 400
    if not validate_email(email):
        return jsonify({"message": "Invalid email format."}), 400

    try:
        if users_collection.find_one({"email": email}):
            return jsonify({"message": "User with this email already exists."}), 409

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        users_collection.insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": hashed_password
        })

        return jsonify({"message": "User successfully signed up!"}), 201
    except Exception as e:
        return jsonify({"message": "Internal server error", "error": str(e)}), 500

# User login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    elif user:
        return jsonify({"status": "error", "message": "Invalid password."}), 401
    else:
        return jsonify({"status": "error", "message": "User not found."}), 404

# Admin login route
@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('adminName') == "admin@gmail.com" and data.get('password') == "admin123":
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    return jsonify({"status": "error", "message": "Invalid credentials."}), 401

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = users_collection.find()
        user_list = [{
            "id": str(u["_id"]),
            "firstName": u["first_name"],
            "lastName": u["last_name"],
            "email": u["email"],
            "isApproved": u.get("is_approved", False)
        } for u in users]
        return jsonify({"status": "success", "data": user_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to retrieve users", "error": str(e)}), 500

# Edit user email
@app.route('/admin/edit-user', methods=['PUT'])
def edit_user():
    data = request.get_json()
    old_email = data.get('oldEmail')
    new_email = data.get('newEmail')

    try:
        result = users_collection.update_one(
            {'email': old_email},
            {'$set': {'email': new_email}}
        )

        if result.matched_count == 0:
            return jsonify({"status": "error", "message": "User not found."}), 404
        if result.modified_count > 0:
            return jsonify({"status": "success", "message": "User email updated successfully."}), 200
        return jsonify({"status": "error", "message": "No changes made."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to update user.", "error": str(e)}), 500

# Run server
if __name__ == '__main__':
    app.run(debug=True)
