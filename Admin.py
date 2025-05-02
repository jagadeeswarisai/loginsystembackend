from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from pymongo import MongoClient
import os
from bson import ObjectId
import os

app = Flask(__name__)

# Ensure the path to your upload folder is correct
UPLOAD_FOLDER = 'path_to_your_upload_folder'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route to serve the uploaded images



# Initialize Flask application
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']
users_collection = db['users']
categories_collection = db['categories']

# Upload folder setup
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --------- USER ROUTES --------- #
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    password = data.get('password')

    if not all([first_name, last_name, email, password]):
        return jsonify({"status": "error", "message": "All fields are required."}), 400

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


@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('adminName') == "admin@gmail.com" and data.get('password') == "admin123":
        return jsonify({"status": "success", "message": "Login successful!"}), 200
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

# --------- CATEGORY ROUTES --------- #
@app.route('/uploads/<filename>')
def serve_image(filename):
    # Ensure the file exists and is served from the correct directory
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)
@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_url = os.path.join('uploads', filename)
        return jsonify({'status': 'success', 'message': 'File uploaded successfully', 'image_url': image_url}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400



# Get all categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = list(categories_collection.find())
    category_list = [{
        "_id": str(category["_id"]),
        "name": category["name"],
        "description": category["description"],
        "image_url": category["image_url"]
    } for category in categories]
    return jsonify({"status": "success", "data": category_list}), 200

# Get a single category by ID
@app.route('/api/categories/<id>', methods=['GET'])
def get_category(id):
    category = categories_collection.find_one({"_id": ObjectId(id)})
    if category:
        return jsonify({
            "status": "success",
            "data": {
                "_id": str(category["_id"]),
                "name": category["name"],
                "description": category["description"],
                "image_url": category["image_url"]
            }
        }), 200
    return jsonify({"status": "error", "message": "Category not found"}), 404

# Add a new category
@app.route('/api/categories', methods=['POST'])
def add_category():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    image_url = data.get('image_url')

    if not all([name, description, image_url]):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    new_category = {
        'name': name,
        'description': description,
        'image_url': image_url
    }
    result = categories_collection.insert_one(new_category)
    new_category['_id'] = str(result.inserted_id)

    return jsonify({'status': 'success', 'message': 'Category added successfully', 'category': new_category}), 200

# Edit a category
@app.route('/api/categories/<id>', methods=['PUT'])
def edit_category(id):
    data = request.json
    name = data.get('name')
    description = data.get('description')
    image_url = data.get('image_url')

    result = categories_collection.update_one(
        {'_id': ObjectId(id)},
        {'$set': {'name': name, 'description': description, 'image_url': image_url}}
    )
    if result.modified_count > 0:
        return jsonify({"status": "success", "message": "Category updated successfully."}), 200
    return jsonify({"status": "error", "message": "Failed to update category."}), 400

# Delete a category
@app.route('/api/categories/<id>', methods=['DELETE'])
def delete_category(id):
    result = categories_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"status": "success", "message": "Category deleted successfully"}), 200
    return jsonify({"status": "error", "message": "Category not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
