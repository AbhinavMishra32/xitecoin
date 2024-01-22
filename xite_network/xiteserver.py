import socket
import threading
import json

HOST = "localhost"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client: socket.socket):
    while True:
        try:
            data_recvd = json.loads(client.recv(2024).decode())
            print(data_recvd)
            json.dumps(data_recvd)
            # handle_choice(client, data_recvd["action"])
            # message = client.recv(1024)
            broadcast(data_recvd.encode())
        except:
            if client.fileno() == -1:
                # The client's socket has been closed
                # index = clients.index(client)
                clients.remove(client)
                # nickname = nicknames[index]
                broadcast(f"{client} left the network".encode())
                # nicknames.remove(nickname)
                break
            else:
                # An exception occurred, but the client's socket is still open
                # Continue to the next iteration of the loop to try to receive more data
                continue

def handle_choice(client: socket.socket, choice: str):
    try:
        # choice = client.recv(1024).decode()
        if choice == "SEND_BC":
            client.send("Ok, send the blockchain".encode())
        if choice == "MESSAGE":
            return "MSG_MODE"
    except:
        # index = clients.index(client)
        clients.remove(client)
        client.close()
        # nickname = nicknames[index]
        broadcast(f"{client} left the network".encode())
        # nicknames.remove(nickname)

def recieve_old():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send("NICK".encode())
        nickname  = client.recv(1024).decode()
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of client is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode())
        client.send("Connected to the server".encode())

        thread = threading.Thread(target = handle, args = (client,))
        thread.start()

def recieve():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        thread = threading.Thread(target = handle, args = (client,))
        thread.start()
        # data_recvd = json.loads(client.recv(2024).decode())
        # nickname  = data_recvd["sender"]
        # print(data_recvd)
        # nicknames.append(nickname)
        try:
            clients.append(client)
            print(f"Client {client} added to clients list")
        except Exception as e:
            print(f"Error occured while appending client to clients list: {e}")

        # print(f"Nickname of client is {nickname}")
        # broadcast(f"{nickname} joined the chat!".encode())
        client.send("Connected to the server".encode())

        # choice = json.loads(client.recv(1024).decode())["action"]
        # handle_choice(client, choice)
        
        # print(data_recvd)=
        # print(choice)
        # print("hello")


if __name__ == "__main__":
    print("Server started...")
    recieve()