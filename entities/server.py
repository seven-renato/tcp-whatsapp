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
            '05': self.send_message,
            '08': self.confirm_read
        }

    def deliver_message(self, conn, message):
        send_message = '06' + message[2:]
        deliver_message = '07' + message[2:]
        conn.sendall(send_message.encode())
        src = message[2:16]
        if src in self.connected_clients:
            conn = self.connected_clients[src]
            conn.sendall(deliver_message.encode())
        else:
            self.unreceived_messages[src].append(message)
    
    def confirm_read(self, payload, conn):
        src = payload[:14]
        timestamp = payload[14:25]
        if src in self.connected_clients:
            conn = self.connected_clients[src]
            dst = list(self.connected_clients.keys())[list(self.connected_clients.values()).index(conn)]
            conn.sendall(f'09{dst}{timestamp}'.encode())

    def register_client(self, payload, conn):
        id = str(len(self.created_clients))
        self.created_clients += 1
        res = '02' + id
        self.unreceived_messages[id] = []
        
        conn.sendall(res.encode())

    def connect_client(self, payload, conn):
        self.connected_clients[payload] = conn

        unreceived_messages = self.unreceived_messages[payload]
        for message in unreceived_messages:
            self.deliver_message(conn, message)
        self.unreceived_messages[payload] = []

    def send_message(self, payload, conn):
        dst = payload[14:28]
        server_payload = payload
        if dst in self.connected_clients:
            conn = self.connected_clients[dst]
            self.deliver_message(conn, server_payload)
        else:
            self.unreceived_messages[dst].append(server_payload)

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
