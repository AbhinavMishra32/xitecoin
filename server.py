from http import server
import socket
import threading
import json
import time

HEADER = 64
PORT = 5000
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

known_nodes = ['localhost:5000']
def handle_client(conn, addr):
	global known_nodes
	data = conn.recv(1024)
	nodes = json.loads(data)
	known_nodes += [node for node in nodes if node not in known_nodes]
	print(f"Updated nodes: {known_nodes}")

def start_server():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(('localhost', PORT))
	server.listen()
	while True:
		conn, addr = server.accept()
		handle_client(conn, addr)
		
def connect_to_node(node):
    global known_nodes
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host, port = node.split(':')
    client.connect((host, int(port)))
    data = json.dumps(known_nodes).encode(FORMAT)
    client.send(data)

server_thread = threading.Thread(target = start_server)
server_thread.start()

# time.sleep(1)

# connect_to_node('localhost:5000')
for node in known_nodes:
	connect_to_node(node)