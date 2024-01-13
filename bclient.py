import socket
import json
import threading

HOST = socket.gethostbyname(socket.gethostname()) #this is the bootstrap server's ip
PORT = 12345
ADDR = ("HOST", PORT)

class BClient():
	def __init__(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.connect(ADDR)

	def send_data(self):
		# data = json.loads(json.dumps({"test": "message"}))
		# self.client.sendall()
		pass
	
	def recieve_msg(self):
		data = json.loads(self.client.recv(1024).decode('utf-8'))
		print(f"Data recieved from server: {data}")

peer = BClient()
peer.recieve_msg()