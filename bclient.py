import socket
import json
import threading

# HOST = "192.168.29.241" #this is the bootstrap server's ip
# HOST = socket.gethostbyname(socket.gethostname())
HOST = "hpLaptop.local"
PORT = 12345
ADDR = (HOST, PORT)

class BClient():
	def __init__(self):
		try:
			self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.client.connect(ADDR)
		except Exception as e:
			print(f"Error occured: {e}")

	def send_data(self):
		data = json.dumps({"test": "message"}).encode()
		self.client.send(data)
		pass

	def disc_bserv(self):
		self.client.send("CLOSE".encode())
		pass
	
	def recieve_msg(self):
		self.active_clients = json.loads(self.client.recv(1024).decode('utf-8'))
		print(f"Data received from server: {self.active_clients}")


	def connect_to_peers(self):
		for peer in self.active_clients:
			try:
				ip = peer.get('ip')
				port = peer.get('port')
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((ip, port))
				print(f"Connected to {ip}:{port}")
			except Exception as e:
				# print(f"Error while connecting to {ip}:{port}")
				print(f"Error while connecting to peers: {e}")


if __name__ == "__main__":
	peer = BClient()
	peer.recieve_msg()
	# peer.connect_to_peers()
	# peer.disc_bserv()
	# peer.recieve_msg()
