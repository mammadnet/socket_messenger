import socket
import threading

import json

# for manage connection in server side
class Server_client:
    def __init__(self, conn:socket.socket, host:str, port:int, username:str):
        self.conn = conn
        self.host = host
        self.port = port
        self.username = username
        
    def send_data(self, data):
        if type(data) != bytes:
            data = data.encode()
        self.conn.sendall(data)
    
    def close(self):
        self.conn.close()

class Server(socket.socket):
    def __init__(self, host:str='127.0.0.1', port:int=65432, header_length=64, msg_handler_callback=None):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        
        self.header_length = header_length
        
        self.msg_handler_callback = msg_handler_callback
        
        self.bind((host, port))
        
        self.conections:set[Server_client] = set()

        
    def _client_handler(self, conn:socket.socket, addr):
        
        msg_handler = self.msg_handler_callback if self.msg_handler_callback else self.print_msg
        
        
        # waiting for get username in first of connection
        header = conn.recv(self.header_length)
        data_length = self.read_header(header)
        received_msg  = conn.recv(data_length).decode()
        received_msg = json.loads(received_msg)
        client = Server_client(conn, addr[0], addr[1], received_msg['username'])
        self.conections.add(client)
        
        connected = True
        while connected:
            try:
                header = client.conn.recv(self.header_length)
                data_length = self.read_header(header)
                received_msg  = client.conn.recv(data_length).decode()
                data = self.decorate_msg(client, received_msg)
                data_with_length = self.attach_header(data)
                
                self.send_to_all_client(client, data_with_length)
                msg_handler(json.loads(data))
            except Exception as e:
                self.conections.remove(client)
                print("ERROR-->", e)
                client.close()
    
    
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
    
    def decorate_msg(self, sender_client:Server_client, msg):
        data_with_addr = {
            'host':sender_client.host,
            'port':sender_client.port,
            'username':sender_client.username,
        }
        msg = json.loads(msg)
        data_with_addr |= msg
        data = json.dumps(data_with_addr)
        
        return data
        
        
    def send_to_all_client(self,sender_client:Server_client, data):
        
        for client in self.conections:
            if client != sender_client: 
                client.send_data(data)
            
            
    def start(self):
        self.listen()
        
        while True:
            conn, addr = self.accept()
            thread = threading.Thread(target=self._client_handler, args=(conn, addr))
            thread.start()
            print("INSIDE WHILE")
    
    
    
    def print_msg(self, data):
        print(f'{data['host']}:{data['port']} --> "{data['msg']}"')
            
            
        
    def sendmsg(self, msg:str):
        self.sendall(msg.encode())
        
        
#------------------------------------------------------------------------



class Client(socket.socket):
    
    def __init__(self, host:str='127.0.0.1', port:int=65432, header_length=64, msg_handler_callback=None):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.ADDR = (host, port)
        
        self.header_length = header_length
        self.msg_handler_callback = msg_handler_callback
        
    
    def start(self):
            
        # Waiting for get username from user and send it to server
        username = self.get_username()
        self.send_initialize_data(username)
        threading.Thread(target=self.msg_receive_handler).start()
        
        connected = True
        while connected:
            msg = self.get_input()
            data = self.decorate_msg(type='msg', msg=msg)
            
            # Dump dict to string
            data = json.dumps(data)
            data_with_length = self.attach_data_length(data)
            self.sendall(data_with_length)
    
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
    
    def route_received_data(self, data):
        if data['type'] == 'init':
            self.initializer(data)
        
        elif data['type'] == 'msg':
            self.print_msg(data)
        
        elif data['type'] == 'setup':
            
            pass

    # Get and send username to server
    def get_username(self):
        username = input("Enter your username-->")
        self.set_id(username)
        return username
        
    def send_initialize_data(self, username):
        initialize = {'type':'initializer', 'username':username}
        data_with_length = self.attach_data_length(json.dumps(initialize))
        self.sendall(data_with_length)
    
    def initializer(self, data):
        self.set_id(data['id'])
        
    def decorate_msg(self, type, msg):
        data_with_metadata = {
            'type':type,
            'msg': msg
        }
        return data_with_metadata
    
    def msg_receive_handler(self):
        
        while True:
            data_length = self.recv(self.header_length)
            
            data_length = int(data_length.strip())
            
            data = self.recv(data_length)
            
            data = json.loads(data)
            
            self.route_received_data(data)
            
        
    def set_id(self, id):
        self.id = id
        
    
    def print_msg(self, data):
        
        print(f'{data['host']}:{data['port']} --{data['username']}--> {data['msg']}')
        
        