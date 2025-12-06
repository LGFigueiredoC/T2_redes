from client import *
import time

def main():
    client1 = tcp_client(host="127.0.0.1", port=8080, directory="recordings/")
    
    client1.connection_loop()

    client1.authentication_loop()

    client1.command_loop()

    client1.close()


    


if __name__ == "__main__":
    main()