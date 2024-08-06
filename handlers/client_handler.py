from .request_handler import handle_request


def handle_client(conn, addr):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        req = data.decode()
        handle_request(req, conn, addr)
    
    conn.close()
