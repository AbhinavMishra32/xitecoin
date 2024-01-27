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
        elif action == "SYNC_BC":
            print("Received latest blockchain from server")
            received_blockchain = Blockchain(data["data"]["name"])
            if load_blockchain_from_data(received_blockchain, data["data"]["chain"]):
                if received_blockchain.verify_blockchain():
                    print("Blockchain verification successful")
                    # consensus algorithm:
                    if len(received_blockchain.chain) > len(client_user.blockchain.chain):
                        client_user.blockchain = received_blockchain
                        print("Blockchain updated with longer chain from server")
                    received_blockchain.save_blockchain()
                    print("Blockchain saved successfully")
                else:
                    print("Error occurred while verifying blockchain")
            else:
                print("Failed to synchronize and load blockchain")
        elif action == "BC_TRANSACTION_DATA":
            if int(data["data"]["nonce"]) == 0:
                print(colored("Block not mined yet", attrs=['bold'], color='light_red', on_color='on_white'))
                add_block_to_buffer(TRANSACTION_BUFFER, make_node_block(data, client_user))
                print(colored("Transaction buffer:", attrs=['bold'], on_color='on_black'))
                for transaction in TRANSACTION_BUFFER:
                    print("----Transaction Data----")
                    # print(transaction)
                    print_transaction_data(transaction)
                    # else:
                    #     print("Transaction does not contain 'sender' key")
                    # print_transaction_data(data)
                    print("--------------------")
                print(colored(f"BUFFER SIZE: {len(TRANSACTION_BUFFER)}", attrs=['bold']))
            else:
                #checking if block is correct or not:
                print("Checking block validity:")
                block = make_node_block(data, client_user)
                if client_user.blockchain.verify_PoW_singlePass(block):
                    print(colored("Block is valid", 'light_green'))
                    print(colored("Saving block", 'light_green'))
                    XiteUser.save_block(client_user, block)
                    print(colored("Block saved successfully", 'light_green'))
                    print(colored("Verifying blockchain", 'light_green'))
                    if client_user.blockchain.verify_blockchain():
                        print(colored("Blockchain verified successfully", 'light_green'))
                    else:
                        print(colored("Blockchain verification failed", 'light_red'))
                        print("Requesting latest blockchain from other nodes")
                        synchronize_blockchain(client_user, client_user.blockchain)
                        

                    # print(colored("Broadcasting block", 'green'))
                    # broadcast(json.dumps(data).encode())
                    # print(colored("Block broadcasted successfully", 'green'))
                
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

def synchronize_blockchain(user: XiteUser, blockchain: Blockchain):
    d = make_json({"Sync Blockchain": "Sync Blockchain"}, user.username, "SYNC_BC")
    client.send(d.encode())
    pass

def load_blockchain_from_data(blockchain: Blockchain, blockchain_data: list) -> bool:
    try:
        blockchain.chain = []
        for block in blockchain_data:
            sender = User(block['data']['sender_name'], blockchain)
            recipient = User(block['data']['recipient_name'], blockchain)
            data = Data(sender, recipient, block['data']['amount'], block['data']['message'])
            new_block = Block(data, block['nonce'])
            new_block.hash = new_block.hash_block()
            if len(blockchain.chain) > 0:
                new_block.prev_hash = blockchain.chain[-1].hash
            blockchain.chain.append(new_block)
        return True
    except Exception as e:
        print(f"Failed to synchronize blockchain [{colored("load_blockchain_from_data", 'light_magenta')}]: {e}")
        return False

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
    try:
        print(colored("\nBlock Data:", 'yellow'))
        print(colored(f"Previous Hash: {transaction_data['prev_hash']}", 'light_cyan'))
        print(colored(f"Hash: {transaction_data['hash']}", 'light_cyan'))
        print(colored(f"Timestamp: {transaction_data['timestamp']}", 'light_cyan'))
        print(colored(f"Nonce: {transaction_data['nonce']}", 'light_cyan'))
        print(colored("\nTransaction Details:", 'yellow'))
        print(colored(f"Sender Name: {transaction_data['data']['sender_name']}", 'light_cyan'))
        print(colored(f"Recipient Name: {transaction_data['data']['recipient_name']}", 'light_cyan'))
        print(colored(f"Amount: {transaction_data['data']['amount']}", 'light_cyan'))
        print(colored(f"Message: {transaction_data['data']['message']}", 'light_cyan'))
    except:
        print(colored("Error occurred while printing transaction data", 'red'))


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


    
