# import socket


# HEADER = 64
# PORT = 5050
# FORMAT = "utf-8"
# DISCONNECT_MESSAGE = "!DISCONNECT"
# SERVER = socket.gethostbyname(socket.gethostname())
# ADDR = (SERVER, PORT)

# client = socket.socket(
#     socket.AF_INET, socket.SOCK_STREAM
# )  # AF_INET = IPv4, SOCK_STREAM = TCP
# client.connect(ADDR)


# def send(msg):
#     message = msg.encode(FORMAT)
#     msg_length = len(message)
#     send_length = str(msg_length).encode(FORMAT)
#     send_length += b" " * (HEADER - len(send_length))
#     client.send(send_length)
#     client.send(message)


# send("Hello World!")


# send(DISCONNECT_MESSAGE)

import socket

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))

input = input(str("Enter message: "))

socket.send("Hello World!".encode('utf-8'))
print(socket.recv(1024).decode('utf-8'))