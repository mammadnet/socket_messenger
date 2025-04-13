import socket
from classes import Server

from dotenv import load_dotenv
import os
load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
ADDR = (HOST, PORT)

server = Server(host=HOST, port=PORT)

server.start()

print(f'Server is listening on host {HOST} and port {PORT}...')

print(f'A connection was accepted by address {addr}')



