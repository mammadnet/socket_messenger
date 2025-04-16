from endpoints import Client

import os
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
ADDR = (HOST, PORT)



username = input("Enter your username-->")
client = Client(HOST, PORT)
client.initializer(username)

while True:
    inp = input("---->")
    if inp == '.exitexit':
        client.close_connection()
        break
    data = {
        'type':'msg',
        'msg':inp
    }
    client.send_data(data)



print("--> You can close the program by enter '.exitexit' command <--")



