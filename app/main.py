import re
import socket

CRLF = "\r\n"


class HTTPRequest:
    def __init__(self, data: bytes):
        self.data = data.decode()
        self.method, self.path, self.protocol = self.data.split(CRLF)[0].split()

    def __str__(self):
        return self.data


class HTTPResponse:
    def __init__(self, status_code: int = 200, headers: dict = {}, body: str = ""):
        self.status_code = status_code
        self.headers = headers
        self.body = body

        if "Content-Type" not in self.headers and self.body:
            self.headers["Content-Type"] = "text/plain"

        if "Content-Length" not in self.headers and self.body:
            self.headers["Content-Length"] = len(self.body)

    def __str__(self):
        STATUS_CODE_STRINGS = {
            200: "OK",
            404: "Not Found",
        }

        return (
            f"HTTP/1.1 {self.status_code} {STATUS_CODE_STRINGS[self.status_code]}"
            + CRLF
            + f"{''.join([f'{key}: {value}{CRLF}' for key, value in self.headers.items()])}"
            + CRLF
            + f"{self.body}"
        )


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    # Start listening for incoming connections
    client_socket, client_address = server_socket.accept()

    # Receive data from the client and parse the HTTP request
    data = client_socket.recv(1024)
    request = HTTPRequest(data)
    print(request)

    # Make a decision based on the path of the request
    echo_match = re.match(r"^\/echo\/(.*)$", request.path)
    if request.path == "/":
        response = HTTPResponse()
    elif echo_match:
        response = HTTPResponse(body=echo_match.group(1))
    else:
        response = HTTPResponse(status_code=404)
    print(response)

    # Send the response back to the client
    client_socket.sendall(response.__str__().encode())
    client_socket.close()


if __name__ == "__main__":
    main()
