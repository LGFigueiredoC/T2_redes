from server import *
import time
import threading

def main():
    server1 = tcp_server(host='', port=8080, listeners=1)
    
    server1.start()

    while True:
        print("Server waiting for connections...")
        conn, addr = server1.accept()
        
        thread = threading.Thread(target=server1.client_thread, args=(conn, addr), daemon=True)
        thread.start()

        


    server1.close()

if __name__ == "__main__":
    main()
    
    