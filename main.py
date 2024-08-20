from config.settings import HOST, PORT
from entities.server import Server

if __name__ == "__main__":
    server = Server(HOST, PORT)
    server.run()
