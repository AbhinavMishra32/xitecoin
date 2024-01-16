from http import server
import socket
import threading
import json
import time


class Peer:
    def __init__(self, host, port):
        self.host = host	
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []

    def connect(self, peer_host, peer_port):
        try:
            connection = self.socket.connect((peer_host, peer_port))
            self.connections.append(connection)
        except socket.error as e:
            print(f"Failed to connect to: {peer_host}, {peer_port}. Error: {e}")
    
    def listen(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)        
            print(f"Listening for connections on {self.host}:{self.port}")
            while True:
                connection, address = self.socket.accept()
                self.connections.append(connection)
                print(f"Accepted connection from {address}")
        except Exception as e:
            print(f"Exception in listen thread: {e}")

    def send_data(self, data):
        for connection in self.connections:
            try:
                connection.sendall(data.encode())
            except socket.error as e:
                print(f"Failed to send data. Error: {e}")
            
    def start(self, peers=[]):
        listen_thread = threading.Thread(target = self.listen)
        listen_thread.start()

        for peer in peers:
            self.connect(*peer)


# if __name__ == "__main__":
#     import sys
#     port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
#     peer = Peer('0.0.0.0', port)
#     peer.start()
peer1 = Peer('localhost', 3000)
peer1.start()