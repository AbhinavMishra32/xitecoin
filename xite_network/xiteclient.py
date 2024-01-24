import socket
import threading
import asyncio
from xitelib.node import Blockchain
from .xiteuser import XiteUser
import sys
import json

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 12345))

nicknames = []
trans_buffer = []

def recieve_dbug():
    while True:
        cl_data_recvd = {}
        try:
            data = client.recv(2024)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

        try:
            decoded_data = data.decode()
        except Exception as e:
            print(f"Error decoding data: {e}")
            break

        try:
            cl_data_recvd = json.loads(decoded_data)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            break

        # try:
        #     cl_handle_json(cl_data_recvd["action"])
        # except Exception as e:
        #     print(f"Error handling action: {e}")
        #     break

def recieve():
    while True:
        try:
            data = client.recv(2024).decode()
            if data:  # Check if data is not empty
                cl_data_recvd = json.loads(data)
                print(cl_data_recvd)
                cl_handle_json(cl_data_recvd["action"])
            else:
                print("No data received")
        except Exception as e:
            print(f"Error occurred: {e}")
            break

def compare_length():
    pass

def cl_handle_json(json):
    try:
        if json["sender"] not in nicknames:
                nicknames.append(json["sender"])
        if json["action"] == "SEND_BC":
            client.send(make_json("Ok, send the blockchain", client_user.username, "HERE COMES THE BC DATA").encode())
        if json["action"] == "BC_TRANSACTION_DATA":
            print("Got transaction data, here it is: \n" + json["data"])
    except Exception as e:
        print(f"Error occurred while handling json: {e}")

def make_json(data, message: str = "Default message", sender: str = "Default sender"):
    return json.dumps({"message": message, "sender": sender, "data": data, "bc_name": client_user.blockchain.name})


#TODO: get a hashed block (meaning it is already mined) in one thread, and hash incoming non-hashed blocks and broadcast them in another thread


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
        client.send(json.dumps({"sender": client_user.username}).encode())
        choice: str = input("Choose an action: ")
        message: str = input("Enter your message: ")
        data: str = input("Enter array: ")
        # data = [block.to_dict() for block in client_user.blockchain.chain]
        json_test = json.dumps({"message": message, "sender": client_user.username, "data": data.split()})
        print(json_test)
        send_message(choice, json_test)
        print("Sent message!")

def send_message(action: str, message):
    message_dict = json.loads(message)
    msg_json = json.dumps({
        "action": action, 
        "message": message_dict.get("message", "No message"),  # Use a default value if "message" key is not present
        "sender": client_user.username, 
        "data": message_dict.get("data", {})  # Use a default value if "data" key is not present
    }) 
    print(msg_json)
    client.send(msg_json.encode())

def recv_msg():
    while True:
        try:
            data = client.recv(2024).decode()
            data_json = json.loads(data)
            
            if data:
                print(data_json)
                cl_handle_json(data_json)
            else:
                print("No data received")
        except Exception as e:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 xiteclient.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]

    tb = Blockchain("tb")
    tb.load_blockchain()
    tb.verify_blockchain()

    # tb.create_genesis_block()
    client_user = XiteUser(username, password, tb)
    if client_user.username == "Abhinav1":
        # sdata = send_message("BC_TRANSACTION_DATA",json.dumps(client_user.nwtransaction(client_user, 0, save = False)))
        # sdata = make_json(client_user.nwtransaction(client_user, 0, save = False), "BC_TRANSACTION_DATA", client_user.username)
        # print(sdata)
        # client.send(sdata.encode())
        send_message("BC_TRANSACTION_DATA", json.dumps(client_user.nwtransaction(client_user, 0, save = False)))
        client.send(json.dumps({"testing":"tested"}).encode())
        print("Sent transaction data")
    else:
        print("Not Abhinav1 so not sending transaction data, only recieving")
    # tb.save_blockchain()
    recieve_thread = threading.Thread(target = recv_msg)
    recieve_thread.start()

    # write_thread = threading.Thread(target = write)
    # write_thread.start()
