import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    data = client_socket.recv(1024)
    print(f"Received {data.decode()}")

    client_socket.sendall("HTTP/1.1 200 OK\r\n\r\n".encode())
    client_socket.close()


if __name__ == "__main__":
    main()
