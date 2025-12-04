from client import *
import time

def main():
    client1 = tcp_client(host="127.0.0.1", port=8080, directory=None)
    
    attempts = 0
    while client1.start() == False:
        for s in range(5, 0, -1):
            print(f"Retrying connection in {s} seconds...", end='\r')
            time.sleep(1)

        print("Retrying connection:                     ")
        attempts += 1
        if attempts == 5:
            print("Unable to connect. Exiting.")
            exit()

    client1.send_message("Obrigado!")


    client1.close()


if __name__ == "__main__":
    main()