import socket
import threading

class Server(socket.socket):
    def __init__(self, host:str='127.0.0.1', port:int=65432, header_length=64, msg_handler_callback=None):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        
        self.header_length = header_length
        
        self.msg_handler_callback = msg_handler_callback
        
        self.bind((host, port))

        
    def _client_handler(self, conn:socket, addr):
        
        msg_handler = self.msg_handler_callback if self.msg_handler_callback else self.print_msg
        
        connected = True
        
        while connected:
            # msg_length = int(conn.recv(self.header_length))
            msg = conn.recv(1024).decode()
            if not msg:
                connected = False
                break
            msg_handler(msg, addr)
    
    
    def start(self):
        self.listen()
        
        while True:
            conn, addr = self.accept()
            thread = threading.Thread(target=self._client_handler, args=(conn, addr))
            thread.start()
            print("INSIDE WHILE")
        
    def print_msg(self, msg, addr):
        print(f'{addr} --> "{msg}"')
            
            
        
    def sendmsg(self, msg:str):
        self.sendall(msg.encode())
        