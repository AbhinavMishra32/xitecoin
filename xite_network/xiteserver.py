import socket
import threading
import json
from termcolor import colored

HOST = "localhost"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    try:
        for client_socket in clients:
            client_socket.send(message)
            print(f"Message sent to {nicknames[clients.index(client_socket)]}")
    except Exception as e:
        print(f"Error occurred while broadcasting: {e}")
        

def handle(client: socket.socket):
    while True:
        try:
            data = client.recv(2024).decode()
            data_recvd = json.loads(data)
            handle_choice(client, data_recvd)
            # sent_data = json.dumps(data_recvd)
            # broadcast(data_recvd.encode())
        except:
            if client.fileno() == -1:
                # The client's socket has been closed
                # index = clients.index(client)
                # clients.remove(client)
                # nickname = nicknames[index]
                # broadcast(f"{client} left the network".encode())
                # nicknames.remove(nickname)
                break
            else:
                # An exception occurred, but the client's socket is still open
                # Continue to the next iteration of the loop to try to receive more data
                continue

def handle_choice(client: socket.socket, data):
    try:
        print(colored(f"[CLIENT]: {data}", 'cyan'))
        print(colored(f"ACTION: {data['action']}", 'yellow','on_black', ['bold']))
        actions = ['SENDER_NAME', 'SEND_BC', 'BC_TRANSACTION_DATA']
        if data["action"] == "SENDER_NAME":
            nickname = data["sender"]
            if nickname in nicknames:
                clients.remove(client)
            else:
                nicknames.append(nickname)
                print(f"{nickname} added to clients list")
            clients.append(client)

            print(colored(f"NICKNAMES: {nicknames}", 'yellow'))
            try:
                pass
            except Exception as e:
                print(f"Error occured while appending client to clients list: {e}")
        client.send(json.dumps({"[Message from Server] Connected to the server"}).encode())
        
        if data["action"] == "SEND_BC":
            client.send(data.dumps({"Ok, send the blockchain"}).encode())
            return "MSG_MODE"
        if data["action"] == "BC_TRANSACTION_DATA":
            print(" action: BC_TRANSACTION_DATA-------")
            print(data["data"])
            print("broadcasting the json")
            broadcast(json.dumps(data).encode())
        if data["action"] not in actions:
            print(colored("No valid action specified, so here is the original json:", 'light_red'))
            print(colored(data, 'light_red'))
            print("broadcasting the json")
            broadcast(json.dumps(data).encode())
    except Exception as e:
        print(colored(f"Error occurred while handling action: {e}", 'red'))
        print(colored(data, 'red'))
        # pass
        # index = clients.index(client)
        # clients.remove(client)
        # client.close()
        # nickname = nicknames[index]
        # broadcast(f"{nickname} left the network".encode())
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
    try:
        while True:
            client, address = server.accept()
            if client not in clients:
                thread = threading.Thread(target = handle, args = (client,))
                thread.start()
                print("handle thread started")
            # data = client.recv(10024).decode()
            # if data:  # Add this line 
                # print(f"Connected with {str(address)}")
                # print("starting handle thread")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    print("Server started...")
    recieve()