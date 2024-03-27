import os
import re
import argparse
import socket
import threading

CRLF = "\r\n"

class HTTPRequest:
    def __init__(self, data: bytes):
        self.data = data.decode()

        self.method, self.path, self.protocol = self.data.split(CRLF)[0].split()

        self.headers = {}
        for header in self.data.split(CRLF)[1:]:
            if not header:
                break

            key, value = header.split(": ")
            self.headers[key] = value

    def __str__(self):
        return self.data


class HTTPResponse:
    def __init__(self, status_code: int = 200, headers: dict = {}, body: bytes | str = b""):
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
            + f"{self.body.decode() if isinstance(self.body, bytes) else self.body}"
        )


def handle_client(client_socket: socket.socket, directory: str, debug: bool = False):
    try:
        # Receive data from the client and parse the HTTP request
        data = client_socket.recv(1024)
        request = HTTPRequest(data)

        if debug:
            print(request)

        # Make a decision based on the path of the request
        echo_match = re.match(r"^\/echo\/(.*)$", request.path)
        files_match = re.match(r"^\/files\/(.*)$", request.path)

        if request.path == "/":
            response = HTTPResponse()

        elif request.path == "/user-agent":
            response = HTTPResponse(body=request.headers.get("User-Agent", ""))

        elif echo_match:
            response = HTTPResponse(body=echo_match.group(1))

        elif files_match:
            file_path = os.path.join(directory, files_match.group(1))

            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    response = HTTPResponse(headers={"Content-Type": "application/octet-stream"}, body=file.read())
            else:
                response = HTTPResponse(status_code=404)

        else:
            response = HTTPResponse(status_code=404)

        if debug:
            print(response)

        # Send the response back to the client
        client_socket.sendall(response.__str__().encode())
        client_socket.close()

    except Exception as e:
        print(e)
        client_socket.close()


def main(directory: str, debug: bool = False):
    # Check if the directory exists
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist")
    
    if debug:
        print(f"Serving files from {directory}")

    # Create a server socket
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        # Start listening for incoming connections
        client_socket, client_address = server_socket.accept()

        # Handle the client in a separate thread
        threading.Thread(target=handle_client, args=(client_socket, directory, debug)).start()


if __name__ == "__main__":
    praser = argparse.ArgumentParser()

    praser.add_argument("--directory", type=str, default=".", help="Directory to serve files from")
    praser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = praser.parse_args()

    main(args.directory)
