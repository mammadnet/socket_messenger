from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
import datetime
import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from endpoints import Client

# Load environment variables
load_dotenv()
HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', 5000))
FLASK_HOST = os.getenv('FLASK_HOST', 'localhost')
FlASK_PORT = int(os.getenv('FLASK_PORT', 5001))

app = Flask(__name__, static_folder='static')
CORS(app)

messages = []
clients = {}
message_ids = set()

def generate_message_id(prefix, username):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{username}_{unique_id}"

def handle_received_message(data):
    if "id" not in data:
        data["id"] = generate_message_id("received", data.get("username", "unknown"))
    
    if data.get("id") in message_ids:
        print(f"Skipping duplicate message in callback: {data.get('id')}")
        return
    
    message_ids.add(data.get("id"))
    messages.append(data)

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
    
    new_client = Client(host=HOST, port=PORT)
    success = new_client.initializer(username)
    
    if not success:
        return jsonify({"error": "Failed to connect to chat server"}), 500
    
    clients[username] = new_client
    new_client.set_receive_data_handler(handle_received_message)
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    system_message = {
        "id": generate_message_id("system", username),
        "user": "System",
        "message": f"{username} joined the chat!",
        "time": timestamp
    }
    messages.append(system_message)
    
    return jsonify({"message": "Login successful"}), 200    

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('username')
    message = data.get('message')
    
    if not username or not message:
        return jsonify({"error": "username and message are required"}), 400
    
    if username not in clients:
        return jsonify({"error": "User not logged in"}), 401
    
    user_client = clients[username]
    
    if not user_client.is_connected:
        return jsonify({"error": "Not connected to chat server"}), 500
    
    message_id = generate_message_id("msg", username)
    success = user_client.send_data(message)

    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    full_message = {
        "id": message_id,
        "user": username,
        "message": message,
        "time": timestamp,
        "sent_by_user": True  
    }
    messages.append(full_message)
    
    return jsonify({"success": True}), 200

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

@app.route('/logout', methods=['POST'])
def logout():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    if username not in clients:
        return jsonify({"error": "User not logged in"}), 401
    
    client = clients[username]
    client.close_connection()
    del clients[username]
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    system_message = {
        "id": generate_message_id("system", username),
        "user": "System",
        "message": f"{username} left the chat!",
        "time": timestamp
    }
    messages.append(system_message)
    
    return jsonify({"message": "Logout successful"}), 200

if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FlASK_PORT, debug=True)