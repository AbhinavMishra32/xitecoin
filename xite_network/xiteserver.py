import socket
import threading
import json
import traceback
from termcolor import colored
from util.debug import debug_log
import sys


HOST = "localhost"
PORT = 50000

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
            debug_log(colored(f"Message sent to {nicknames[client_socket]}", 'green'))
        return message.decode()
    except Exception as e:
        debug_log(f"Error occurred while broadcasting: {e}")


def safe_print(text):
    try:
        # Try printing normally
        print(text)
    except UnicodeEncodeError:
        # If printing fails due to encoding issues, encode to 'utf-8' and decode to 'cp1252'
        encoded_text = text.encode('utf-8', errors='replace').decode('cp1252', errors='replace')
        # Print the encoded text
        sys.stdout.buffer.write(encoded_text.encode(sys.stdout.encoding, errors='replace'))
        # Print a warning
        print("\nWarning: Some characters could not be properly encoded and were replaced.")

        

def handle(client: socket.socket):
    buffer = ""
    while True:
        try:
            data = client.recv(2024).decode()
            buffer += data
            while True:
                try:
                    # Try to decode a JSON object from the start of the buffer
                    data_recvd, index = json.JSONDecoder().raw_decode(buffer)
                    handle_choice(client, data_recvd)
                    # Remove the processed JSON object from the buffer
                    buffer = buffer[index:].lstrip()
                except ValueError:
                    # No more complete JSON objects in the buffer
                    break
        except json.JSONDecodeError as e:
            debug_log(colored(f"Error occurred while decoding json: {e}", 'red', attrs=['bold']))
        except Exception as e:
            debug_log(f"Error occurred in : \033[1;32;40m handle \033[m {e}")
            debug_log(data)
            traceback.print_exc()
            if client.fileno() == -1:
                break
            else:
                # An exception occurred, but the client's socket is still open
                # Continue to the next iteration of the loop to try to receive more data
                continue

def get_latest_bc_dict(c_len_dict: dict) -> tuple:
    max_name = max(c_len_dict, key=c_len_dict.get) # type: ignore
    max_len = c_len_dict[max_name]
    return max_len, max_name

def handle_choice(client: socket.socket, data):
    try:
        debug_log(colored(f"[CLIENT]: {data}", 'cyan'))
        debug_log(colored(f"ACTION: {data['action']}", 'yellow','on_black', ['bold']))
        actions = ['SENDER_NAME', 'SEND_BC', 'BC_TRANSACTION_DATA', 'SYNC_BC', 'CHECK_BC_LEN', 'WANT_BC', 'GIVE_BC']

        # if data["action"] != "SENDER_NAME":
        #     # c_lens.append(int(data["data"]["data"]["chain_length"]))
        #     ch_len_dict[data["sender"]] = data["data"]["data"]["chain_length"]
        #     print(data["sender"],data["data"]["data"]["chain_length"])
        try:
            if data["action"] == "SENDER_NAME":
                ch_len_dict[data["sender"]] = data["chain_length"]
                # print(data["sender"],data["data"]["data"]["chain_length"])
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
                debug_log(f"{nickname} added to clients list")

                clients.append(client)
                nickname_list= []
                for _ in nicknames:
                    nickname_list.append(nicknames[_])
                debug_log(colored(f"NICKNAMES: {nickname_list}", 'yellow'))  # Moved inside the else block
                debug_log(colored(f"NO. OF CLIENTS: {len(clients)}", 'yellow'))
        except Exception as e:
            debug_log(f"Error occurred while appending client to clients list: {type(e).__name__}, {e.args}")
        client.send(json.dumps({"[Message from Server] Connected to the server": ""}).encode())
        if data["action"] == "SEND_BC":
            client.send(json.dumps({"Ok, send the blockchain" : ""}).encode())
            if data["reciever"]:
                debug_log(f"SEND_BC reciver: {data['reciever']}")
            else:
                debug_log("SEND_BC reciever: None")
            return "MSG_MODE"
        if data["action"] == "BC_TRANSACTION_DATA":
            ch_len_dict[data["sender"]] = data["data"]["data"]["chain_length"]
            debug_log(f"CHAIN DICT: {ch_len_dict}")
            debug_log("broadcasting the json, action: BC_TRANSACTION_DATA :-")
            broadcast(json.dumps(data).encode())
        if data["action"] == "SYNC_BC":
            debug_log("broadcasting json for synchronizing blockchain")
            broadcast(json.dumps(data).encode())

        if data["action"] == "CHECK_BC_LEN":
            debug_log("in CHECK_BC_LEN action")
            debug_log("Checking blockchain length")
            debug_log(f"MAX CHAIN LENGTH: {max(ch_len_dict.values())}")
            max_len, max_name = get_latest_bc_dict(ch_len_dict)
            debug_log(f"CHAIN LENGTH DICT: {ch_len_dict}")
            debug_log(f"MAX LENGTH: {max_len}, MAX NAME: {max_name}")
            debug_log("broadcasting the json from CHECK_BC_LEN action...")
            sender_client: socket.socket = next((c for c in clients if nicknames[c] == data["sender"]), None) #type: ignore
            sender_client.send(json.dumps({"action": "C_LEN_BROADCAST", "data": {"chain_length": max_len, "reciever": data["sender"], "lgt_c_name": max_name}}).encode())
            # now broadcasting to the client having the max length to give their chain
            # broadcast(json.dumps({"action": "SEND_BC", "sender": max_name, "reciever": data["sender"]}).encode()) # reciever is the person who requested the chain, sender is the client with max chain length

        if data["action"] == "C_LEN_BROADCAST":
            # print("broadcasting the json")
            # broadcast(json.dumps(data).encode())
            pass

        if data["action"] == "WANT_BC":
            debug_log("broadcasting the json from WANT_BC action...")
            broadcast(json.dumps(data).encode())
        
        if data["action"] == "GIVE_BC":
            debug_log("broadcasting the json")
            broadcast(json.dumps(data).encode())

        if data["action"] == "MINE_STATUS":
           pass 

        if data["action"] not in actions:
            debug_log(colored("No valid action specified, so here is the original json:", 'light_red'))
            debug_log(colored(data, 'light_red'))
            debug_log("broadcasting the json, action: None")
            broadcast(json.dumps(data).encode())
    
    except BrokenPipeError as e:
        debug_log(colored(f"BrokenPipeError: {e}", 'red', attrs=['bold']))
        if client in clients:
            clients.remove(client)
            nickname = nicknames.pop(client, None)
            if nickname:
                broadcast(f"{nickname} left the network".encode())
                client.close()
    except Exception as e:
        debug_log(colored(f"Error occurred while handling action, so not broadcasting: {e}", 'red', attrs=['bold']))
        debug_log("Faulty action:" + colored(data, 'red'))
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
                debug_log(colored(f"Handle thread started", attrs=['bold']))
            # data = client.recv(10024).decode()
            # if data:  # Add this line     
                # print(f"Connected with {str(address)}")
                # print("starting handle thread")
    except Exception as e:
        debug_log(f"Error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print(colored('''
                  
▀▄▀ █ ▀█▀ █▀▀ █▀▀ █▀█ █ █▄░█
█░█ █ ░█░ ██▄ █▄▄ █▄█ █ █░▀█
''', 'cyan'))
    print(colored("Xitecoin server started...", 'green'))
    recieve()