from socket import *
from threading import Thread
import ssl
import pyaudio

class Server ():
    def __init__(self, ip, port, directory):
        self.ip = ip
        self.port = port

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.directory = directory