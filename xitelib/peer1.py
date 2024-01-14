import socket
import threading

class Peer1:
    def __init__(self, host, port):
        self.host = host	
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.peers = []

    def connect(self, peer_host, peer_port):
        try:
            connection = self.socket.connect((peer_host, peer_port))
            self.connections.append(connection)
            self.peers.append((peer_host, peer_port))
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
                threading.Thread(target=self.handle_connection, args=(connection,)).start()
        except Exception as e:
            print(f"Exception in listen thread: {e}")

    def handle_connection(self, connection):
        while True:
            data = connection.recv(1024)
            if not data:
                break
            print(f"Received data: {data}")
            self.broadcast_data(data)

    def broadcast_data(self, data):
        for connection in self.connections:
            try:
                connection.sendall(data)
            except socket.error as e:
                print(f"Failed to send data. Error: {e}")

    def start(self):
        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()

peer = Peer1('localhost', 3000)
peer.start()
