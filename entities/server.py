import socket
import threading
import time
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
        id = payload
        self.connected_clients[id] = conn
        print(f"Connected clients: {self.connected_clients}")
        
        self.receive_unreceived_messages(id, conn)
        print("LOGGED!", id)
        print(type(id))


    def send_message(self, payload, conn):
        src = payload[:13]
        dst = payload[13:26]
        message = '06' + payload
        
        print(f"{src} Sending message to {dst}: {payload}")
        if dst in self.connected_clients: # Se quem vai receber a mensagem está conectado, entrega a mensagem
            print("Enviando mensagem...")
            conn = self.connected_clients[dst]
            conn.sendall('07' + dst + time.time())

            receiver_conn = self.connected_clients[dst]
            receiver_conn.sendall(message)
            return
        
        # Se não, armazena a mensagem para entrega futura na conexão
        print("Armazenando mensagem...")
        if int(dst) <= self.created_clients and int(dst) >= 1000000000000: 
            self.unreceived_messages[dst].append(message)
        else:
            conn.sendall("0000000000000".encode())
    
    def receive_unreceived_messages(self, id, conn):
        print("Delevering unreceived message...")
        for message in self.unreceived_messages[id]:
            if message[:2] == '06':
                src = message[:13]
                dst = message[13:26]
                timestamp = message[26:36]
                src_message = '07' + dst + timestamp
                if src in self.connected_clients:
                    src_conn = self.connected_clients[src]
                    src_conn.sendall(src_message.encode())
                else:
                    self.unreceived_messages[src].append(src_message)
            
            conn.sendall(message.encode())
        self.unreceived_messages[id] = []
    
    def confirm_read(self, payload, conn):
        src = payload[:13]
        dst = payload[13:26]
        timestamp = payload[26:36]
        if src in self.connected_clients:
            conn = self.connected_clients[src]
            conn.sendall(f'09{src}{dst}{timestamp}'.encode())

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

