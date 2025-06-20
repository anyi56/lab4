import socket
import os
import base64
class Client:
    def __init__(self, server_host,server_port, filelist_file):
        self.server_host = server_host
        self.server_port = server_port
        self.filelist_file = filelist_file
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def send_with_retry(self, message, addr=None):
        max_retries = 5
        if addr is None:
            addr = (self.server_host, self.server_port)
        
        retries = 0
        current_timeout = 2
        
        while retries < max_retries:
            try:
                self.socket.sendto(message.encode(), addr)
                self.socket.settimeout(current_timeout)
                data, _ = self.socket.recvfrom(65536)
                return data.decode()
            except socket.timeout:
                retries += 1
                print(f" Timeout, retrying {retries}/{max_retries}...")
                current_timeout *= 2
        
        raise Exception("Failed to send message after retries.")
    def download_file(self, filename):
        print(f"\nDownloading: {filename}")
        try:
            response = self.send_with_retry(f"DOWNLOAD {filename}\n", (self.server_host, self.server_port))
            if not response:
                print(f"Failed to download {filename} after retries.")
                return

            parts = response.split()

            # Check if the response has enough parts and starts with the expected prefix
            if len(parts) < 7 or parts[0] != "FILE":
                print(f"Invalid response from server: {response}")
                return

            filesize = int(parts[4])
            port = int(parts[6])

            if not os.path.exists("Client"):
                os.makedirs("Client")

            received = 0
            with open(os.path.join("Client", filename), 'wb') as f:
                for start in range(0, filesize, 1000):
                    end = min(start + 999, filesize - 1)

                    while True:
                        try:
                            request = f"FILE {filename} GET START {start} END {end}"
                            response = self.send_with_retry(request, (self.server_host, port))

                            parts = response.split()

                            # Check if the response has enough parts and starts with the expected prefix
                            if len(parts) < 9 or parts[0] != "FILE" or parts[1] != filename or parts[2] != "OK":
                                print(f"Invalid response from server: {response}")
                                break

                            data_start = int(parts[4])
                            data_end = int(parts[6])
                            encoded = ' '.join(parts[8:])
                            chunk = base64.b64decode(encoded.encode())
                            f.write(chunk)
                            received += len(chunk)
                            print(f"\rDownloading : {received}/{filesize} {'*' * (received//1000 + 1)}", end='')
                            break

                        except Exception as e:
                            print(f"\n {start}-{end} error: {str(e)}")
                            if "out of range" in str(e):
                                raise
                            continue

            print(f"\nDownload succeed: {filename}")
            return True

        except Exception as e:
            print(f"\nDownload failed: {str(e)}")
            return False
    
    def start(self):
        try:
            with open(self.filelist_file, 'r') as f:
                files = [line.strip() for line in f if line.strip()]
            
            for filename in files:
                self.download_file(filename)
                
        except Exception as e:
            print(f"Client error: {str(e)}")
        finally:
            self.socket.close()
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python client.py <server_host> <server_port> <filelist_file>")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    filelist_filename = sys.argv[3]

    client = Client(server_host, server_port, filelist_filename) 
    client.start()