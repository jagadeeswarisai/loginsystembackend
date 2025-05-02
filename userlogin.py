from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/signup")
db = client["userDB"]  # Database name
users_collection = db["users"]  # Collection name

@app.route('/api/signup', methods=['POST'])
def signup():
    # Get data from the request body
    data = request.get_json()

    # Ensure all fields are provided
    if not all([data.get('firstName'), data.get('lastName'), data.get('email'), data.get('password')]):
        return jsonify({"error": "Missing required fields"}), 400

    # Check if email already exists
    existing_user = users_collection.find_one({"email": data['email']})
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    # Insert new user data into MongoDB with the hashed password
    user_data = {
        "firstName": data['firstName'],
        "lastName": data['lastName'],
        "email": data['email'],
        "password": hashed_password.decode('utf-8'),  # Store the hashed password as a string
    }

    users_collection.insert_one(user_data)

    return jsonify({"message": "Signup successful!"}), 201
@app.route('/api/users', methods=['GET'])
def get_users():
    # Fetch all users from the MongoDB collection
    users = users_collection.find()

    # Convert the MongoDB cursor to a list and exclude the password field
    users_list = []
    for user in users:
        user_data = {
            "firstName": user['firstName'],
            "lastName": user['lastName'],
            "email": user['email']
        }
        users_list.append(user_data)

    return jsonify(users_list), 200


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    user = users_collection.find_one({"email": data['email']})

    if user is None:
        return jsonify({"error": "Invalid credentials"}), 401

    # Check if the provided password matches the stored hash
    if bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401
    
@app.route('/api/users/<email>', methods=['PUT'])
def update_user(email):
    data = request.get_json()

    # Ensure required fields are provided
    if not any([data.get('firstName'), data.get('lastName'), data.get('password')]):
        return jsonify({"error": "No fields to update"}), 400

    # Find the user by email
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Hash the new password if provided
    if data.get('password'):
        data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Update user data in the database
    update_data = {key: value for key, value in data.items() if value}  # Exclude None/empty values
    users_collection.update_one({"email": email}, {"$set": update_data})

    return jsonify({"message": "User updated successfully!"}), 200
@app.route('/api/users/<email>', methods=['DELETE'])
def delete_user(email):
    # Find the user by email
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Delete the user from the database
    users_collection.delete_one({"email": email})

    return jsonify({"message": "User deleted successfully!"}), 200




if __name__ == '__main__':
    app.run(debug=True)
