import socket
import threading
import json
import traceback
from annotated_types import MaxLen
from termcolor import colored
from util.debug import debug_log


HOST = "localhost"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = {}

ch_len_dict = {}

def broadcast(message):
    try:
        for client_socket in clients:
            client_socket.send(message)
            print(colored(f"Message sent to {nicknames[client_socket]}", 'green'))
    except Exception as e:
        print(f"Error occurred while broadcasting: {e}")
        

def handle(client: socket.socket):
    while True:
        try:
            data = client.recv(2024).decode()
            if not data.strip():
                break
            data_recvd = json.loads(data)
            handle_choice(client, data_recvd)
            # sent_data = json.dumps(data_recvd)
            # broadcast(data_recvd.encode())
        except Exception as e:
            print(f"Error occurred in : \033[1;32;40m handle \033[m {e}")
            if client.fileno() == -1:
                break
            else:
                # An exception occurred, but the client's socket is still open
                # Continue to the next iteration of the loop to try to receive more data
                continue

def get_latest_bc_dict(c_len_dict: dict) -> tuple:
    max_len = max(c_len_dict.values())
    max_name = c_len_dict[max_len]
    return max_len, max_name

def handle_choice(client: socket.socket, data):
    try:
        print(colored(f"[CLIENT]: {data}", 'cyan'))
        print(colored(f"ACTION: {data['action']}", 'yellow','on_black', ['bold']))
        actions = ['SENDER_NAME', 'SEND_BC', 'BC_TRANSACTION_DATA', 'SYNC_BC']

        if data["action"] != "SENDER_NAME":
            # c_lens.append(int(data["data"]["data"]["chain_length"]))
            ch_len_dict[data["sender"]] = data["data"]["data"]["chain_length"]
            print(data["sender"],data["data"]["data"]["chain_length"])
        try:
            if data["action"] == "SENDER_NAME":
                nickname = data["sender"]
                if nickname in nicknames.values():  # Check the values of the nicknames dictionary
                    # Find the old client with the same nickname
                    old_client = next((c for c in clients if c.getpeername() != client.getpeername() and nicknames[c] == nickname), None)
                    if old_client:
                        # Remove the old client
                        clients.remove(old_client)
                        del nicknames[old_client]
                # Add the new client, regardless of whether an old client was found
                nicknames[client] = nickname
                print(f"{nickname} added to clients list")

                clients.append(client)
                nickname_list= []
                for _ in nicknames:
                    nickname_list.append(nicknames[_])
                print(colored(f"NICKNAMES: {nickname_list}", 'yellow'))  # Moved inside the else block
                print(colored(f"NO. OF CLIENTS: {len(clients)}", 'yellow'))
        except Exception as e:
            print(f"Error occured while appending client to clients list: {type(e).__name__}, {e.args}")
        client.send(json.dumps({"[Message from Server] Connected to the server": ""}).encode())
        if data["action"] == "SEND_BC":
            client.send(json.dumps({"Ok, send the blockchain" : ""}).encode())
            if data["reciever"]:
                debug_log(f"SEND_BC reciver: {data['reciever']}")
            else:
                debug_log("SEND_BC reciever: None")
            return "MSG_MODE"
        if data["action"] == "BC_TRANSACTION_DATA":
            # print(" action: BC_TRANSACTION_DATA-------")
            # print(data["data"])
            print("broadcasting the json")
            broadcast(json.dumps(data).encode())
        if data["action"] == "SYNC_BC":
            print("broadcasting json for synchronizing blockchain")
            broadcast(json.dumps(data).encode())

        if data["action"] == "CHECK_BC_LEN":
            print("Checking blockchain length")
            print(f"CHAIN LENGTH: {ch_len_dict}")
            max_len, max_name = get_latest_bc_dict(ch_len_dict)
            print(f"MAX LENGTH: {max_len}, MAX NAME: {max_name}")
            client.send(json.dumps({"action": "C_LEN_BRODCAST", "data": {"chain_length": max_len, "reciever": data["sender"]}}).encode())
            print("broadcasting the json")
            broadcast(json.dumps(data).encode())
            #now broadcasting to the client having the max length to give their chain
            broadcast(json.dumps({"action": "SEND_BC", "sender": max_name, "reciever": data["sender"]}).encode()) #reciever is the person who requested the chain, sender is the client with max chain length

        if data["action"] == "C_LEN_BRODCAST":
            # print("broadcasting the json")
            # broadcast(json.dumps(data).encode())
            pass

        if data["action"] not in actions:
            print(colored("No valid action specified, so here is the original json:", 'light_red'))
            print(colored(data, 'light_red'))
            print("broadcasting the json")
            broadcast(json.dumps(data).encode())
    except Exception as e:
        print(colored(f"Error occurred while handling action, so not broadcasting: {e}", 'red', attrs=['bold']))
        print(colored(data, 'red'))
        traceback.print_exc()
        # index = clients.index(client)
        # clients.remove(client)
        # client.close()
        # nickname = nicknames[index]
        # broadcast(f"{nickname} left the network".encode())
        # nicknames.remove(nickname)
        

def recieve():
    try:
        while True:
            client, address = server.accept()
            if client not in clients:
                thread = threading.Thread(target = handle, args = (client,))
                thread.start()
                print(colored(f"Handle thread started", attrs=['bold']))
            # data = client.recv(10024).decode()
            # if data:  # Add this line     
                # print(f"Connected with {str(address)}")
                # print("starting handle thread")
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print(colored('''
                  
▀▄▀ █ ▀█▀ █▀▀ █▀▀ █▀█ █ █▄░█
█░█ █ ░█░ ██▄ █▄▄ █▄█ █ █░▀█
''', 'cyan'))
    print(colored("Xitecoin server started...", 'green'))
    recieve()