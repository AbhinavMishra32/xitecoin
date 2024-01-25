import socket
import threading
from xitelib.node import Blockchain, User
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
                cl_handle_json(client, cl_data_recvd["action"])
            else:
                print("No data received")
        except Exception as e:
            print(f"Error occurred: {e}")
            break

def compare_length():
    pass

def cl_handle_json(client, json):
    try:
        if json["sender"] not in nicknames:
                nicknames.append(json["sender"])
                #dbug
                print(f"New user connected: {json['sender']}")
        if json["action"] == "SEND_BC":
            print("Sending whole blockchain")
            send_whole_blockchain(client)
        if json["action"] == "BC_TRANSACTION_DATA":
            print("Got transaction data, here it is: \n" + json["data"])
    except Exception as e:
        print(f"Error occurred while handling json: {e}")

def make_json(data, sender: str = "Default sender", action: str = "Default action") -> str:
    return json.dumps({"action": action, "sender": sender, "data": data, "bc_name": client_user.blockchain.name})
        
#TODO: get a hashed block (meaning it is already mined) in one thread, and hash incoming non-hashed blocks and broadcast them in another thread

def send_whole_blockchain(client):
    with open(client_user.blockchain.file_path, 'r') as f:
        blockchain = json.load(f)
        client.send(make_json(blockchain, "SEND_BC", client_user.username).encode())

def make_block():
    pass

def mine_block():
    pass

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
        payment: str = input("Enter payment: ")
        recipient = payment.split(' ')[0]
        amount = int(payment.split(' ')[1])
        recp_user = User(recipient,client_user.blockchain)
        client_user.nwtransaction(recp_user, amount)

        send_data = make_json(data = client_user.nwtransaction(recp_user, amount, save = False), action = "BC_TRANSACTION_DATA", sender = client_user.username)
        print(send_data)
        client.send(send_data.encode())
        # if client_user.user_exists(recipient):
        #     print("User exists")
        #     recp_user = User(recipient,client_user.blockchain)
        #     client_user.nwtransaction(recp_user, amount)
        # else:
        #     print("User doesn't exist")
        #     print("Making new user to put in blockchain")
        #     recp_user = User(recipient,client_user.blockchain)
        #     client_user.nwtransaction(recp_user, amount)
        #     continue
        
        # data = [block.to_dict() for block in client_user.blockchain.chain]
        # json_test = json.dumps({"message": message, "sender": client_user.username, "data": data.split()})
        # print(json_test)
        # send_message(choice, json_test)
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
                cl_handle_json(client, data_json)
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
    tb.load_blockchain()
    tb.verify_blockchain()

    # tb.create_genesis_block()
    client_user = XiteUser(username, password, tb)

    recieve_thread = threading.Thread(target = recv_msg)
    recieve_thread.start()
    
    # if client_user.username == "Abhinav1":
    #     send_message("my action",json.dumps({"testing":"tested"}))
    #     sdata = make_json(data = client_user.nwtransaction(client_user, 0, save = False), action = "BC_TRANSACTION_DATA", sender = client_user.username)
    #     print(sdata)
    #     client.send(sdata.encode())
    #     print("Sent transaction data")
    # else:
    #     print("Not Abhinav1 so not sending transaction data, only recieving")
    #     send_message("my action",json.dumps({"testing":"tested"}))
    # tb.save_blockchain()


    write_thread = threading.Thread(target = write)
    write_thread.start()
