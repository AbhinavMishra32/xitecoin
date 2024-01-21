import socket
import threading
from xitelib.node import Blockchain
from .xiteuser import XiteUser
import sys
import json

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 12345))

def recieve():
    while True:
        try:
            message = client.recv(1024).decode()
            print(message)
            # if message == "NICK":
            #     client.send(nickname.encode())
            # else:
            #     print(message)
        except Exception as e:
            print(f"Error occurred: {e}")
            break

def compare_length():
    pass

def cl_handle_choice(client: socket.socket, choice: str):
    try:
        if choice == "SEND_BC":
            client.send("Ok, send the blockchain".encode())
        if choice == "MESSAGE":
            return "MSG_MODE"
    except Exception as e:
        print(f"Error occurred: {e}")

def write():
    while True:
        choice: str = input("Choose an action: ")
        message: str = input("Enter your message: ")
        data: str = input("Enter array: ")
        
        # data = [block.to_dict() for block in client_user.blockchain.chain]
        json_test = json.dumps({"message": message, "sender": client_user.username, "data": data.split()})
        print(json_test)
        # json_test = json.dumps({"message": "Im sending teh blockchain mf", "sender": client_user.username, "data": "HERE COMES THE BC DATA"})
        send_message(choice, json_test)
        print("Sent message!")
        # send_message("MESSAGE", input(""))
        # message = f"{nickname}: {input('')}"
        # message = choice
        # client.send(message.encode())

def send_message(action: str, message: str):
    message = json.loads(message)
    msg_json = json.dumps({"action": action, "message": message["message"], "sender": client_user.username, "data": message["data"]}) #type: ignore
    client.send(msg_json.encode())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 xiteclient.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]

    tb = Blockchain("tb")
    client_user = XiteUser(username, password, tb)

    recieve_thread = threading.Thread(target = recieve)
    recieve_thread.start()

    write_thread = threading.Thread(target = write)
    write_thread.start()