from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt
import re

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "https://login-system-lac-three.vercel.app"]) # Replace with your frontend URL

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["mydatabase"]
users_collection = db.users

# Email validation
def validate_email(email):
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email)

# Signup route
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

# Login route
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

admin_email = os.getenv("ADMIN_EMAIL")
admin_password_hash = os.getenv("ADMIN_PASSWORD_HASH")  # Store the hashed password securely

# Admin login route
@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if the email and password match the admin credentials
    if email == admin_email and bcrypt.checkpw(password.encode('utf-8'), admin_password_hash.encode('utf-8')):
        return jsonify({"status": "success", "message": "Admin login successful!"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid credentials."}), 401

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

# Edit user
@app.route('/admin/edit-user', methods=['PUT'])
def edit_user():
    data = request.get_json()
    old_email = data.get('oldEmail')
    new_email = data.get('newEmail')

    result = users_collection.update_one(
        {'email': old_email},
        {'$set': {'email': new_email}}
    )

    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "User not found."}), 404
    if result.modified_count > 0:
        return jsonify({"status": "success", "message": "User email updated successfully."}), 200
    return jsonify({"status": "error", "message": "No changes made."}), 400

# Run app on Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
