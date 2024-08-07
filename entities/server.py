import socket
import threading


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected_clients = {}
        self.created_clients = {}

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print("Server running...")
            while True:
                conn, addr = s.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, args=(conn, addr)
                )
                client_thread.start()

    def _handle_client(self, conn, addr):
