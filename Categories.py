from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import cloudinary
import cloudinary.uploader

# --- App Configuration ---
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "https://login-system-4xtj.vercel.app",
    "http://localhost:5173"
])

# --- Cloudinary Configuration ---
cloudinary.config(
    cloud_name='dklysh3ty',      # உங்கள் Cloudinary Cloud Name
    api_key='536781396976572',            # உங்கள் API Key
    api_secret='-dKXwlRlrkT3ks66LcaY7TzuJHE',      # உங்கள் API Secret
    secure=True
)

# --- MongoDB Connection ---
client = MongoClient('mongodb+srv://jagadeeswarisai43:login12345@cluster0.dup95ax.mongodb.net/')
db = client['your_db']  # உங்கள் DB Name
category_collection = db['categories']
product_collection = db['products']

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(image):
    upload_result = cloudinary.uploader.upload(image)
    return upload_result['secure_url']

# ================= CATEGORY ROUTES =================

@app.route('/api/categories', methods=['POST'])
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')
    group = request.form.get('group')
    image = request.files.get('image')

    if not name or not group or not image or not allowed_file(image.filename):
        return jsonify({'error': 'Name, group, and valid image are required'}), 400

    image_url = save_image(image)

    category = {
        'name': name,
        'description': description,
        'group': group,
        'image': image_url
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
            # No need to delete old image from Cloudinary here unless you want to
            image_url = save_image(image)
            update_data['image'] = image_url
    else:
        update_data['image'] = data.get('existingImage', '')

    category_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'message': 'Category updated successfully'})

@app.route('/api/categories/<id>', methods=['DELETE'])
def delete_category(id):
    category = category_collection.find_one({'_id': ObjectId(id)})
    if category:
        # Optionally delete image from Cloudinary via API here if you have public_id stored
        category_collection.delete_one({'_id': ObjectId(id)})
        return jsonify({'message': 'Category deleted'})
    else:
        return jsonify({'error': 'Category not found'}), 404

# ================= PRODUCT ROUTES =================

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.form
    image = request.files.get('image')
    image_url = save_image(image) if image and allowed_file(image.filename) else ''

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
            image_url = save_image(image)
            update_data['image'] = image_url
    else:
        update_data['image'] = data.get('existingImage', '')

    product_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<id>', methods=['DELETE'])
def delete_product(id):
    product = product_collection.find_one({'_id': ObjectId(id)})
    if product:
        # Optionally delete image from Cloudinary here if public_id stored
        product_collection.delete_one({'_id': ObjectId(id)})
        return jsonify({'message': 'Product deleted successfully'})
    else:
        return jsonify({'error': 'Product not found'}), 404

# ================= MAIN =================
if __name__ == '__main__':
    app.run(debug=True)
