"""
Bootstrap server keeps record of active/known peers and connect them to the network, after that it allows transfer of data from one peer to another

task 1: make a known peer list then when a peer connect, send that list to that peer.
task 2: make that peer broadcast stuff to other connected peers.

"""

import socket
import json
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 12345

class BServer():
	def __init__(self, host, port):
		self.active_peers = []
		self.host = host
		self.port = port

	def handle_client(self, client, address):
		print(f"Handling client: {address}")
		while True:
			data = client.recv(1024)
			if not data:
				print(f"Connection closed by: {address}")
				self.active_peers.remove(address)
				client.close()
				break
			print(f"Recieved data from {address}: {data.decode()}")

	def start(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.bind((self.host, self.port))
		server.listen()
		print(f"Server started on {HOST}:{PORT}")
		while True:
			client, address = server.accept()
			print(f"Connected with {address}")
			self.active_peers.append(address)
			client_thread = threading.Thread(target = self.handle_client, args = (client, address))
			client_thread.start()

xite_bserv = BServer(HOST, PORT)
xite_bserv.start()