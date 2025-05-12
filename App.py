from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from flask import send_from_directory
from Admin import signup, login, admin_login, get_users, edit_user  # Directly import the route functions
from Categories import (
    get_categories, add_category,
    update_category, delete_category,
    add_product, get_products,
    get_product_by_id, update_product,
    delete_product
)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for specific origins
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "https://login-system-lac-three.vercel.app"
])

client = MongoClient('mongodb+srv://jagadeeswarisai43:login12345@cluster0.dup95ax.mongodb.net/')
db = client['your_database_name'] 
db = client['your_db']  

users_collection = db['users']
category_collection = db['categories']
product_collection = db['products']

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/signup', methods=['POST'])
def signup_route():
    return signup()  # Directly call the signup function from Admin.py

@app.route('/login', methods=['POST'])
def login_route():
    return login()  # Directly call the login function from Admin.py

@app.route('/admin-login', methods=['POST'])
def admin_login_route():
    return admin_login()  # Directly call the admin_login function from Admin.py

@app.route('/users', methods=['GET'])
def get_users_route():
    return get_users()  # Directly call the get_users function from Admin.py

@app.route('/admin/edit-user', methods=['PUT'])
def edit_user_route():
    return edit_user()  # Directly call the edit_user function from Admin.py

# Category routes
@app.route('/api/categories', methods=['GET'])
def get_categories_route():
    return get_categories()  # Directly call the get_categories function from Categories.py

@app.route('/api/categories', methods=['POST'])
def add_category_route():
    return add_category()  # Directly call the add_category function from Categories.py

@app.route('/api/categories/<id>', methods=['PUT'])
def update_category_route(id):
    return update_category(id)  # Directly call the update_category function from Categories.py

@app.route('/api/categories/<id>', methods=['DELETE'])
def delete_category_route(id):
    return delete_category(id)  # Directly call the delete_category function from Categories.py

# Product routes
@app.route('/api/products', methods=['POST'])
def add_product_route():
    return add_product()  # Directly call the add_product function from Categories.py

@app.route('/api/products', methods=['GET'])
def get_products_route():
    return get_products()  # Directly call the get_products function from Categories.py

@app.route('/api/products/<id>', methods=['GET'])
def get_product_by_id_route(id):
    return get_product_by_id(id)  # Directly call the get_product_by_id function from Categories.py

@app.route('/api/products/<id>', methods=['PUT'])
def update_product_route(id):
    return update_product(id)  # Directly call the update_product function from Categories.py

@app.route('/api/products/<id>', methods=['DELETE'])
def delete_product_route(id):
    return delete_product(id)  # Directly call the delete_product function from Categories.py

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=5000)
