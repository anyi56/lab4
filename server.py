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
        if not os.path.exists(self.filepath):
            self.main_socket.sendto(f"ERR {self.filename} NOT_FOUND".encode(), self.client_addr)
            return
        transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        transfer_socket.bind(('0.0.0.0', self.port))
        
        filesize = os.path.getsize(self.filepath)
        response = f"OK {self.filename} SIZE {filesize} PORT {self.port}"
        self.main_socket.sendto(response.encode(), self.client_addr)
        
        with open(self.filepath, 'rb') as file:
            while True:
                data, addr = transfer_socket.recvfrom(2048)
                request = data.decode().split()
                
                if request[0] == "FILE" and request[2] == "GET":
                    start = int(request[4])
                    end = int(request[6])
                    file.seek(start)
                    chunk = file.read(end - start + 1)
                    encoded = base64.b64encode(chunk).decode()
                    response = f"FILE {self.filename} OK START {start} END {end} DATA {encoded}"
                    transfer_socket.sendto(response.encode(), addr)
                
                elif request[0] == "FILE" and request[2] == "CLOSE":
                    transfer_socket.sendto(f"FILE {self.filename} CLOSE_OK".encode(), addr)
                    break
        
        transfer_socket.close()
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