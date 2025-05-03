from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from pymongo import MongoClient
import os
from bson import ObjectId

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']
users_collection = db['users']
categories_collection = db['categories']
products_collection = db['producttable']


UPLOAD_FOLDER = 'static/uploads/products'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        image_url = os.path.join('uploads/products', filename)
        return jsonify({'status': 'success', 'message': 'File uploaded successfully', 'image_url': image_url}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

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

@app.route('/api/categories/<id>', methods=['DELETE'])
def delete_category(id):
    result = categories_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"status": "success", "message": "Category deleted successfully"}), 200
    return jsonify({"status": "error", "message": "Category not found"}), 404

# --------- PRODUCT ROUTES --------- #

@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.form
    image_file = request.files.get("image")
    image_name = None

    if image_file and allowed_file(image_file.filename):
        image_name = secure_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
        image_file.save(image_path)

    product = {
        "name": data.get("name"),
        "description": data.get("description"),
        "price": data.get("price"),
        "category": data.get("category"),
        "status": data.get("status"),
        "image": image_name,
    }

    result = products_collection.insert_one(product)
    product["_id"] = str(result.inserted_id)
    return jsonify({"message": "Product added", "product": product}), 201

@app.route("/api/products", methods=["GET"])
def get_products():
    products = list(products_collection.find())
    for product in products:
        product["_id"] = str(product["_id"])
    return jsonify(products), 200

@app.route("/api/products/<id>", methods=["PUT"])
def update_product(id):
    data = request.form
    image_file = request.files.get("image")

    product = products_collection.find_one({"_id": ObjectId(id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404

    updated_data = {
        "name": data.get("name"),
        "description": data.get("description"),
        "price": data.get("price"),
        "category": data.get("category"),
        "status": data.get("status"),
    }

    if image_file and allowed_file(image_file.filename):
        image_name = secure_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
        image_file.save(image_path)
        updated_data["image"] = image_name

    products_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
    return jsonify({"message": "Product updated"}), 200

@app.route("/api/products/<id>", methods=["DELETE"])
def delete_product(id):
    result = products_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Product deleted"}), 200

@app.route("/uploads/products/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == '__main__':
    app.run(debug=True)
