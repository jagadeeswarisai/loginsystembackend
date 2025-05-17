from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max size

# Make sure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup CORS - allow your frontend URLs here
CORS(app, supports_credentials=True, origins=[
    "https://login-system-lac-three.vercel.app",
    "http://localhost:5173"
])

# MongoDB Setup - change with your own URI and DB name
client = MongoClient('mongodb+srv://jagadeeswarisai43:login12345@cluster0.dup95ax.mongodb.net/')
db = client['your_db']  # change this to your DB name
category_collection = db['categories']

# Helper to check allowed files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to upload image and create category
@app.route('/api/categories', methods=['POST'])
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')
    group = request.form.get('group')
    image = request.files.get('image')

    if not name or not group or not image:
        return jsonify({'error': 'Name, group, and image are required'}), 400

    if not allowed_file(image.filename):
        return jsonify({'error': 'Invalid image type'}), 400

    # Save the image to uploads folder
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Insert category document in MongoDB
    category = {
        'name': name,
        'description': description,
        'group': group,
        'image': filename
    }
    result = category_collection.insert_one(category)
    return jsonify({'message': 'Category added successfully', 'id': str(result.inserted_id)}), 201

# Route to serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
