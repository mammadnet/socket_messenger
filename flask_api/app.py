from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#from chat_client import ChatClient


app = Flask(__name__, static_folder='static')
CORS(app)

messages = []

clients = {}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages), 200

if __name__ == '__main__':
    app.run(debug=True)