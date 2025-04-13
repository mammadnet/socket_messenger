import socket
from classes import Client

import os
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
ADDR = (HOST, PORT)


client = Client()

client.connect(ADDR)

print("--> You can close the program by enter '.exitexit' command <--")

client.start()


