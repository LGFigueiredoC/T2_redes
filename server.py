from socket import *
import asyncio
from threading import Thread, Lock
from time import sleep
import os
import recorder
import ssl
import wave
import json

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
        
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile="server.crt", keyfile="server.key")

        with open ("client_info.json", "r") as info:
            self.users = json.load(info)

        self.audio_dir = "./audio"

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
        try:
            conn, addr = self.sock.accept()
            conn_ssl = self.context.wrap_socket(conn, server_side=True)
            tcp_conn = self.tcp_connection(conn_ssl, addr)
            with self.mutex_connections:
                self.connections.append(tcp_conn)
            print(f"\nConnection accepted from {addr}")
            return tcp_conn
        
        except ssl.SSLError as err:
            print(f"SSL Handshake failed: {err}")
            conn.close()
            return None
    
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
                    break
                else:
                    tcp_conn.conn.send(str.encode("AUTH_FAIL"))

            # control commands loop
            while True:
                # print("Esperando comando")
                msg = tcp_conn.conn.recv(2048)
                if not msg:
                    self.remove_connection(tcp_conn)
                    break
                # print(msg)
                text = msg.decode().strip()
                self.handle_command(tcp_conn, text)


        except ConnectionResetError:
            print(f"{tcp_conn.addr} disconnected unexpectedly.")
        
        finally:
            tcp_conn.conn.close()
            print(f"Connection with {tcp_conn.addr} closed.")

    def handle_command(self, tcp_conn, cmd):


        if cmd == "PLAY_LIVE":
            self.send_live_audio(tcp_conn)
            return
        
        elif cmd == "SHOW_FILES":
            self.send_available_files(tcp_conn)
            return
        
        elif cmd.startswith("PLAY_RECORDED"):
            _, filename = cmd.split()
            self.send_recorded_audio(tcp_conn, filename)


        tcp_conn.conn.send(b"ERROR Unknown command\n")

    def send_available_files(self, tcp_conn):
        files = os.listdir(self.audio_dir)

        output_lines = []
        for i, filename in enumerate(files):
            output_lines.append(f"{i + 1}. {filename}")

        msg = "\n".join(output_lines)

        tcp_conn.conn.send(msg.encode())

    def send_recorded_audio(self, tcp_conn, filename):
        file_path = os.path.join(self.audio_dir, filename)
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            error_msg = b"END_STREAM"
            tcp_conn.conn.send(error_msg)
            return

        print(f"Streaming recorded audio '{filename}' to {tcp_conn.addr}...")
        
        try:
            with wave.open(file_path, 'rb') as wf:
                # Obter informações do arquivo
                channels = wf.getnchannels()
                sampwidth = wf.getsampwidth()
                framerate = wf.getframerate()
                
                # Calcular bytes por frame
                bytes_per_frame = channels * sampwidth
                
                # Usar o mesmo tamanho de chunk do recorder (1024 frames)
                chunk_frames = 1024
                chunk_bytes = chunk_frames * bytes_per_frame
                
                # Calcular delay para simular streaming em tempo real
                # delay = (chunk_frames / framerate) * 0.9  # 90% da velocidade real
                
                print(f"File info: {channels}ch, {sampwidth}bytes, {framerate}Hz")
                
                while True:
                    data = wf.readframes(chunk_frames)
                    if not data:
                        break
                    
                    tcp_conn.conn.send(data)
                    # sleep(delay)  # Opcional: descomente para simular streaming real

                print(f"Successfully streamed '{filename}'.")
                
        except Exception as e:
            print(f"Error streaming file {filename}: {e}")
            
        finally:
            try:
                tcp_conn.conn.send(b"END_STREAM") 
            except:
                pass

    def send_live_audio(self, tcp_conn):

        r = recorder.Recorder()

        stream = r.rec.open(
            format=r.format,
            channels=r.channels,
            rate=r.rate,
            input=True,
            frames_per_buffer=r.frames_p_buffer
        )

        print(f"Streaming live audio to {tcp_conn.addr}...")

        try:
            while True:
                chunk = stream.read(r.frames_p_buffer)
                r.frames.append(chunk)
                tcp_conn.conn.send(chunk)

        except (ConnectionResetError, BrokenPipeError, OSError):
            print(f"Stream for {tcp_conn.addr} finished.")
        
        except Exception as e:
            print(f"Error during streaming: {e}")
        
        finally:
            try:
                tcp_conn.conn.send(str.encode("END_STREAM"))
            except:
                pass
        
            stream.stop_stream()
            stream.close()
            r.rec.terminate()


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
                if tcp_conn != None :
                    thread = Thread(target=self.client_thread, args=(tcp_conn,), daemon=True)
                    thread.start()
            
            except OSError:
                break
        
    async def menu(self):
        while True:
            print("\nSERVER MENU:")
            print("[1] LIST CONNECTIONS")
            print("[2] EXIT\n")

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
