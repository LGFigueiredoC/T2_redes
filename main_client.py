from client import *
import time

def main():
    client1 = tcp_client(host="127.0.0.1", port=8080, directory=None)
    
    client1.connection_loop()

    while True:
        login = input("Login: ")
        password = input("Password: ")
        if client1.authenticate(login, password):
            print("Login successful!")
            break
        else:
            print("Invalid credentials, please try again.")

    input("Press Enter to close the client...")
    client1.close()


    


if __name__ == "__main__":
    main()