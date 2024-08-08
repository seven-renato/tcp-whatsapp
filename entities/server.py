import socket
import threading

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
        self.created_clients = 1000000000000
        self.connected_clients = {}
        self.unreceived_messages = {'1000000': []}

        self.codes = {
            '01': self.register_client,
            '03': self.connect_client,
        }

    def register_client(self, payload, conn):
        id = str(len(self.created_clients))
        self.created_clients += 1
        res = '02' + id
        
        conn.sendall(res.encode())

    def connect_client(self, payload, conn):
        self.connected_clients[payload] = conn

        unreceived_messages = self.unreceived_messages[payload]
        for message in unreceived_messages:
            conn.sendall(message.encode())
        #enviar mensagens pendentes se tiver

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print("Server running...")
            while True:
                conn, _ = s.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, args=(conn)
                )
                client_thread.start()

    def handle_client(self, conn):
        while True:
            data = conn.recv(256)
            if not data:
                break
            req = data.decode()
            self.handle_request(req, conn)
        
        user_id = list(self.connected_clients.keys())[list(self.connected_clients.values()).index(conn)]
        del self.connected_clients[user_id]
        conn.close()

    def handle_request(self, req, conn):
        code = req[:2]
        handler = self.codes.get(code)
        
        if handler:
            handler(req[2:])
            
        else:
            conn.sendall("0000000000000".encode())
