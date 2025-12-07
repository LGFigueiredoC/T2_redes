from socket import *
from threading import Thread
from time import sleep
import asyncio
import pyaudio
import wave
import pygame
import recorder


class tcp_client():
    def __init__(self, host, port, directory):
        self.host = host
        self.port = port
        self.sock = None
        self.directory = directory

        self.paused = False
        self.running = False

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
    
    def authentication_loop(self):
        i = 5
        while True:
            login = input("Login: ")
            password = input("Password: ")
            if self.authenticate(login, password):
                print("Login successful!")
                break
            else:
                i -= 1
                if i == 0:
                    print("Maximum authentication attempts reached.")
                    self.close()
                    exit()

                print(f"Invalid credentials, please try again. {i} attempts left.")

    def command_loop(self):
        while True:
            print("\nMenu:")
            print("1. PLAY LIVE")
            print("2. PLAY RECORDED")
            print("3. SHOW AVAILABLE FILES")
            print("4. QUIT")

            choice = input("Enter your choice:")
            
            if choice == '1':
                filename = input("Enter file name to play: ")
                record = input("Save content? (y/n) ")
                self.sock.send(str.encode("PLAY_LIVE"))
                self.receive_live(filename, record)
                # rodar live udp
            elif choice == '2':
                filename = input("Enter file name to play: ")
                record = input("Save content? (y/n) ")

                save = (record.lower() == "y")
                self.receive_recorded(filename, save)

            elif choice == '3':
                # mandar request pro servidor
                pass
            elif choice == '4':
                break
            else:
                print("Invalid option")

    # def request_live(self, filename):
    #     cmd = f"PLAY_FILE {filename}"
    #     self.sock.send(cmd.encode())

    def receive_thread(self):
        while self.running:
            data = self.sock.recv(1024)
            if data == b"END_STREAM":
                self.running = False
                break
            self.buffer.append(data)
    
    def play_thread(self):
        while self.running:
            if self.is_paused:
                sleep(0.1)
                continue

            if len(self.buffer) == 0:
                sleep(0.01)
                continue

            chunk = self.buffer.pop(0)
            sound = pygame.mixer.Sound(buffer=chunk)
            sound.play()



    def receive_live(self, filename, save_file):

        chunks = []
        pygame.mixer.init()
        rec = recorder.Recorder()
        audio_data = []

        receive_thread = Thread(target=self.receive_thread())
        play_thread = Thread(target=self.play_thread())

        print("Controle de reprodução:")
        print("1. PAUSE/RESUME")
        print("2. STOP")
        while self.running:
            cmd = input()
            if cmd == "1":
                self.paused = not self.paused
            elif cmd == "2":
                self.running = False
                break

        receive_thread.join()
        play_thread.join()
        

        print("Transmissão encerrada")

        if save_file:
            obj = wave.open("audio.wav", "wb")
            obj.setnchannels(rec.channels)
            obj.setsampwidth(rec.rec.get_sample_size(rec.channels))
            obj.setframerate(rec.rate/2)
            obj.writeframes(b"".join(chunks))

    
    def receive_recorded(self, filename, save_file):
        chunks = []
        rec = recorder.Recorder()

        while True:
            data = self.sock.recv(1024)
            if data == b"END_STREAM":
                break
            chunks.append(data)

        print("Arquivo recebido")

        obj = wave.open("audio.wav", "wb")
        obj.setnchannels(rec.channels)
        obj.setsampwidth(rec.rec.get_sample_size(rec.channels))
        obj.setframerate(rec.rate/2)
        obj.writeframes(b"".join(chunks))


    def close(self):
        try:
            self.sock.close()
            print("Connection closed.")
        except OSError as err:
            print(f"Error closing socket: {err}")

    