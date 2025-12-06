from socket import *
import asyncio
from threading import Thread, Lock
from time import sleep
import os

class tcp_server():
    class tcp_connection():
        def __init__(self, conn, addr):
            self.conn = conn
            self.addr = addr
            self.auth = False


    def __init__(self, host='', port=8080, listeners=1):
        self.host = host
        self.port = port
        self.listeners = listeners
        self.sock = None
        self.running = False

        self.users = {
            'login1': 'password1',
        }

        self.mutex_connections = Lock()
        self.connections = []
        # list of tcp connection objects
        # conn -> socket.socket
        # addr -> (ip, port)
        # auth -> bool

    def start(self):
        print(f"Starting TCP server in port {self.port}...")
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(self.listeners)
            self.running = True

            connection_thread = Thread(target=self.connection_loop, daemon=True).start()

        except OSError as err:
            print(f"Socket error: {err}")
            exit()
    
    def accept(self):
        conn, addr = self.sock.accept()
        tcp_conn = self.tcp_connection(conn, addr)
        with self.mutex_connections:
            self.connections.append(tcp_conn)
        print(f"\nConnection accepted from {addr}")
        return tcp_conn
    
    def client_thread(self, tcp_conn):
        try:
            # authentication loop
            while not tcp_conn.auth:
                credentials = tcp_conn.conn.recv(2048)
                credentials = credentials.decode("utf-8")

                if not credentials:
                    self.remove_connection(tcp_conn)
                    return

                if self.authentication(credentials) == True:
                    tcp_conn.auth = True
                    tcp_conn.conn.send(str.encode("AUTH_OK"))
                else:
                    tcp_conn.conn.send(str.encode("AUTH_FAIL"))

            # control commands loop
            while True:
                msg = tcp_conn.conn.recv(2048)
                if not msg:
                    self.remove_connection(tcp_conn)
                    break

                text = msg.decode().strip()
                self.handle_command(tcp_conn, text)

        except ConnectionResetError:
            print(f"{tcp_conn.addr} disconnected unexpectedly.")
        
        finally:
            tcp_conn.conn.close()
            print(f"Connection with {tcp_conn.addr} closed.")

    def handle_command(self, tcp_conn, cmd):
            parts = cmd.split()

            if len(parts) == 0:
                return

            if parts[0] == "PLAY_FILE":
                if len(parts) < 2:
                    tcp_conn.conn.send(b"ERROR Missing filename\n")
                    return
                filename = parts[1]
                self.send_recorded_audio(tcp_conn, filename)
                return

            tcp_conn.conn.send(b"ERROR Unknown command\n")

    def send_recorded_audio(self, tcp_conn, filename):
        folder = "audio"  # pasta onde você guarda os arquivos
        path = os.path.join(folder, filename)




    def authentication(self, credentials: str):
        login, password = credentials.split(':')
        if login in self.users and self.users[login] == password:
            return True
        else:
            return False

    def connection_loop(self):
        while self.running:
            try:
                print("Server waiting for connections...")
                tcp_conn = self.accept()
                thread = Thread(target=self.client_thread, args=(tcp_conn,), daemon=True)
                thread.start()
            
            except OSError:
                break
        
    async def menu(self):
        while True:
            print("\nServer Menu:")
            print("1. List Connections")
            print("2. Restart Server")
            print("3. Exit\n")

            choice = await asyncio.to_thread(input, "Enter your choice: ")

            if choice == '1':
                with self.mutex_connections:
                    if not self.connections:
                        print("\nNo active connections.")
                    else:
                        print("\nActive Connections:")
                        for i, tcp_conn in enumerate(self.connections):
                            print(f"{i+1} - {tcp_conn.addr} - Auth: {tcp_conn.auth}")
            
            elif choice == '2':
                # ainda nao ta na moral
                print("Restarting server...")
                self.restart()
                print("Server restarted.")

            elif choice == '3':
                print("Exiting server...")
                self.close()
                break

    def restart(self):
        self.close()
        sleep(1)
        self.start()

    def remove_connection(self, tcp_conn):
        with self.mutex_connections:
            if tcp_conn in self.connections:
                self.connections.remove(tcp_conn)
                

    def close(self):
        try:
            self.running = False

            self.sock.close()

            with self.mutex_connections:
                for tcp_conn in self.connections:
                    tcp_conn.conn.close()

                self.connections.clear()
            print(f"Server socket closed. Port {self.port} is now free.")

        except OSError as err:
            print(f"Error closing server socket: {err}")
