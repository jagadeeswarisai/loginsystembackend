from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient('mongodb://localhost:27017/')
db = client['your_db']
category_collection = db['categories']
product_collection = db['products']

# Serve images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------------- CATEGORY ROUTES ----------------
@app.route('/api/categories', methods=['POST'])
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')
    image = request.files.get('image')

    if not name or not image:
        return jsonify({'error': 'Name and image required'}), 400

    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    category = {
        'name': name,
        'description': description,
        'image': filename
    }

    category_collection.insert_one(category)
    return jsonify({'message': 'Category added successfully'}), 201

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = list(category_collection.find())
    for cat in categories:
        cat['_id'] = str(cat['_id'])
    return jsonify(categories)

@app.route('/api/categories/<id>', methods=['PUT'])
def update_category(id):
    data = request.form
    update_data = {
        'name': data.get('name'),
        'description': data.get('description'),
    }

    if 'image' in request.files:
        image = request.files['image']
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        update_data['image'] = filename

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

# ---------------- PRODUCT ROUTES ----------------
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.form
    image = request.files.get('image')

    filename = ''
    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

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

    product_collection.insert_one(product)
    return jsonify({'message': 'Product added successfully'}), 201

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    Retrieves all products from the database.
    Optionally filter by category.
    """
    category = request.args.get('category')
    query = {}
    if category:
        query = {"category": category}
    
    try:
        products = list(product_collection.find(query))
        # Convert MongoDB ObjectId to string
        for product in products:
            product['_id'] = str(product['_id'])
        
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



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
        if image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            update_data['image'] = filename

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

if __name__ == '__main__':
    app.run(debug=True)
