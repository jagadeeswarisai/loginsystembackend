from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from pymongo import MongoClient
from bson import ObjectId

# --- App Configuration ---
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "https://login-system-lac-three.vercel.app",
    "http://localhost:5173"
])

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- MongoDB Connection ---
client = MongoClient('mongodb+srv://jagadeeswarisai43:login12345@cluster0.dup95ax.mongodb.net/')
db = client['your_db']
category_collection = db['categories']
product_collection = db['products']

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if not file:
        print("No file provided")
        return None
    print("Received file:", file.filename)
    if allowed_file(file.filename):
        filename = datetime.now().strftime("%Y%m%d%H%M%S_") + secure_filename(file.filename)
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print("Saving file to:", full_path)
        try:
            file.save(full_path)
            print("File saved successfully.")
            return filename
        except Exception as e:
            print("Error saving file:", e)
            return None
    else:
        print("File extension not allowed:", file.filename)
        return None


# --- Serve Uploaded Files ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ================= CATEGORY ROUTES =================

@app.route('/api/categories', methods=['POST'])
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')
    group = request.form.get('group')
    image = request.files.get('image')

    if not name or not group or not image or not allowed_file(image.filename):
        return jsonify({'error': 'Name, group, and valid image are required'}), 400

    filename = save_image(image)

    category = {
        'name': name,
        'description': description,
        'group': group,
        'image': filename
    }
    result = category_collection.insert_one(category)
    return jsonify({'message': 'Category added successfully', 'id': str(result.inserted_id)}), 201

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = list(category_collection.find())
    for cat in categories:
        cat['_id'] = str(cat['_id'])
    return jsonify(categories)

@app.route('/api/categories/bygroup/<group>', methods=['GET'])
def get_categories_by_group(group):
    categories = list(category_collection.find({'group': group}))
    for cat in categories:
        cat['_id'] = str(cat['_id'])
    return jsonify(categories)

@app.route('/api/categories/<id>', methods=['PUT'])
def update_category(id):
    data = request.form
    update_data = {
        'name': data.get('name'),
        'description': data.get('description'),
        'group': data.get('group'),
    }

    if 'image' in request.files and request.files['image']:
        image = request.files['image']
        if allowed_file(image.filename):
            old = category_collection.find_one({'_id': ObjectId(id)})
            if old and old.get('image'):
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old['image']))
                except FileNotFoundError:
                    pass
            filename = save_image(image)
            update_data['image'] = filename
    else:
        update_data['image'] = data.get('existingImage', '')

    category_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'message': 'Category updated successfully'})

@app.route('/api/categories/<id>', methods=['DELETE'])
def delete_category(id):
    category = category_collection.find_one({'_id': ObjectId(id)})
    if category and category.get('image'):
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], category['image']))
        except FileNotFoundError:
            pass
    category_collection.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Category deleted'})

# ================= PRODUCT ROUTES =================

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.form
    image = request.files.get('image')
    filename = save_image(image) if image else ''

    product = {
        'name': data.get('name'),
        'description': data.get('description'),
        'price': data.get('price'),
        'height': data.get('height'),
        'weight': data.get('weight'),
        'length': data.get('length'),
        'width': data.get('width'),
        'status': data.get('status'),
        'tax': data.get('tax'),
        'warehouseLocation': data.get('warehouseLocation'),
        'category': data.get('category'),
        'image': filename
    }

    result = product_collection.insert_one(product)
    return jsonify({'message': 'Product added successfully', 'id': str(result.inserted_id)}), 201

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    query = {"category": category} if category else {}

    products = list(product_collection.find(query))
    for product in products:
        product['_id'] = str(product['_id'])
    return jsonify(products)

@app.route('/api/products/<id>', methods=['GET'])
def get_product_by_id(id):
    product = product_collection.find_one({"_id": ObjectId(id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404
    product['_id'] = str(product['_id'])
    return jsonify(product)

@app.route('/api/products/<id>', methods=['PUT'])
def update_product(id):
    data = request.form
    update_data = {
        'name': data.get('name'),
        'description': data.get('description'),
        'price': data.get('price'),
        'height': data.get('height'),
        'weight': data.get('weight'),
        'length': data.get('length'),
        'width': data.get('width'),
        'status': data.get('status'),
        'tax': data.get('tax'),
        'warehouseLocation': data.get('warehouseLocation'),
        'category': data.get('category'),
    }

    if 'image' in request.files:
        image = request.files['image']
        if image and allowed_file(image.filename):
            old = product_collection.find_one({'_id': ObjectId(id)})
            if old and old.get('image'):
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old['image']))
                except FileNotFoundError:
                    pass
            filename = save_image(image)
            update_data['image'] = filename
    else:
        update_data['image'] = data.get('existingImage', '')

    product_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<id>', methods=['DELETE'])
def delete_product(id):
    product = product_collection.find_one({'_id': ObjectId(id)})
    if product and product.get('image'):
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product['image']))
        except FileNotFoundError:
            pass
    product_collection.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Product deleted successfully'})

# ================= MAIN =================
if __name__ == '__main__':
    app.run(debug=True)
