from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt
import re

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": [
    "http://localhost:5173",
    "https://login-system-lac-three.vercel.app/"
]}})

# MongoDB connection setup
client = MongoClient('mongodb+srv://jagadeeswarisai43:login12345@cluster0.dup95ax.mongodb.net/')
db = client['your_database_name']  # Replace with your actual database name
users_collection = db['users']  # Replace with your actual collection name

# Admin credentials (use environment variables for better security)
admin_email = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
admin_password_plain = os.getenv("ADMIN_PASSWORD", "admin123")
admin_password_hash = bcrypt.hashpw(admin_password_plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Helper function: validate email format
def validate_email(email):
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(regex, email)

# ========== Signup ========== 
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    first = data.get('firstName')
    last = data.get('lastName')
    email = data.get('email')
    confirm_email = data.get('confirmEmail')
    pwd = data.get('password')
    confirm_pwd = data.get('confirmPassword')

    if not all([first, last, email, confirm_email, pwd, confirm_pwd]):
        return jsonify({"message": "All fields are required."}), 400
    if email != confirm_email:
        return jsonify({"message": "Emails do not match."}), 400
    if pwd != confirm_pwd:
        return jsonify({"message": "Passwords do not match."}), 400
    if not validate_email(email):
        return jsonify({"message": "Invalid email format."}), 400
    if users_collection.find_one({"email": email}):
        return jsonify({"message": "User already exists."}), 409

    hashed_pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users_collection.insert_one({
    "first_name": first,
    "last_name": last,
    "email": email,
    "password": hashed_pwd  # this is now a string
})
    return jsonify({"message": "Signup successful!"}), 201

# ========== User Login ========== 
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    pwd = data.get('password')

    user = users_collection.find_one({"email": email})
    if user and bcrypt.checkpw(pwd.encode('utf-8'), user['password']).encode('utf-8'):
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    elif user:
        return jsonify({"status": "error", "message": "Invalid password."}), 401
    else:
        return jsonify({"status": "error", "message": "User not found."}), 404

# ========== Admin Login ========== 
@app.route('/admin-login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if email == admin_email and bcrypt.checkpw(password.encode('utf-8'), admin_password_hash.encode('utf-8')):
            return jsonify({"status": "success", "message": "Admin login successful!"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid credentials."}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

# ========== Get All Users ========== 
@app.route('/users', methods=['GET'])
def get_users():
    users = users_collection.find()
    user_list = [{
        "id": str(u["_id"]),
        "firstName": u["first_name"],
        "lastName": u["last_name"],
        "email": u["email"]
    } for u in users]
    return jsonify({"status": "success", "data": user_list}), 200

# ========== Admin: Edit User Email ========== 
@app.route('/admin/edit-user', methods=['PUT'])
def edit_user():
    data = request.get_json()
    old_email = data.get('oldEmail')
    new_email = data.get('newEmail')

    result = users_collection.update_one(
        {"email": old_email},
        {"$set": {"email": new_email}}
    )

    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "User not found."}), 404
    elif result.modified_count > 0:
        return jsonify({"status": "success", "message": "Email updated."}), 200
    else:
        return jsonify({"status": "error", "message": "No changes made."}), 400

# ========== Run the Flask App ========== 
if __name__ == '__main__':
    app.run(debug=True, port=5000)
