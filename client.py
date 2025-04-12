import socket
from classes import Client


HOST = '127.0.0.1'
PORT = 65432
ADDR = (HOST, PORT)


client = Client()

client.connect(ADDR)

print("--> You can close the program by enter '.exitexit' command <--")

client.start()


