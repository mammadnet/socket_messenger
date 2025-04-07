import socket



HOST = '127.0.0.1'
PORT = 65432
ADDR = (HOST, PORT)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


sock.connect(ADDR)

print("--> You can close the program by enter '.exitexit' command <--")

inp = ''

while inp != '.exitexit':
    inp = input()
    
    sock.sendall(inp.encode())
    data = sock.recv(1024)
    print("From server:")
    print(data)

sock.close()
