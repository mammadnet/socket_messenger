import socket


HOST = '127.0.0.1'
PORT = 65432
ADDR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server.bind(ADDR)


server.listen()

print(f'Server is listening on host {HOST} and port {PORT}...')

conn, addr = server.accept()

print(f'A connection was accepted by address {addr}')


while True:
    data = conn.recv(1024)
    if data.decode() == '.exitexit':
        print("The connection was closed by client")
        break
    
    print(data.decode())
    conn.sendall('message was received'.encode())

