import socket
import threading
import os
import base64
import random
class FileDownloader(threading.Thread):
    def __init__(self, filename, client_addr, main_socket):
        threading.Thread.__init__(self)
        self.filename = filename
        self.client_addr = client_addr
        self.main_socket = main_socket
        self.port = random.randint(50000, 51000)
        self.filepath = os.path.join("Server", filename)

    def run(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as file:
                data = file.read()
                self.client_socket.sendall(data)
            print(f"Sent file {self.filename} to client.")
        else:
            self.client_socket.sendall(b"File not found.")
            print(f"File {self.filename} not found.")

        self.client_socket.close()
def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Server is listening on port {port}")
    while True:
        data, addr = server_socket.recvfrom(1024)
        message = data.decode().split()
        if message[0] == "DOWNLOAD":
            filename = message[1]            
            print(f"Accepted connection from {addr}")
            FileDownloader(server_socket, filename,addr).start()
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    start_server(port)