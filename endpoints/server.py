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
        
        self.connections:set[Server_client] = set()

        
    def _client_handler(self, conn:socket.socket, addr):
        
        msg_handler = self.msg_handler_callback if self.msg_handler_callback else self.print_msg
        
        
        # Waiting for get username in first of connection
        username = self.get_username_from_client(conn)
        ack = {
            "type": "init",
            "msg": f"Welcome {username}!"
        }
        ack_msg = self.attach_header(json.dumps(ack))
        conn.sendall(ack_msg)

        client = Server_client(conn, addr[0], addr[1], username)
        self.connections.add(client)
        self.new_connection_notif(client)
        connected = True
        while connected:
            try:
                received_msg  = self.get_data_from_client(client)
                if received_msg['type'] == "terminate":
                    self.connections.remove(client)
                    print(f'**{client.username} disconnected**')
                    client.close()
                    break
                data = self.decorate_msg(client, received_msg)
                dumped_data = json.dumps(data)
                data_with_length = self.attach_header(dumped_data)
                
                self.send_to_all_client(client, data_with_length)
                msg_handler(data)
            except Exception as e:
                self.connections.remove(client)
                print("ERROR-->", e)
                client.close()
    
    
    def read_header(self, header:str) -> int:
        msg_length = header.strip()
        if msg_length:
            msg_length = int(msg_length.decode())
        else: 
            msg_length = 0
        return msg_length
    
    def get_data_from_client(self, client:Server_client) -> dict:
        header = client.conn.recv(self.header_length)
        data_length = self.read_header(header)
        received_data  = client.conn.recv(data_length).decode()
        return json.loads(received_data)
        
    def get_username_from_client(self, conn:socket.socket):
        header = conn.recv(self.header_length)
        data_length = self.read_header(header)
        received_data  = conn.recv(data_length).decode()
        data = json.loads(received_data)
        return data['username']
    
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
    
    def decorate_msg(self, sender_client:Server_client, msg:dict):
        data_with_addr = {
            'host':sender_client.host,
            'port':sender_client.port,
            'username':sender_client.username,
        }
        
        data_with_addr |= msg
        
        return data_with_addr
    
        
        
    def send_to_all_client(self,sender_client:Server_client, data):
        
        for client in self.connections:
            if client != sender_client: 
                client.send_data(data)
            
            
    def start(self):
        self.listen()
        
        while True:
            conn, addr = self.accept()
            thread = threading.Thread(target=self._client_handler, args=(conn, addr))
            thread.start()
    
    
    
    def print_msg(self, data):
        print(f'{data['host']}:{data['port']} --> "{data['msg']}"')
            
            
    
    def new_connection_notif(self, client:Server_client):
        print(f'NEWCONNECTION:{client.username} connected with host {client.host}:{client.port}')
    
    def sendmsg(self, msg:str):
        self.sendall(msg.encode())