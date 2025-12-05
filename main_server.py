from server import *
import time
import threading

async def main():
    server1 = tcp_server(host='', port=8080, listeners=1)
    
    server1.start()

    await server1.menu()
    

if __name__ == "__main__":
    asyncio.run(main())
