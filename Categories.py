from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import cloudinary
import cloudinary.uploader
from collections import defaultdict

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "https://login-system-4xtj.vercel.app"
])

# --- MongoDB Setup ---
client = MongoClient("mongodb+srv://jagadeeswarisai43:login12345@cluster0.dup95ax.mongodb.net/")
db = client['your_db']  # Replace with your DB name
category_collection = db['categories']
product_collection = db['products']

# --- Cloudinary Configuration ---
cloudinary.config(
    cloud_name="dklysh3ty",
    api_key="536781396976572",
    api_secret="your_actual_api_secret_here"  # Replace this with your actual secret
)

# === CATEGORY ROUTES ===

@app.route('/api/categories', methods=['POST'])
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')
    group = request.form.get('group')
    image = request.files.get('image')

    if not name or not group or not image:
        return jsonify({'error': 'Name, group, and image are required'}), 400

    # Upload image to Cloudinary
    upload_result = cloudinary.uploader.upload(image)
    image_url = upload_result.get('secure_url')

    category = {
        'name': name,
        'description': description,
        'group': group,
        'image': image_url
    }
    res = category_collection.insert_one(category)
    return jsonify({'message': 'Category added', 'id': str(res.inserted_id)}), 201

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = list(category_collection.find())
    for cat in categories:
        cat['_id'] = str(cat['_id'])
    return jsonify(categories)

@app.route('/api/categories/group/<group_name>', methods=['GET'])
def get_categories_by_group(group_name):
    categories = list(category_collection.find({'group': group_name}))
    for cat in categories:
        cat['_id'] = str(cat['_id'])
    return jsonify(categories)

@app.route('/api/categories/grouped', methods=['GET'])
def get_categories_grouped():
    categories = list(category_collection.find())
    grouped = defaultdict(list)
    for cat in categories:
        cat['_id'] = str(cat['_id'])
        grouped[cat['group']].append(cat)
    return jsonify(grouped)

@app.route('/api/categories/<id>', methods=['PUT'])
def update_category(id):
    category = category_collection.find_one({'_id': ObjectId(id)})
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    name = request.form.get('name')
    description = request.form.get('description')
    group = request.form.get('group')
    existing_image = request.form.get('existingImage')

    update_data = {
        'name': name,
        'description': description,
        'group': group
    }

    if 'image' in request.files:
        image = request.files['image']
        upload_result = cloudinary.uploader.upload(image)
        update_data['image'] = upload_result.get('secure_url')
    else:
        update_data['image'] = existing_image

    category_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'message': 'Category updated successfully'})

@app.route('/api/categories/<id>', methods=['DELETE'])
def delete_category(id):
    category = category_collection.find_one({'_id': ObjectId(id)})
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    category_collection.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Category deleted successfully'})

# === PRODUCT ROUTES ===

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.form
    image = request.files.get('image')

    if not data.get('name') or not data.get('category') or not image:
        return jsonify({'error': 'Name, category, and image are required'}), 400

    # Upload product image to Cloudinary
    upload_result = cloudinary.uploader.upload(image)
    image_url = upload_result.get('secure_url')

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
        'image': image_url
    }

    res = product_collection.insert_one(product)
    return jsonify({'message': 'Product added', 'id': str(res.inserted_id)}), 201

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    query = {"category": category} if category else {}

    products = list(product_collection.find(query))
    for prod in products:
        prod['_id'] = str(prod['_id'])
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
    product = product_collection.find_one({'_id': ObjectId(id)})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

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
        upload_result = cloudinary.uploader.upload(image)
        update_data['image'] = upload_result.get('secure_url')
    else:
        update_data['image'] = data.get('existingImage')

    product_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<id>', methods=['DELETE'])
def delete_product(id):
    product = product_collection.find_one({'_id': ObjectId(id)})
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    product_collection.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Product deleted successfully'})

# === Run Server ===
if __name__ == '__main__':
    app.run(debug=True)
