import socket
import threading
import json

class Client(socket.socket):
    
    def __init__(self, host:str='127.0.0.1', port:int=65432, header_length=64, data_handler_callback=None):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.ADDR = (host, port)
        
        self.header_length = header_length
        self.data_handler_callback = data_handler_callback
        self.is_connected = False
        self.id = None
    
    def set_receive_data_handler(self, callback):
        self.data_handler_callback = callback
    
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
        data_handler = self.data_handler_callback if self.data_handler_callback else self.print_msg
        if data['type'] == 'init':
            self.is_connected = True
            return
        elif data['type'] == 'msg':
            data_handler(data)
        
        elif data['type'] == 'setup':
            
            pass
    
    def close_connection(self):
        data = {'type':'terminate'}
        self.send_data(data)
        self.is_connected = False

    def get_username(self):
        username = input("Enter your username-->")
        self.set_id(username)
        return username
        
    def send_initialize_data(self, username):
        initialize = {'type':'initializer', 'username':username}
        data_with_length = self.attach_data_length(json.dumps(initialize))
        self.sendall(data_with_length)
    
    def initializer(self, username):
        try:
            self.connect(self.ADDR)
            self.send_initialize_data(username)
            self.id = username
            threading.Thread(target=self.msg_receive_handler, daemon=True).start()
            return True
        except Exception:
            return False
        
    def send_data(self, data:dict):
        if isinstance(data, str):
            data = {'type': 'msg', 'msg': data}
        data = json.dumps(data)
        data_with_length = self.attach_data_length(data)
        self.sendall(data_with_length)
        
    def decorate_msg(self, type, msg):
        data_with_metadata = {
            'type':type,
            'msg': msg
        }
        return data_with_metadata
    
    def msg_receive_handler(self):
        while True:
            try:
                data_length = self.recv(self.header_length)
                data_length = int(data_length.strip())
                data = self.recv(data_length)
                data = json.loads(data)
                self.route_received_data(data)
            except Exception as e:
                print(f"Error in receive handler: {e}")
                self.is_connected = False
                break
    
    def set_id(self, id):
        self.id = id
        
    def print_msg(self, data):
        
        print(f'{data['host']}:{data['port']} --{data['username']}--> {data['msg']}')
        
        