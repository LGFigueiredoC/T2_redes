from server import *
import time
import threading

async def main():
    control_server = tcp_server(host='', port=8080, listeners=1)
    
    control_server.start()

    await control_server.menu()
    

if __name__ == "__main__":
    asyncio.run(main())
