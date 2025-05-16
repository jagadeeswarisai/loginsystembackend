from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# Import route functions
from Admin import signup, login, admin_login, get_users, edit_user
from Categories import (
    get_categories, add_category, update_category, delete_category,
    add_product, get_products, get_product_by_id, update_product, delete_product
)

app = Flask(__name__)

# CORS setup
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "https://login-system-lac-three.vercel.app"
])

# Uploads folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- Admin Routes ----------
app.route('/signup', methods=['POST'])(signup)
app.route('/login', methods=['POST'])(login)
app.route('/admin-login', methods=['POST'])(admin_login)
app.route('/users', methods=['GET'])(get_users)
app.route('/admin/edit-user', methods=['PUT'])(edit_user)

# ---------- Category Routes ----------
app.route('/api/categories', methods=['GET'])(get_categories)
app.route('/api/categories', methods=['POST'])(add_category)
app.route('/api/categories/<id>', methods=['PUT'])(update_category)
app.route('/api/categories/<id>', methods=['DELETE'])(delete_category)

# ---------- Product Routes ----------
app.route('/api/products', methods=['GET'])(get_products)
app.route('/api/products', methods=['POST'])(add_product)
app.route('/api/products/<id>', methods=['GET'])(get_product_by_id)
app.route('/api/products/<id>', methods=['PUT'])(update_product)
app.route('/api/products/<id>', methods=['DELETE'])(delete_product)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
