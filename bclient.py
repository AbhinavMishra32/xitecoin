import socket
import json
import threading

# HOST = "192.168.29.241" #this is the bootstrap server's ip
HOST = socket.gethostbyname(socket.gethostname())
PORT = 12345
ADDR = (HOST, PORT)

class BClient():
	def __init__(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.connect(ADDR)

	def send_data(self):
		data = json.dumps({"test": "message"}).encode()
		self.client.send(data)
		pass

	def disc_bserv(self):
		self.client.send("CLOSE".encode())
	
	def recieve_msg(self):
		self.active_clients = json.loads(self.client.recv(1024).decode('utf-8'))
		print(f"Data recieved from server: {self.active_clients}")

	def connect_to_peers(self):
		for peer in self.active_clients:
			ip, port = peer['ip'], peer['port']

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, port))

		

peer = BClient()
peer.send_data()
peer.recieve_msg()
peer.disc_bserv()