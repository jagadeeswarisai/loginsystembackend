from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "https://login-system-4xtj.vercel.app",
    "http://localhost:5173"
])

# Cloudinary config
cloudinary.config(
    cloud_name='dklysh3ty',
    api_key='536781396976572',
    api_secret='-dKXwlRlrkT3ks66LcaY7TzuJHE',
    secure=True
)

# MongoDB connection
client = MongoClient('mongodb+srv://jagadeeswarisai43:login12345@cluster0.dup95ax.mongodb.net/')
db = client['your_db']
category_collection = db['categories']
product_collection = db['products']

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- CATEGORY ROUTES ----------------

@app.route('/api/categories', methods=['POST'])
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')
    group = request.form.get('group')
    image = request.files.get('image')

    if not name or not group or not image or not allowed_file(image.filename):
        return jsonify({'error': 'Name, group, and valid image are required'}), 400

    upload_result = cloudinary.uploader.upload(image)
    image_url = upload_result.get('secure_url')
    public_id = upload_result.get('public_id')

    category = {
        'name': name,
        'description': description,
        'group': group,
        'image': image_url,
        'image_id': public_id
    }
    result = category_collection.insert_one(category)
    return jsonify({'message': 'Category added successfully', 'id': str(result.inserted_id), 'image_url': image_url}), 201

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
        'group': data.get('group')
    }

    if 'image' in request.files:
        image = request.files['image']
        if image and allowed_file(image.filename):
            upload_result = cloudinary.uploader.upload(image)
            update_data['image'] = upload_result.get('secure_url')
            update_data['image_id'] = upload_result.get('public_id')
    else:
        update_data['image'] = data.get('existingImage', '')
        update_data['image_id'] = data.get('existingImageId', '')

    category_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'message': 'Category updated successfully'})

@app.route('/api/categories/<id>', methods=['DELETE'])
def delete_category(id):
    category = category_collection.find_one({'_id': ObjectId(id)})
    if category and 'image_id' in category:
        try:
            cloudinary.uploader.destroy(category['image_id'])
        except:
            pass
    category_collection.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Category deleted'})

# ---------------- PRODUCT ROUTES ----------------

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.form
    image = request.files.get('image')
    image_url = ''
    public_id = ''

    if image and allowed_file(image.filename):
        upload_result = cloudinary.uploader.upload(image)
        image_url = upload_result.get('secure_url')
        public_id = upload_result.get('public_id')

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
        'image': image_url,
        'image_id': public_id
    }

    result = product_collection.insert_one(product)
    return jsonify({'message': 'Product added successfully', 'id': str(result.inserted_id), 'image_url': image_url}), 201

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    query = {"category": category} if category else {}
    products = list(product_collection.find(query))
    for product in products:
        product['_id'] = str(product['_id'])
    return jsonify(products)

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
        'category': data.get('category')
    }

    if 'image' in request.files:
        image = request.files['image']
        if image and allowed_file(image.filename):
            upload_result = cloudinary.uploader.upload(image)
            update_data['image'] = upload_result.get('secure_url')
            update_data['image_id'] = upload_result.get('public_id')
    else:
        update_data['image'] = data.get('existingImage', '')
        update_data['image_id'] = data.get('existingImageId', '')

    product_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<id>', methods=['DELETE'])
def delete_product(id):
    product = product_collection.find_one({'_id': ObjectId(id)})
    if product and 'image_id' in product:
        try:
            cloudinary.uploader.destroy(product['image_id'])
        except:
            pass
    product_collection.delete_one({'_id': ObjectId(id)})
    return jsonify({'message': 'Product deleted successfully'})

# --------------- RUN APP ---------------
if __name__ == '__main__':
    app.run(debug=True)
