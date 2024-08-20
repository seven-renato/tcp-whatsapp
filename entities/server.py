import socket
import threading
from config.settings import HOST, PORT

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
        self.created_clients = 1000000000000
        self.connected_clients = {}
        self.unreceived_messages = {}

        self.codes = {
            '01': self.register_client,
            '03': self.connect_client,
            '05': self.send_message,
            '08': self.confirm_read
        }

    def register_client(self, payload, conn):
        id = str(self.created_clients)
        self.created_clients += 1
        res = '02' + id
        self.unreceived_messages[id] = []
        print(f"Registered client: {id}")
        print(f"Unreceived messages: {self.unreceived_messages}") 
        conn.sendall(res.encode()) # 02 + id

    def connect_client(self, payload, conn):
        self.connected_clients[payload] = conn
        print(f"Connected clients: {self.connected_clients}")
        for message in self.unreceived_messages[payload]:
            print("Delevering unreceived message...")
            self.deliver_message(conn, message)
        self.unreceived_messages[payload] = []
        print("LOGGED!", payload)
        print(type(payload))


    def send_message(self, payload, conn):
        dst = payload[13:26] # 05
        src = payload[:13]
        print(f"{src} Sending message to {dst}" + " " + payload)
        server_payload = payload
        if dst in self.connected_clients: # Se quem vai receber a mensagem está conectado, entrega a mensagem
            print("Enviando mensagem...")
            conn = self.connected_clients[dst]
            self.deliver_message(conn, server_payload)
        else: # Se não, armazena a mensagem para entrega futura na conexão
            print("Armazenando mensagem...")
            if int(dst) <= self.created_clients and int(dst) >= 1000000000000: 
                self.unreceived_messages[dst].append(server_payload)
            else:
                conn.sendall("0000000000000".encode())

    def deliver_message(self, receiver_conn, message): # Message = 100000000000001000000000000 11724109292 TESTANDOPROTOCOLOTCP
        dst_message = '06' + message
        receiver_conn.sendall(dst_message.encode()) # 06 + message - Para o destino
        timestamp = message[26:36]
        dst = message[13:26]
        src_message = '07' + dst + timestamp
        src = message[:13]
        print("OLHA O SRC --->", src)
        if src in self.connected_clients:
            conn = self.connected_clients[src]
            conn.sendall(src_message.encode()) # 07 + message - Quem vai receber
        else:
            self.unreceived_messages[src].append(message)
    
    def confirm_read(self, payload, conn):
        src = payload[:13]
        timestamp = payload[13:26]
        if src in self.connected_clients:
            conn = self.connected_clients[src]
            dst = list(self.connected_clients.keys())[list(self.connected_clients.values()).index(conn)]
            conn.sendall(f'09{dst}{timestamp}'.encode())

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server running on {HOST}:{PORT}")
            while True:
                conn, _ = s.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, args=((conn,))
                )
                client_thread.start()

    def handle_client(self, conn):
        try:
            while True:
                print("Minha conexao e: ", conn)
                data = conn.recv(256)
                if not data or data.decode() == "00":
                    break
                req = data.decode()
                print(f"Received: {req}")
                self.handle_request(req, conn)
        except ConnectionResetError:
            print("Connection reset by peer")
            self.disconnect_client(conn)
        except ConnectionAbortedError:
            print("Connection aborted")
            self.disconnect_client(conn)
        except Exception as e:
            print("An error occurred"*100)
            import traceback
            traceback.print_exc()
            print("Erro ->", str(e))
        self.disconnect_client(conn)
    

    def handle_request(self, req, conn):
        code = req[:2]
        handler = self.codes.get(code)
        
        if handler:
            handler(req[2:], conn)
        else:
            conn.sendall("0000000000000".encode())

    def disconnect_client(self, conn):
        print("Client disconnected")
        if conn in self.connected_clients.values():
            user_id = list(self.connected_clients.keys())[list(self.connected_clients.values()).index(conn)]
            print(f"Disconnected client: {user_id}")
            if user_id in self.connected_clients:
                del self.connected_clients[user_id]
        print(f"Connected clients: {self.connected_clients}")
        conn.close()

