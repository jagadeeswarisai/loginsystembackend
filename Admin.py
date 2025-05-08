from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from pymongo import MongoClient
import os
from bson import ObjectId

# Initialize Flask App
app = Flask(__name__)

# CORS setup for localhost and Vercel frontend
CORS(app, origins=[
    "http://localhost:5173",
    "https://login-system-lac-three.vercel.app"
])

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']
users_collection = db['users']

# Upload Folder Setup
UPLOAD_FOLDER = 'static/uploads/products'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --------- USER ROUTES --------- #

# Signup Route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    confirm_email = data.get('confirmEmail')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    # Basic validation
    if not all([first_name, last_name, email, confirm_email, password, confirm_password]):
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    if email != confirm_email:
        return jsonify({"status": "error", "message": "Emails do not match."}), 400

    if password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match."}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"status": "error", "message": "Email already registered."}), 400

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': hashed_password,
        'is_approved': False
    })

    return jsonify({"status": "success", "message": "Signup successful!"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = users_collection.find_one({"email": email})

    if user and check_password_hash(user['password'], password):
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    elif user:
        return jsonify({"status": "error", "message": "Invalid password."}), 401
    else:
        return jsonify({"status": "error", "message": "User not found."}), 404

# Admin Login Route
@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('adminName') == "admin@gmail.com" and data.get('password') == "admin123":
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    return jsonify({"status": "error", "message": "Invalid credentials."}), 401

# Get All Users
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

# Edit User Email
@app.route('/admin/edit-user', methods=['PUT'])
def edit_user():
    data = request.get_json()
    result = users_collection.update_one(
        {'email': data.get('oldEmail')},
        {'$set': {'email': data.get('newEmail')}}
    )
    if result.modified_count > 0:
        return jsonify({"status": "success", "message": "User email updated successfully."}), 200
    return jsonify({"status": "error", "message": "Failed to update user."}), 400

# Start Flask App
if __name__ == '__main__':
    app.run(debug=True)
