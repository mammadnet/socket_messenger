import socket


class Connection(socket.socket):
    def __init__(self, server:bool=False, host:str='127.0.0.1', port:int=65432):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        
        if server:
            self.bind((host, port))

        
    def receive(self, bufsize:int=1024):
        data = self.recv(bufsize)
        if data:
            return data.decode()
        else:
            return data
        
    def sendmsg(self, msg:str):
        self.sendall(msg.encode())
        