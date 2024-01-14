"""
Bootstrap server keeps record of active/known peers and connect them to the network, after that it allows transfer of data from one peer to another

task 1: make a known peer list then when a peer connect, send that list to that peer.
task 2: make that peer broadcast stuff to other connected peers.

"""

import socket
import json
import threading

# HOST = "192.168.29.241"
HOST = socket.gethostbyname("hpLaptop.local")
# HOST = "localhost"
PORT = 12345

class BServer():
	def __init__(self, host, port):
		self.active_peers = []
		self.host = host
		self.port = port

	def broadcast(self, message):
		for client in self.active_peers:
			client.sendall(message.encode())

	def handle_user_commands(self, client, address):
		msg = client.recv(1024).decode('utf-8')
		print(msg)
		match msg:
			case "CLOSE":
				print(f"Connection closed by: {address}")
				for _ in self.active_peers:
					if _["ip"] == address[0]:
						self.active_peers.remove(address)
				client.close()
			case _:
				return msg

	def handle_client(self, client: socket.socket, address):
		try:	
			print(f"Handling client: {address}")
			while True:
				client.send(json.dumps(self.active_peers).encode())
				self.handle_user_commands(client, address)
				data = json.loads(client.recv(1024))
				print(f"Recieved data from {address}: {data}")
		except Exception as e:
			print(f"Error occured (From handle_client): {e}")

	def start(self):
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.server.bind((self.host, self.port))
			self.server.listen()
			print(f"Server started on {self.host}:{self.port}")
			while True:
				client, address = self.server.accept()
				new_client = {"ip": address[0], "port": address[1]}
				# print(self.active_peers)
				if new_client["ip"] not in [x["ip"] for x in self.active_peers]:
					self.active_peers.append(new_client)
				else:
					for _ in self.active_peers:
						if _["ip"] == new_client["ip"]:
							_["port"] = new_client["port"]
				print(f"Connected with {address}")
				client_thread = threading.Thread(target=self.handle_client, args=(client, address))
				client_thread.start()
		except Exception as e:
			print(f"Error occured: {e}")

xite_bserv = BServer(HOST, PORT)
xite_bserv.start()