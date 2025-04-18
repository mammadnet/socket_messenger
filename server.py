from endpoints import Server

from dotenv import load_dotenv
import os
load_dotenv()

HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', '5000'))
ADDR = (HOST, PORT)

server = Server(host=HOST, port=PORT)

print(f'Server is listening on host {HOST} and port {PORT}...')

server.start()




