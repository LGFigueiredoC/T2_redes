from socket import *

class tcp_server():
    def __init__(self, host='', port=8080, listeners=1):
        self.host = host
        self.port = port
        self.listeners = listeners
        self.sock = None

        self.connections = []

    def start(self):
        print("Starting TCP server...")
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.bind((self.host, self.port))
            self.sock.listen(self.listeners)

        except OSError as err:
            print(f"Socket error: {err}")
            return False
    
    def accept(self):
        conn, addr = self.sock.accept()
        self.connections.append((conn, addr))
        print(f"Connection accepted from {addr}")
        return conn, addr
    
    def client_thread(self, conn, addr):
        conn.send(str.encode(f"Welcome to the server, {addr}!\n"))
        while True:
            data = conn.recv(2048)
            if not data:
                break
            print(f"Received from {addr}: {data.decode()}")
        


    
    
    def close(self):
        try:
            self.sock.close()
            print("Server socket closed.")
        except OSError as err:
            print(f"Error closing server socket: {err}")

