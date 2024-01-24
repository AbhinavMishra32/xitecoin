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
    try:
        for client in clients:
            client.send(message)
        print("Message sent to all clients")
    except Exception as e:
        print(f"Error occurred while broadcasting: {e}")

def handle(client: socket.socket):
    while True:
        try:
            data = client.recv(2024).decode()
            data_recvd = json.loads(data)
            print(data_recvd)
            sent_data = json.dumps(data_recvd)
            handle_choice(client, data_recvd)
            broadcast(sent_data.encode())
        except:
            if client.fileno() == -1:
                # The client's socket has been closed
                index = clients.index(client)
                clients.remove(client)
                nickname = nicknames[index]
                broadcast(f"{client} left the network".encode())
                nicknames.remove(nickname)
                break
            else:
                # An exception occurred, but the client's socket is still open
                # Continue to the next iteration of the loop to try to receive more data
                continue

def handle_choice(client: socket.socket, json):
    try:
        # choice = client.recv(1024).decode()
        if json["action"] == "SEND_BC":
            client.send(json.dumps("Ok, send the blockchain").encode())
        if json["action"] == "MESSAGE":
            return "MSG_MODE"
        if json["action"] == "BC_TRANSACTION_DATA":
            print(json["data"])
        
    except:
        index = clients.index(client)
        clients.remove(client)
        client.close()
        nickname = nicknames[index]
        broadcast(f"{nickname} left the network".encode())
        nicknames.remove(nickname)

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
    try:
        while True:
            client, address = server.accept()
            data = client.recv(10024).decode()
            data_recvd = json.loads(data)
            nickname = data_recvd["sender"]
            print(data_recvd)
            nicknames.append(nickname)
            print(f"Connected with {str(address)}")
            try:
                clients.append(client)
                print(f"{nickname} added to clients list")
            except Exception as e:
                print(f"Error occured while appending client to clients list: {e}")
            client.send("Connected to the server".encode())
            thread = threading.Thread(target = handle, args = (client,))
            thread.start()
    except Exception as e:
        print(f"Error occurred: {e}")
        server.close()

if __name__ == "__main__":
    print("Server started...")
    recieve()