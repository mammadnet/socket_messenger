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
            
            self.send_to_all_client(conn, data)
            msg_handler(data, addr)
    
    
    def read_header(self, header:str) -> int:
        msg_length = header.strip()
        if msg_length:
            msg_length = int(msg_length.decode())
        else: 
            msg_length = 0
        return msg_length
    
    
    def attach_header(self, msg:str):
        msg_length = len(msg)
        
        header = str(msg_length).ljust(self.header_length, ' ')
        return (header + msg).encode()
    
    def attach_sender_addr(self, addr, msg):
        data = {
            'host':addr[0],
            'port':addr[1]
        }
        
        data = json.dumps(data)
        
        return data+msg
    
    def decorate_msg(self, addr, msg):
        data_with_addr = self.attach_sender_addr(addr, msg)
        data_with_length = self.attach_header(data_with_addr)
        
        return data_with_length
        
        
    def send_to_all_client(self,sender_client, data):
        
        for client in self.conections:
            if client != sender_client: 
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
            
        
        threading.Thread(target=self.msg_receive_handler).start()
        
        connected = True
        while connected:
            msg = self.get_input()
            data = self.attach_data_length(msg)
            self.sendall(data)
    
    def get_input(self):
        inp = input()
        
        return inp
    
    def attach_data_length(self, msg:str):
        msg_length = len(msg)
        
        header = str(msg_length).ljust(self.header_length, ' ')
        return (header + msg).encode()
    
    
    def separate_sender_addr(self, data):
        
        addr_end = data.find(b'}')
        
        sender_addr = data[0:addr_end+1]
        
        return (json.loads(sender_addr), data[addr_end+1:])
    
    
    def msg_receive_handler(self):
        
        while True:
            data_length = self.recv(self.header_length)
            
            data_length = int(data_length.strip())
            
            data = self.recv(data_length)
            
            sender_addr, msg = self.separate_sender_addr(data)
            
            if not msg:
                break
            
            self.print_msg(sender_addr, msg)
            
            
        
    
    def print_msg(self, addr, msg):
        
        print(f'{addr['host']}:{addr['port']} --> {msg.decode()}')
        
        
        