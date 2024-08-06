from ..usecases.connect_client_usecase import connect_client
from ..usecases.register_client_usecase import register_client

request_handlers = {"01": register_client, "03": connect_client}


def handle_request(req, conn, address):
    code = req[:2]
    handler = request_handlers.get(code)
    if handler:
        handler(req[2:], conn, address)
    else:
        conn.sendall("0000000000000".encode())
