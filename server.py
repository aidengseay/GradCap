################################################################################
# SERVER SUPPORTING FUNCTIONS
# Created by Aiden Seay | Fall 2026
################################################################################
# IMPORTS

from config import SERVER_HOST, SERVER_PORT
import socket

################################################################################

def start():

    # set server socket
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(1)

    while True:

        client, address = server.accept()

        print("Client connected from:", address)

        request = client.recv(1024)

        print("Request:")
        print(request)

        client.send(
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "Connection: close\r\n"
            "\r\n"
            "Hello from GradCap!"
        )

        client.close()

################################################################################