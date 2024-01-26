from re import T
import socket
import threading
from xitelib.node import Blockchain, InvalidTransactionException, User, Block, Data
from xite_network.xiteuser import XiteUser, add_block_to_buffer, make_node_block
import sys
import json
from termcolor import colored

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 12345))

nicknames = []
TRANSACTION_BUFFER = []

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

def cl_handle_json(client, data: dict):
    # print("in cl_handle_json: ")
    try:
        sender = data.get("sender")
        if sender:
            if sender not in nicknames:
                nicknames.append(sender)
                print("Nicknames stored:")
                print(nicknames)
                print(f"New user connected: {sender}")
        else:
            print(colored("No sender specified", 'light_red'))

        action = data.get("action")
        if action == "SEND_BC":
            print("Sending whole blockchain")
            send_whole_blockchain(client)
        elif action == "BC_TRANSACTION_DATA":
            # print("Got transaction data, here it is: \n" + json.dumps(data.get("data", "")))
            # sender_user = User(data["sender"], client_user.blockchain)
            # recp_user = User(data["data"]["data"]["recipient_name"], client_user.blockchain)
            # node_data = Data(sender_user, recp_user, int(data["data"]["data"]["amount"]), data["data"]["data"]["message"], timestamp = data["data"]["timestamp"])
            # node_block = Block(node_data)
            # XiteUser.save_block(client_user, node_block)
            # print("Block saved successfully, but not mined yet \n THEREFORE VERIFYING INCORRECTLY:")
            # Blockchain.verify_single_block(client_user.blockchain, node_block)
            add_block_to_buffer(TRANSACTION_BUFFER, make_node_block(data, client_user))
            print("Transaction buffer:")
            # print(colored(len(TRANSACTION_BUFFER), 'green'))
            for _ in TRANSACTION_BUFFER:
                print("----Transaction Data----")
                print_transaction_data(data)
                print("--------------------")
            print(colored(f"BUFFER SIZE: {len(TRANSACTION_BUFFER)}", attrs=['bold']))
            # XiteUser.mine_block(data, client_user)

        else:
            print(colored("No action specified", 'light_red'))
            print(colored(data, 'light_grey'))
    except Exception as e:
        print(colored(f"Error occurred while handling json: {e}", attrs=['bold'], color='light_red'))
        print(colored(data, 'red'))

def make_json(data, sender: str = "Default sender", action: str = "Default action") -> str:
    if isinstance(data, set):
        data = list(data)
    return json.dumps({"action": action, "sender": sender, "data": data, "bc_name": client_user.blockchain.name})
        
#TODO: get a hashed block (meaning it is already mined) in one thread, and hash incoming non-hashed blocks and broadcast them in another thread

def send_whole_blockchain(client):
    with open(client_user.blockchain.file_path, 'r') as f:
        blockchain = json.load(f)
        client.send(make_json(blockchain, "SEND_BC", client_user.username).encode())

def make_block(recipient: str, amount: int):
    recp_user = User(recipient,client_user.blockchain)
    try:
        return client_user.nwtransaction(recp_user, amount, save = False, return_block = True)
    except InvalidTransactionException as e:
        print(colored(f"Error occurred while making transaction: {e}", 'red'))
        return None
    # return client_user.blockchain.chain[-1].to_dict()

def mine_block():
    pass


def write():
    # print("write thread started")
    while True:
        print("---------XITECOIN---------")
        payment: str = input("\nEnter payment: ")
        recipient = payment.split(' ')[0]
        amount = int(payment.split(' ')[1])

        send_data = make_json(data = make_block(recipient, amount), action = "BC_TRANSACTION_DATA", sender = client_user.username)
        print(colored(send_data, "yellow"))
        client.send(send_data.encode())
        print("Sent transaction data")
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
        # json_test = json.dumps({"message": {"hello":"hello1"}, "sender": client_user.username, "data": {"test": "data"}})
    # json_test = make_json(sender = client_user.username,action = "test action", data = {"hello":"hello1"})
    # client.send(json_test.encode())
    # print(json_test)
    # print("Sent message!")
    while True:
        pass

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
        data = "DEFAULT DATA"
        try:
            # print("recieving data")
            # data = client.recv(2024).decode().strip().replace('\n', '')
            data = client.recv(10024).decode()
            # print(data)
            data_json = json.loads(data)
            print(colored(data_json, 'cyan'))
            if data:
                # print(data_json)
                cl_handle_json(client, data_json)
            else:
                print("No data received")
        except Exception as e:
            print(colored(f"Error occurred while recieving message: {e}", 'red'))
            # print(colored(data, 'red'))
            break
        # finally:
        #     print("actual data recieved:")
        #     print(data)
        


def print_transaction_data(transaction_data):
    print(colored("\nTransaction Data:", 'yellow'))
    print(colored(f"Action: {transaction_data['action']}", 'green'))
    print(colored(f"Sender: {transaction_data['sender']}", 'green'))
    print(colored(f"Blockchain Name: {transaction_data['bc_name']}", 'green'))
    print(colored("\nBlock Data:", 'yellow'))
    print(colored(f"Previous Hash: {transaction_data['data']['prev_hash']}", 'green'))
    print(colored(f"Hash: {transaction_data['data']['hash']}", 'green'))
    print(colored(f"Timestamp: {transaction_data['data']['timestamp']}", 'green'))
    print(colored(f"Nonce: {transaction_data['data']['nonce']}", 'green'))
    print(colored("\nTransaction Details:", 'yellow'))
    print(colored(f"Sender Name: {transaction_data['data']['data']['sender_name']}", 'green'))
    print(colored(f"Recipient Name: {transaction_data['data']['data']['recipient_name']}", 'green'))
    print(colored(f"Amount: {transaction_data['data']['data']['amount']}", 'green'))
    print(colored(f"Message: {transaction_data['data']['data']['message']}", 'green'))
    


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 xiteclient.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]

    tb = Blockchain("tb")
    # tb.load_blockchain()
    # tb.verify_blockchain()

    # tb.create_genesis_block()
    client_user = XiteUser(username, password, tb)

    client.send(json.dumps({"sender": str(client_user.username), "action": "SENDER_NAME"}).encode())

    write_thread = threading.Thread(target = write)
    write_thread.start()
    recieve_thread = threading.Thread(target = recv_msg)
    recieve_thread.start()


    # if client_user.username == "Abhinav1":
    #     # send_message("my action",json.dumps({"testing":"tested"}))
    #     # sdata = make_json(data = client_user.nwtransaction(client_user, 0, save = False), action = "BC_TRANSACTION_DATA", sender = client_user.username)
    #     # print(sdata)
    #     # client.send(sdata.encode())
    #     # print("Sent transaction data")
    #     write_thread = threading.Thread(target = write)
    #     write_thread.start()
    # else:
    #     print("Not Abhinav1 so not sending transaction data, only recieving")
    #     client.send(make_json(json.dumps({"testing":"tested"})).encode())
    # # tb.save_blockchain()

    # write_thread = threading.Thread(target = write)
    # write_thread.start()


    
