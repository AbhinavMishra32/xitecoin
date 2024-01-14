import socket
import json
import threading

# HOST = "192.168.29.241" #this is the bootstrap server's ip
HOST_BS = socket.gethostbyname("hpLaptop.local")
HOST_CL = socket.gethostbyname(socket.gethostname())
PORT = 12345
ADDR = (HOST_BS, PORT)

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

	def start_server(self):
		def handle_client(conn, addr):
			if addr == HOST_CL:
				return
			print(f"Connected by {addr}")
			while True:
				data = conn.recv(1024)
				if not data:
					break
				conn.sendall(data)
				conn.close()

		def server_thread():
			server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server.bind((HOST_CL, PORT))
			server.listen()
			print(f"Server started on {HOST_CL}:{PORT}")
			while True:
				conn, addr = server.accept()
				threading.Thread(target=handle_client, args = (conn, addr)).start()
		threading.Thread(target = server_thread).start()

	def connect_to_peers(self):
		for peer in self.active_clients:
			try:
				ip = peer.get('ip')
				if ip == HOST_BS:
					continue
				# port = peer.get('port')
				port = 12345
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((ip, port))
				print(f"Connected to {ip}:{port}")
			except Exception as e:
				# print(f"Error while connecting to {ip}:{port}")
				print(f"Error while connecting to peers: {e}")


if __name__ == "__main__":
	peer = BClient()
	peer.start_server()
	peer.recieve_msg()
	peer.connect_to_peers()
	# peer.disc_bserv()
	# peer.recieve_msg()
