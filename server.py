# import socket
# import threading

# HEADER = 64
# PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
# ADDR = (SERVER, PORT)
# FORMAT = "utf-8"
# DISCONNECT_MESSAGE = "!DISCONNECT"

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind(ADDR)


# def handle_client(conn, addr):
#     print(f"[NEW CONNECTION] {addr} connected.")
#     connected = True
#     while connected:
#         msg_length = conn.recv(HEADER).decode(FORMAT)
#         if msg_length:
#             msg_length = int(msg_length)
#             msg = conn.recv(msg_length).decode(FORMAT)
#             if msg == DISCONNECT_MESSAGE:
#                 conncted = False

#             print(f"[{addr}] {msg}")
#     conn.close()


# def start():
#     server.listen()
#     print(f"[LISTENING] Server is listening on {SERVER}")
#     while True:
#         conn, addr = server.accept()
#         thread = threading.Thread(target=handle_client, args=(conn, addr))
#         thread.start()
#         print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


# print("[STARTING] server is starting...")
# start()
import socket
import json

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen(5)

while True:
    communication_socket, address = server.accept()
    print(f"Connected to: {address}")
    while True:
        # message = communication_socket.recv(1024).decode('utf-8')
        # json_file =json.loads(communication_socket.recv(1024).decode('utf-8'))
        data = communication_socket.recv(1024).decode('utf-8')
        if data:
            try:
                json_file = json.loads(data)
                print(f"JSON RECEIVED: {json_file}")
            except json.JSONDecodeError:
                print(f"Message from client is: {data}")
        else:
            print("No data received")
        # if message == "STOP":
        #     communication_socket.close()
        #     print(f"Connection with {address} ended!")
        # print(f"Message from client is: {message}")
        communication_socket.send(f"Got you message! Thank you!".encode('utf-8'))

