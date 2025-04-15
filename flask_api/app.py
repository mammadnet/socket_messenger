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
    success = new_client.initializer(username)

    #if not success:
    #    return jsonify({"error": "Failed to initialize client"}), 500
    
    clients[username] = new_client

    new_client.set_receive_data_handler(handle_received_message)
    
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    system_message = {
        "id": generate_message_id("system", username),
        "user": "System",
        "message": f"{username} joined the chat!",
        "time": timestamp
    }

    add_message(system_message)
    
    return jsonify({"message": "Login successful"}), 200    

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('username')
    message = data.get('message')
    
    if not username or not message:
        return jsonify({"error": "username and message are required"}), 400
    
    # Check if the user has a client
    if username not in clients:
        return jsonify({"error": "User not logged in"}), 401
    
    # Get the client for this user
    user_client = clients[username]
    
    # Check if the client is connected
    if not user_client.is_connected:
        return jsonify({"error": "Not connected to chat server"}), 500
    
    # Generate a unique message ID
    message_id = generate_message_id("msg", username)
    
    # Send message to the socket server via client
    success = user_client.send_data(message)

    timestamp = datetime.now().strftime("%H:%M:%S")
    full_message = {
        "id": message_id,
        "user": username,
        "message": message,
        "time": timestamp,
        "sent_by_user": True  
    }
    
    
    add_message(full_message)

    return jsonify({"message": "Message sent successfully"}), 200

@app.route('/logout', methods=['POST'])
def logout():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({"error": "username is required"}), 400
    
    # Check if the user has a client
    if username not in clients:
        return jsonify({"error": "User not logged in"}), 401
    
    # Get the client for this user
    user_client = clients[username]
    
    # Close the client connection
    user_client.close_connection()
    
    # Remove the client from our dictionary
    del clients[username]
    
    # Add a system message for the user leaving
    timestamp = datetime.now().strftime("%H:%M:%S")
    system_message = {
        "id": generate_message_id("system", f"{username}_left"),
        "user": "System",
        "message": f"{username} left the chat.",
        "time": timestamp
    }
    
    # Add to local message storage
    add_message(system_message)
    
    return jsonify({"success": True}), 200

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
    app.run(port=5001, debug=True)