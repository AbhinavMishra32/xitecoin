import socket
import threading
from xitelib.node import Blockchain
from .xiteuser import XiteUser
import sys
import json

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 12345))

def recieve_dbug():
    while True:
        cl_data_recvd = {}
        try:
            data = client.recv(2024)
        except Exception as e:
            print(f"Error receiving data: {e}")
            # break

        try:
            decoded_data = data.decode()
        except Exception as e:
            print(f"Error decoding data: {e}")
            # break

        try:
            cl_data_recvd = json.loads(decoded_data)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            # break

        try:
            cl_handle_choice(cl_data_recvd["action"])
        except Exception as e:
            print(f"Error handling action: {e}")
            # break

def recieve():
    while True:
        try:
            data = client.recv(2024).decode()
            if data:  # Check if data is not empty
                cl_data_recvd = json.loads(data)
                print(cl_data_recvd)
                cl_handle_choice(cl_data_recvd["action"])
            else:
                print("No data received")
        except Exception as e:
            print(f"Error occurred: {e}")
            break

def compare_length():
    pass

def cl_handle_choice(choice: str):
    try:
        if choice == "SEND_BC":
            client.send(make_json("Ok, send the blockchain", client_user.username, "HERE COMES THE BC DATA").encode())
    except Exception as e:
        print(f"Error occurred: {e}")

def make_json(message: str, sender: str, data: str):
    return json.dumps({"message": message, "sender": sender, "data": data})

def send_msg():
    while True:
        try:
            message = input("Enter your message: ")
            client.send(json.dumps(message).encode())
            if message == "DISCONNECT":
                client.close()
                break
        except Exception as e:
            print(f"Error occurred: {e}")
            break

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

def recv_msg():
    while True:
        try:
            data = client.recv(2024).decode()
            if data:  # Check if data is not empty
                print(data)
            else:
                print("No data received")
        except Exception as e:
            print(f"Error occurred: {e}")
            break


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 xiteclient.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]

    tb = Blockchain("tb")
    tb.create_genesis_block()
    client_user = XiteUser(username, password, tb)

    recieve_thread = threading.Thread(target = recv_msg)
    recieve_thread.start()

    write_thread = threading.Thread(target = send_msg)
    write_thread.start()


#TODO: broadcasting is not working, fix it