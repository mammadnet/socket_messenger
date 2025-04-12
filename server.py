import socket
from classes import Server

HOST = '127.0.0.1'
PORT = 65432
ADDR = (HOST, PORT)

server = Server(host=HOST, port=PORT)

server.start()

print(f'Server is listening on host {HOST} and port {PORT}...')

print(f'A connection was accepted by address {addr}')



