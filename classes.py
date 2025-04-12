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
            header = conn.recv(self.header_length)
            msg_length = self.read_header(header)
            msg = conn.recv(msg_length).decode()
            if not msg:
                connected = False
                break
            msg_handler(msg, addr)
    
    
    def read_header(self, header:str) -> int:
        msg_length = header.strip()
        if msg_length:
            msg_length = int(msg_length.decode())
        else: 
            msg_length = 0
        return msg_length
    
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
        
        

class Client(socket.socket):
    
    def __init__(self, host:str='127.0.0.1', port:int=65432, header_length=64, msg_handler_callback=None):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.ADDR = (host, port)
        
        self.header_length = header_length
        self.msg_handler_callback = msg_handler_callback
        
    
    def start(self):
            
        connected = True
        while connected:
            msg = self.get_input()
            data = self.atach_header(msg)
            self.sendall(data)
    
    def get_input(self):
        inp = input()
        
        return inp
    
    def atach_header(self, msg:str):
        msg_length = len(msg)
        
        header = str(msg_length).ljust(self.header_length, ' ')
        return (header + msg).encode()
        
        
        