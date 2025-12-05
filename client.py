from socket import *
from threading import Thread
from time import sleep
import pyaudio


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
    
    def connection_loop(self):
        attempts = 0
        while self.start() == False:
            for s in range(5, 0, -1):
                print(f"Retrying connection in {s} seconds...", end='\r')
                sleep(1)

        print("Retrying connection:                     ")
        attempts += 1
        if attempts == 5:
            print("Unable to connect. Exiting.")
            exit()

    def authenticate(self, login, password):
        try:
            credentials = f"{login}:{password}"
            self.sock.send(str.encode(credentials))

            response = self.sock.recv(1024)
            if response.decode() == "AUTH_OK":
                return True
            elif response.decode() == "AUTH_FAIL":
                return False
            else:
                raise OSError("[Errno ##] Invalid authentication response from server")
        
        except OSError as err:
            print(f"Authentication error: {err}")
            return False
    
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

    