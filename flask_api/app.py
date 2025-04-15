from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from classes import Client



app = Flask(__name__, static_folder='static')
CORS(app)

messages = []

clients = {}

message_ids = set()

# Helper function to generate a unique message ID
def generate_message_id(prefix, username):
    timestamp = datetime.now().strftime("%H:%M:%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{username}_{unique_id}"


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    if username in clients:
        return jsonify({"error": "User already logged in"}), 400
    
    new_client = Client()
    success = new_client.initialize(username)

    if not success:
        return jsonify({"error": "Failed to initialize client"}), 500
    
    clients[username] = new_client

    new_client.set_message_callback(handle_received_message)
    
    # Add a system message for the new user
    timestamp = datetime.now().strftime("%H:%M:%S")
    system_message = {
        "id": generate_message_id("system", username),
        "user": "System",
        "message": f"{username} joined the chat!",
        "time": timestamp
    }

    add_message(system_message)
    
    return jsonify({"message": "Login successful"}), 200    



@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages), 200


def add_message(message):
    if message.get("id") not in message_ids:
        messages.append(message)
        message_ids.add(message.get("id"))
        print(f"Added message: {message.get('id')}")
    else:
        print(f"Message {message.get('id')} already exists")

def handle_received_message(message):
    if "id" not in message:
        message["id"] = generate_message_id("received", "unknown")
    
    if message.get("id") in message_ids:
        print(f"Skipping duplicate message in callback: {message.get('id')}")
        return
    
    add_message(message)

if __name__ == '__main__':
    app.run(debug=True)