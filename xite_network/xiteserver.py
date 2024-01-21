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

actions = "HELLO", "GOODBYE", "MESSAGE"

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} left the network".encode())
            nicknames.remove(nickname)
            break

def handle_choice(client: socket.socket, choice: str):
    while True:
        try:
            # choice = client.recv(1024).decode()
            if choice == "SEND_BC":
                client.send("Ok, send the blockchain".encode())
            if choice == "MESSAGE":
                return "MSG_MODE"
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f"{nickname} left the network".encode())
            nicknames.remove(nickname)
            break



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
        data_recvd = json.loads(client.recv(2024).decode())
        nickname  = data_recvd["sender"]
        print(data_recvd)
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of client is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode())
        client.send("Connected to the server".encode())

        choice = json.loads(client.recv(1024).decode())["action"]
        # handle_choice(client, choice)
        
        print(data_recvd)
        print(choice)
        print("hello")
        thread = threading.Thread(target = handle, args = (client,))
        thread.start()

if __name__ == "__main__":
    print("Server started...")
    recieve()