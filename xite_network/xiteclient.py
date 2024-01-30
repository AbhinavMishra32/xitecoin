from multiprocessing import process
import socket
import threading
import traceback
from xitelib.node import Blockchain, InvalidTransactionException, User, Block, Data
from xite_network.xiteuser import XiteUser, add_block_to_buffer, make_node_block
import sys
import json
from termcolor import colored

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 12345))

nicknames = []
TRANSACTION_BUFFER = []
MINE = False

def set_mine(mine: str):
    global MINE
    if mine.lower() == 'true':
        MINE = True
    elif mine.lower() == 'false':
        MINE = False
    else:
        raise ValueError("Invalid value for MINE. Expected 'True' or 'False'.")

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
            # print("In BC_TRANSACTION_DATA action")
            block = make_node_block(data, client_user, data["data"]["prev_hash"], hash = data['data']['hash'])
            # client_user.blockchain.update_merkel_root()
            # block.hash = block.hash_block()
            print(colored(f"Block prev_hash: {block.prev_hash}", 'yellow'))
            print(colored(f"Block hash: {block.hash}", 'yellow'))
            if MINE:
                # if not block.is_mined(): # block isnt mined yet
                if data["data"]["nonce"] == 0:
                    print(colored("Block not mined yet", attrs=['bold'], color='light_red', on_color='on_white'))
                    add_block_to_buffer(TRANSACTION_BUFFER, make_node_block(data, client_user))
                    print(colored("Transaction buffer:", attrs=['bold'], on_color='on_black'))
                    i = 0
                    for transaction in TRANSACTION_BUFFER:
                        i += 1
                        print("----Transaction Data----")
                        print(colored(f"[{i}]:", 'yellow', attrs=['bold']))
                        # print(json.dumps(transaction, indent=4))
                        print(colored(f"SENDER'S CHAIN LENGTH : {data['data']['data']['chain_length']}", 'light_cyan', attrs=['bold', 'underline']))  # Remove 'light_cyan' attribute
                        print_transaction_data(transaction)
                        print("--------------------")
                    print(colored(f"BUFFER SIZE: {len(TRANSACTION_BUFFER)}", attrs=['bold']))

                    print(colored("NOW MINING BLOCK: ", 'yellow', attrs=['bold']))
                    if XiteUser.process_mined_block(data, client_user, use_multithreading=False):
                        TRANSACTION_BUFFER.pop(TRANSACTION_BUFFER.index(data))
                # else:
                #     #checking if block is correct or not:
                #     XiteUser.process_mined_block(block, client_user, use_multithreading=False)
        else:
            print(colored("No action specified", 'light_red'))
            print(colored(data, 'light_grey'))

    except Exception as e:
        print(colored(f"Error occurred while handling json: {e}", attrs=['bold'], color='light_red'))
        print(colored("TRACEBACK OF CL_HANDLE_JSON:", attrs=['bold'], color='red'))
        traceback.print_exc()
        print(colored(json.dumps(data, indent = 4), 'red'))

def make_json(data, sender: str = "Default sender", action: str = "Default action", **kwargs) -> str:
    if isinstance(data, set):
        data = list(data)
    json_data = {"action": action, "sender": sender, "data": data, "bc_name": client_user.blockchain.name}
    json_data["data"].update(kwargs)
    return json.dumps(json_data)
        
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

def synchronize_blockchain(user: XiteUser):
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
            new_block = Block(data, int(block['data']['data']['nonce']), hash = block['data']['hash'])
            # new_block.hash = new_block.hash_block()
            # blockchain.save_blockchain()
            # blockchain.load_blockchain()
            if len(blockchain.chain) > 0:
                new_block.prev_hash = blockchain.chain[-1].hash
            blockchain.chain.append(new_block)
        return True
    except Exception as e:
        print(f"Failed to synchronize blockchain [{colored('load_blockchain_from_data', 'light_magenta')}]: {e}")
        return False

def make_transaction(recipient: str, amount: int, blockchain: Blockchain):
    t = Blockchain(blockchain.name)
    t.load_blockchain()
    chain_length = len(t.chain)
    if chain_length > 0:
        prev_hash = t.chain[-1].hash
        send_data = make_json(data = make_block(recipient, amount), action = "BC_TRANSACTION_DATA", sender = client_user.username, prev_hash = prev_hash)
        send_data = json.loads(send_data)  # Convert send_data to a dictionary
        send_data["data"]["data"]["chain_length"] = chain_length
        print(colored(send_data, "yellow"))
        client.send(json.dumps(send_data).encode())
    print(colored("Sent transaction data", 'green'))

def write():
    # print("write thread started")
    while True:
        print("---------XITECOIN---------")
        payment: str = input("\nEnter payment: ")
        try:
            recipient = payment.split(' ')[0]
            amount = int(payment.split(' ')[1])
            make_transaction(recipient, amount, client_user.blockchain)
        except Exception:
            # print("IndexError occurred while handling json")
            print(colored("Please enter transaction correctly. [Username] [Amount]",'red',attrs =['bold']))
        # for i in range(1,5):


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
            data = client.recv(100024).decode()
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
            traceback.print_exc()
            break
        # finally:
        #     print("actual data recieved:")
        #     print(data)
        

# def mining_thread():
#     while True:
#         if TRANSACTION_BUFFER:
#             print("NOW MINING BLOCK: ")
#             XiteUser.process_mined_block(TRANSACTION_BUFFER, client_user, use_multithreading=False)
        


def print_transaction_data(transaction_data, repeat=False):
    try:
        print(colored("\nBlock Data:", 'yellow'), end="\r" if repeat else "\n")
        print(colored(f"Previous Hash: {transaction_data['prev_hash']}", 'light_cyan'), end="\r" if repeat else "\n")
        print(colored(f"Hash: {transaction_data['hash']}", 'light_cyan'), end="\r" if repeat else "\n")
        print(colored(f"Timestamp: {transaction_data['timestamp']}", 'light_cyan'), end="\r" if repeat else "\n")
        print(colored(f"Nonce: {transaction_data['nonce']}", 'light_cyan'), end="\r" if repeat else "\n")
        print(colored("\nTransaction Details:", 'yellow'), end="\r" if repeat else "\n")
        print(colored(f"Sender Name: {transaction_data['data']['sender_name']}", 'light_cyan'), end="\r" if repeat else "\n")
        print(colored(f"Recipient Name: {transaction_data['data']['recipient_name']}", 'light_cyan'), end="\r" if repeat else "\n")
        print(colored(f"Amount: {transaction_data['data']['amount']}", 'light_cyan'), end="\r" if repeat else "\n")
        print(colored(f"Message: {transaction_data['data']['message']}", 'light_cyan'), end="\r" if repeat else "\n")
    except:
        print(colored("Error occurred while printing transaction data", 'red'))
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 xiteclient.py <username> <password> [MINE]")
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    set_mine(sys.argv[3])

    tb = Blockchain(f"tb_{username}")
    # if not tb.load_blockchain():
    #     tb.create_genesis_block()
    #     tb.save_blockchain()
    # if len(tb.chain) == 0:
    #     tb.create_genesis_block()
    client_user = XiteUser(username, password, tb)

    client.send(json.dumps({"sender": str(client_user.username), "action": "SENDER_NAME"}).encode())

    write_thread = threading.Thread(target=write)
    write_thread.start()
    receive_thread = threading.Thread(target=recv_msg)
    receive_thread.start()