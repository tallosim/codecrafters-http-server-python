import socket

CRLF = "\r\n"

class HTTPRequest:
    def __init__(self, data: bytes):
        self.data = data.decode()
        self.method, self.path, self.protocol = self.data.split(CRLF)[0].split()

class HTTPResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code

    def __str__(self):
        STATUS_CODE_STRINGS = {
            200: "OK",
            404: "Not Found",
        }

        return f"HTTP/1.1 {self.status_code} {STATUS_CODE_STRINGS[self.status_code]}{CRLF}{CRLF}"


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    # Start listening for incoming connections
    client_socket, client_address = server_socket.accept()

    # Receive data from the client and parse the HTTP request
    data = client_socket.recv(1024)
    request = HTTPRequest(data)

    # Make a decision based on the path of the request
    response = HTTPResponse(200) if request.path == "/" else HTTPResponse(404)

    # Send the response back to the client
    client_socket.sendall(response.__str__().encode())
    client_socket.close()


if __name__ == "__main__":
    main()
