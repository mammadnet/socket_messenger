import socket
import threading

import json

class Server(socket.socket):
    def __init__(self, host:str='127.0.0.1', port:int=65432, header_length=64, msg_handler_callback=None):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        
        self.header_length = header_length
        
        self.msg_handler_callback = msg_handler_callback
        
        self.bind((host, port))
        
        self.conections:set[socket.socket] = set()

        
    def _client_handler(self, conn:socket, addr):
        
        msg_handler = self.msg_handler_callback if self.msg_handler_callback else self.print_msg
        
        connected = True
        
        while connected:
            header = conn.recv(self.header_length)
            data_length = self.read_header(header)
            received_msg  = conn.recv(data_length).decode()
            data = self.decorate_msg(addr, received_msg)
            if not received_msg:
                connected = False
                break
            
            self.send_to_all_client(data)
            msg_handler(data, addr)
    
    
    def read_header(self, header:str) -> int:
        msg_length = header.strip()
        if msg_length:
            msg_length = int(msg_length.decode())
        else: 
            msg_length = 0
        return msg_length
    
    
    def atach_header(self, msg:str):
        msg_length = len(msg)
        
        header = str(msg_length).ljust(self.header_length, ' ')
        return (header + msg).encode()
    
    def atach_sender_addr(self, addr, msg):
        data = {
            'host':addr[0],
            'port':addr[1]
        }
        
        data = json.dumps(data)
        
        return data+msg
    
    def decorate_msg(self, addr, msg):
        data_with_addr = self.atach_sender_addr(addr, msg)
        data_with_length = self.atach_header(data_with_addr)
        
        return data_with_length
        
        
    def send_to_all_client(self, data):
        
        for client in self.conections:
            client.sendall(data)
            
            
    def start(self):
        self.listen()
        
        while True:
            conn, addr = self.accept()
            self.conections.add(conn)
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
        
        
        