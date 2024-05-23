import threading
import json
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from termcolor import colored
from util.debug import debug_log

HOST = "localhost"
PORT = 8003

clients = []
nicknames = {}

ch_len_dict = {}

def broadcast(message):
    try:
        for client_socket in clients:
            client_socket.sendall(message)
            print(colored(f"Message sent to {nicknames[client_socket]}", 'green'))
        return message.decode()
    except Exception as e:
        print(f"Error occurred while broadcasting: {e}")

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()
        
        try:
            data = json.loads(post_data)
            self.handle_choice(data)
        except json.JSONDecodeError as e:
            print(colored(f"Error occurred while decoding json: {e}", 'red', attrs=['bold']))
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            print(f"Error occurred in handle: {e}")
            traceback.print_exc()
            self.send_error(500, "Internal Server Error")
    
    def handle_choice(self, data):
        try:
            print(colored(f"[CLIENT]: {data}", 'cyan'))
            print(colored(f"ACTION: {data['action']}", 'yellow', 'on_black', ['bold']))
            actions = ['SENDER_NAME', 'SEND_BC', 'BC_TRANSACTION_DATA', 'SYNC_BC', 'CHECK_BC_LEN', 'WANT_BC', 'GIVE_BC']

            if data["action"] == "SENDER_NAME":
                ch_len_dict[data["sender"]] = data["chain_length"]
                nickname = data["sender"]
                if nickname in nicknames.values():
                    old_client = next((c for c in clients if nicknames[c] == nickname), None)
                    if old_client:
                        clients.remove(old_client)
                        del nicknames[old_client]
                nicknames[self.client_address] = nickname
                print(f"{nickname} added to clients list")
                clients.append(self.client_address)
                nickname_list = [nicknames[_] for _ in nicknames]
                print(colored(f"NICKNAMES: {nickname_list}", 'yellow'))
                print(colored(f"NO. OF CLIENTS: {len(clients)}", 'yellow'))
                self._set_headers()
                self.wfile.write(json.dumps({"[Message from Server] Connected to the server": ""}).encode())

            if data["action"] == "SEND_BC":
                self._set_headers()
                self.wfile.write(json.dumps({"Ok, send the blockchain": ""}).encode())
                debug_log(f"SEND_BC reciver: {data.get('reciever')}")
                return "MSG_MODE"

            if data["action"] == "BC_TRANSACTION_DATA":
                ch_len_dict[data["sender"]] = data["data"]["data"]["chain_length"]
                debug_log(f"CHAIN DICT: {ch_len_dict}")
                print("broadcasting the json, action: BC_TRANSACTION_DATA :-")
                broadcast(json.dumps(data).encode())

            if data["action"] == "SYNC_BC":
                print("broadcasting json for synchronizing blockchain")
                broadcast(json.dumps(data).encode())

            if data["action"] == "CHECK_BC_LEN":
                debug_log("in CHECK_BC_LEN action")
                print("Checking blockchain length")
                max_len, max_name = get_latest_bc_dict(ch_len_dict)
                sender_client = next((c for c in clients if nicknames[c] == data["sender"]), None)
                if sender_client:
                    self._set_headers()
                    self.wfile.write(json.dumps({
                        "action": "C_LEN_BROADCAST",
                        "data": {"chain_length": max_len, "reciever": data["sender"], "lgt_c_name": max_name}
                    }).encode())

            if data["action"] in ["WANT_BC", "GIVE_BC"]:
                print(f"broadcasting the json from {data['action']} action...")
                broadcast(json.dumps(data).encode())

            if data["action"] not in actions:
                print(colored("No valid action specified, so here is the original json:", 'light_red'))
                print(colored(data, 'light_red'))
                debug_log("broadcasting the json, action: None")
                broadcast(json.dumps(data).encode())

        except Exception as e:
            print(colored(f"Error occurred while handling action, so not broadcasting: {e}", 'red', attrs=['bold']))
            print("Faulty action:", colored(data, 'red'))
            traceback.print_exc()

def get_latest_bc_dict(c_len_dict: dict) -> tuple:
    max_name = max(c_len_dict, key=c_len_dict.get)
    max_len = c_len_dict[max_name]
    return max_len, max_name

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8003):
    server_address = (HOST, port)
    httpd = server_class(server_address, handler_class)
    print(colored('''
                  
▀▄▀ █ ▀█▀ █▀▀ █▀▀ █▀█ █ █▄░█
█░█ █ ░█░ ██▄ █▄▄ █▄█ █ █░▀█
''', 'cyan'))
    print(colored("Xitecoin server started...", 'green'))
    httpd.serve_forever()

if __name__ == "__main__":
    run()
