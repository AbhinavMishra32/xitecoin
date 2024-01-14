import socket
import json
import threading

# HOST_BS = "192.168.200.1" #this is the bootstrap server's ip
HOST_BS = socket.gethostbyname("Abhinavs-Macbook-Air.local")
# HOST_BS = "localhost"
# HOST_BS = socket.gethostbyname("HomeComputer.local")
HOST_CL = socket.gethostbyname(socket.gethostname())
PORT_BS = 12345
PORT_CL = 12346
ADDR = (HOST_BS, PORT_BS)

class BClient():
	def __init__(self):
		try:
			self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.client.connect(ADDR)
			print("Bootstrap server connected successfully.")
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
		# print("Starting client server")
		try:
			def handle_client(conn, addr):
				if addr[0] == HOST_CL:
					return
				print(f"Connected by {addr}")
				while True:
					data = conn.recv(1024)
					if not data:
						break
					conn.sendall(data)
					conn.close()
		except Exception as e:
			print(f"Error occured: {e}")

		def server_thread():
			try:
				server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				server.bind((HOST_CL, PORT_BS))
				server.listen()
				print(f"Server started on {HOST_CL}:{PORT_BS}")
				while True:
					conn, addr = server.accept()
					threading.Thread(target=handle_client, args = (conn, addr)).start()
			except Exception as e:
				print(f"Error occured: {e}")
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
	peer.recieve_msg()
