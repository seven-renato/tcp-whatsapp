import socket

def register_client(client):
    client.send("01".encode())  # Código 01 para registrar cliente
    response = client.recv(1024).decode()
    print(f"Server response: {response}")
    return response[2:]  # Retorna o ID do cliente registrado

def connect_client(client, client_id):
    client.send(f"03{client_id}".encode())  # Código 03 para conectar cliente

def send_message(client, src_id, dst_id, message):
    # Mensagem no formato: "05" + src_id + dst_id + timestamp + message
    import time
    timestamp = time.strftime('%Y%m%d%H%M%S')
    full_message = f"05{src_id}{dst_id}{timestamp}{message}"
    client.send(full_message.encode())
    response = client.recv(1024).decode()
    print(f"Server response: {response}")

def receive_message(client):
    response = client.recv(1024).decode()
    print(f"Received message: {response}")

def main():
    host = "0.tcp.sa.ngrok.io"  # Host do servidor
    host = "127.0.0.1"
    port = 65431  # Porta do servidor

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    client_id = None

    while True:
        print("1. Register Client")
        print("2. Connect Client")
        print("3. Send Message")
        print("4. Receive Message")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            client_id = register_client(client)
        elif choice == "2":
            print(client_id)
            if client_id:
                connect_client(client, client_id)
            else:
                print("You need to register first.")
        elif choice == "3":
            if client_id:
                dst_id = input("Enter destination client ID: ")
                message = input("Enter the message: ")
                send_message(client, client_id, dst_id, message)
            else:
                print("You need to register and connect first.")
        elif choice == "4":
            receive_message(client)
        elif choice == "5":
            client.sendall(b"00")
            client.close()
            break
        else:
            print("Invalid choice. Please try again.")

    client.close()

if __name__ == "__main__":
    main()
