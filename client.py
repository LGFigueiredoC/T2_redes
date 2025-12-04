from socket import *
from threading import Thread


class tcp_client():
    def __init__(self, host, port, directory):
        self.host = host
        self.port = port
        self.sock = None
        self.directory = directory

    def start(self):
        print("Starting TCP client...")
        try:
            self.sock = socket(family=AF_INET, type=SOCK_STREAM)
            self.sock.connect((self.host, int(self.port)))
            print(f"Connected to server at {self.host}:{self.port}")
        
        except OSError as err:
            print(f"Socket error: {err}")
            return False
        
        return True
    
    def send_message(self, message):
        try:
            response = self.sock.recv(2048)
            print(f"Server says: {response.decode()}")

            self.sock.send(str.encode(message))
        
        except OSError as err:
            print(f"Message error: {err}")
    
    def close(self):
        try:
            self.sock.close()
            print("Connection closed.")
        except OSError as err:
            print(f"Error closing socket: {err}")

    