import socket
import threading
import traceback
from xitelib.node import Blockchain, InvalidTransactionException, User, Block, Data
from xite_network.xiteuser import XiteUser, add_block_to_buffer, make_node_block
import sys
import json
from util.debug import debug_log
from termcolor import colored


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    client.connect(("localhost", 12345))
except ConnectionRefusedError as e:
    print(colored(f"Server not started!", 'red'))
    sys.exit(1)

nicknames = []
TRANSACTION_BUFFER = []
MINE = False
REWARD = 1

IS_LONGEST_CHAIN = False
LONGEST_CHAIN_LENGTH = 0
LONGEST_CLIENT_NAME = ""


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


def cl_handle_json(client, data: dict):
    # print("in cl_handle_json: ")
    try:
        sender = data.get("sender") or data.get("reciever")
        if sender:
            if sender not in nicknames:
                nicknames.append(sender)
                print("Nicknames stored:")
                print(nicknames)
                print(f"New user connected: {sender}")
        else:
            print(colored("No sender specified", 'light_red'))

        action = data.get("action")

        if action == "C_LEN_BROADCAST" and data["data"]["reciever"] == client_user.username:
            debug_log("reciever: " ,data["data"]["reciever"])
            debug_log(data)
            chain_length = data["data"]["chain_length"]
            print(colored(f"RECIEVED CHAIN LENGTH: {chain_length}", 'yellow'))
            global LONGEST_CHAIN_CLIENT_NAME
            global LONGEST_CHAIN_LENGTH
            LONGEST_CHAIN_CLIENT_NAME = data["data"]["lgt_c_name"]
            LONGEST_CHAIN_LENGTH = chain_length
            if chain_length > len(client_user.blockchain):
                global IS_LONGEST_CHAIN
                IS_LONGEST_CHAIN = False
                debug_log("There is a longer blockchain available. Requesting blockchain update.")
                #now that we know there is a longer chain available, we request the blockchain from the sender
                # sync_bc(client, data, client_user.username, recv = True) #this function here wont work as the data is this: {'action': 'C_LEN_BROADCAST', 'data': {'chain_length': 21, 'reciever': 'Abhinav2', 'lgt_c_name': 'Abhinav1'}}, we need the blockchain data to recieve, not the chain length broadcast data
                client.send(json.dumps({"action" :  "WANT_BC", "sender" : LONGEST_CHAIN_CLIENT_NAME, "reciever":client_user.username}).encode())

            elif chain_length <= len(client_user.blockchain):
                IS_LONGEST_CHAIN = True
                debug_log("Blockchain is up to date.")
            chain_len_status()
                # req_bc_update(client_user.username)

        if action == "WANT_BC" and data["sender"] == client_user.username:
            debug_log("INSIDE WANT_BC ACTION")
            # the person wants the blockchain, so we send it to them because sender is our username, we are sending it to the "reciever" client
            process_sync_bc(client, data, reciever = data.get("reciever", KeyError("No sender found in WANT_BC action")), send = True)
            #now we will send bc with GIVE_BC action
            # client.send(json.dumps({"action": "SEND_BC", "sender": client_user.username, "reciever": data["reciever"]}).encode())

        if action == "GIVE_BC" and data["reciever"] == client_user.username:
            print("Received latest blockchain from server")
            debug_log("LATEST BLOCKCHAIN: ")
            debug_log(colored(data, 'light_cyan'))
            debug_log("Now starting sync_bc function with recv = True and process = True")
            try:
                process_sync_bc(client, data, reciever = data.get("sender", KeyError("No sender found in GIVE_BC action")), recv = True, process = True)
            except:
                sync_bc()

        elif action == "BC_TRANSACTION_DATA":
            # check_bc_len(client_user.blockchain)
            block = make_node_block(data, client_user, data["prev_hash"], hash = data['data']['hash'])
            print(colored(f"Block prev_hash: {block.prev_hash}", 'yellow'))
            print(colored(f"Block hash: {block.hash}", 'yellow'))
            # if data["data"]["data"]["sender_name"] == "XiteNetwork" and data["data"]["data"]["recipient_name"] == client_user.username:
            #     print(colored("Block sender is XiteNetwork, ignoring block", 'yellow'))
            #     block = make_node_block(data, client_user)
            #     client_user.blockchain.add_block(block)
            #     client_user.blockchain.save_blockchain()
            #     debug_log("Block added to blockchain without mining as it already has a nonce")
            #     # debug_log("Now syncing bc as latest transaction was from XiteNetwork")
            #     # sync_bc()
            print(colored("BEFORE WALLET THING", 'red'))
            print(colored(data, 'red'))


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
                    #TODO: check if recieving block's prev hash matches the hash of the last block in the local blockchain
                    client_user.blockchain.load_blockchain()

                    print(colored("NOW MINING BLOCK: ", 'yellow', attrs=['bold']))
                    if XiteUser.process_mined_block(data, client_user, use_multithreading=False, client_user=client_user):
                        # LOGIC FOR GIVING SOME REWARD FOR MINING BLOCK
                        t = Blockchain(client_user.blockchain.name)
                        t.load_blockchain()
                        chain_length = len(t.chain)
                        prev_hash = t.chain[-1].hash
                        debug_log(f"Previous hash: {prev_hash}")
                        if data.get('sender', KeyError("sender not in data")) == client_user.username:
                            #ignore the block and dont mine:
                            # print(colored("Block sender is client user with nonce !=0, saving block", 'yellow'))
                            # block = make_node_block(data, client_user)
                            # client_user.blockchain.add_block(block)
                            # client_user.blockchain.save_blockchain()
                            # debug_log("Block added to blockchain without mining as it already has a nonce")
                            # debug_log("Now saving to wallet as latest transaction was from client user")
                            # colored(data, 'magenta')
                            print(colored("Adding to wallet, sender is client user", 'yellow', attrs=['bold']))
                            client_user.save_to_wallet(-data['data']['data']['amount'], data['data']['data']['recipient_name'], data['sender'])
                            debug_log("Now syncing bc as latest transaction was from client user")
                            sync_bc()
                        elif data['data']['data'].get("recipient_name", KeyError("recipient_name not found")) == client_user.username:
                            print(colored('IN RECIPIENT_NAME THING', 'yellow'))
                            #block is already mined
                            # print(colored("Block already mined", attrs=['bold'], color='green', on_color='on_white'))
                            # print(colored(data["data"], attrs=['bold'], color='green'))
                            # debug_log("Saving already mined block")
                            # block = make_node_block(data, client_user)
                            # client_user.blockchain.add_block(block)
                            # client_user.blockchain.save_blockchain()
                            # debug_log("Block added to blockchain without mining as it already has a nonce")
                            print(colored("Adding to wallet, receiver is client user", 'yellow', attrs=['bold']))
                            client_user.save_to_wallet(data['data']['data']['amount'], data['data']['data']['recipient_name'], data['sender'])
                            sync_bc()

                        # client.send(json.dumps({"action": "MINE_STATUS", "sender": client_user.username}))
                        client_user.save_to_wallet(REWARD, client_user.username, "XiteNetwork", message = f"Reward for hash: {data['data']['hash']}")

                        # return
                        # wallet = XiteUser("XiteNetwork", "pass", client_user.blockchain)
                        # #after mining the user tells to the server that it mined the block (the server "gets to know this") and then the server adds reward to that user's wallet database


                        # #making the block for reward where reward is given from server, after this we will mine this block ourselfs and broadcast transaction with the nonce also
                        # reward_data = wallet.nwtransaction(client_user, REWARD, save = False, return_as_json = True, check_balance=False)
                        # s_reward_data = make_json(data =reward_data, action = "BC_TRANSACTION_DATA", sender = client_user.username, prev_hash = prev_hash)
                        # s_reward_data = json.loads(s_reward_data)  # Convert send_data to a dictionary
                        # # send_data["data"]["data"]["chain_length"] = chain_length
                        # # print(colored(send_data, "yellow"))

                        # mined_reward_block = XiteUser.mine_block(s_reward_data, client_user).to_dict()
                        # mined_reward_data = make_json(mined_reward_block, action = "BC_TRANSACTION_DATA", sender = client_user.username, prev_hash = prev_hash)
                        # mined_reward_data = json.loads(mined_reward_data)  # Convert send_data to a dictionary
                        # mined_reward_data["data"]["data"]["chain_length"] = chain_length
    
                        # # if mined_reward_data["data"]["nonce"] == 0:
                        # #     raise Exception("Block not mined yet")
                        # # else:
                        # #     debug_log("Mined reward data: ",mined_reward_data)
                        # # client.send(json.dumps(mined_reward_data).encode())
                        # # print(colored("Sent reward transaction data", 'green'))
                else:
                    pass
                    # block is already mined
                    # print(colored("Block already mined", attrs=['bold'], color='green', on_color='on_white'))
                    # print(colored(data["data"], attrs=['bold'], color='green'))
                    # debug_log("Saving already mined block")
                    # block = make_node_block(data, client_user)
                    # client_user.blockchain.add_block(block)
                    # client_user.blockchain.save_blockchain()
                    # debug_log("Block added to blockchain without mining as it already has a nonce")
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
    for key, value in kwargs.items():
        json_data[key] = value
    # json_data["data"].update(kwargs)
    return json.dumps(json_data)
        
def process_sync_bc(client, data: dict, reciever = "Non Specific", recv = False, send = False, process = False):
    debug_log("INSIDE SYNC_BC FUNCTION")
    #process is false when we are just broadcasting that we want the blockchain
    #process is true when we get the blockchain data also and now we will process it
    if recv:
        #just asking for the blockchain, dont want any data to save yet, for that we will call this function with process = True.
        pass
    if recv and process:
        debug_log("INSIDE SYNC_BC FUNCTION [RECV]")
        print("Received blockchain from:", data.get("sender", KeyError("No sender found in data")))
        print(colored(data, 'green'))
        data["bc_name"] = client_user.blockchain.name
        received_blockchain = Blockchain(data["bc_name"])
        if load_blockchain_from_data(received_blockchain, data["data"]):
            if received_blockchain.verify_blockchain():
                print("Blockchain verification successful")
                # consensus algorithm in network (offline implementation done in node.py):
                if len(received_blockchain.chain) > len(client_user.blockchain.chain):
                    print("Blockchain updated with longer chain from server")
                    client_user.blockchain = received_blockchain
                    debug_log("now printing the loaded blockchain:")
                    client_user.blockchain.load_blockchain()
                    client_user.blockchain.save_blockchain()
                    print(client_user.blockchain)
                    print("Blockchain saved successfully")
                # else:
                #     print("Error occurred while verifying blockchain")
                    
                #     raise Exception("Blockchain verification failed")
        else:
            print("Failed to synchronize and load blockchain")
            raise Exception("Failed to synchronize and load blockchain")
    if send:
        # debug_log("INSIDE SYNC_BC FUNCTION [SEND]")
        with open(client_user.blockchain.file_path, 'r') as f:
            blockchain_json = json.load(f)
            blockchain = Blockchain(client_user.blockchain.name)
            blockchain.load_blockchain()
            print(make_json(blockchain_json, action = "GIVE_BC", sender = client_user.username, reciever=reciever).encode())
            client.send(make_json(blockchain_json, action = "GIVE_BC", sender = client_user.username, reciever=reciever).encode())
            debug_log("Blockchain data sent to client: ")
            # print(blockchain)

def make_block(recipient: str, amount: int):
    recp_user = User(recipient,client_user.blockchain)
    try:
        return client_user.nwtransaction(recp_user, amount, save = False, return_as_json = True)
    except InvalidTransactionException as e:
        print(colored(f"Error occurred while making transaction: {e}", 'red'))
        return None
    # return client_user.blockchain.chain[-1].to_dict()

def synchronize_blockchain(user: XiteUser, chain: list = [], reciever: str = "Default sender"):
    d = make_json({"Sync Blockchain": "Sync Blockchain"}, user.username, "SYNC_BC", chain = chain, reciever = reciever)
    client.send(d.encode())

def load_blockchain_from_data(blockchain: Blockchain, blockchain_data: list) -> bool:
    try:
        blockchain.chain = []
        for block in blockchain_data:
            sender = User(block['data']['sender_name'], blockchain)
            recipient = User(block['data']['recipient_name'], blockchain)
            data = Data(sender, recipient, block['data']['amount'], block['data']['message'], block['timestamp'])
            new_block = Block(data, int(block['nonce']), hash = block['hash'], prev_hash = block['prev_hash'], timestamp = block['timestamp'])  
            blockchain.chain.append(new_block)
        blockchain.save_blockchain()
        blockchain.load_blockchain()
        return True
    except Exception as e:
        print(f"Failed to synchronize blockchain [{colored('load_blockchain_from_data', 'light_magenta')}]: {e}")
        return False

def make_transaction(recipient: str, amount: int, blockchain: Blockchain):
    t = Blockchain(blockchain.name)
    t.load_blockchain()
    chain_length = len(t.chain)
    print("printing blockchain before prev_hash", 'magenta')
    print(t, 'magenta')
    if chain_length > 0:
        prev_hash = t.chain[-1].hash
        debug_log(f"Previous hash: {prev_hash}")
        send_data = make_json(data = make_block(recipient, amount), action = "BC_TRANSACTION_DATA", sender = client_user.username, prev_hash = prev_hash)
        send_data = json.loads(send_data)  # Convert send_data to a dictionary
        send_data["data"]["data"]["chain_length"] = chain_length
        print(colored(send_data, "yellow"))
        client.send(json.dumps(send_data).encode())
    print(colored("Sent transaction data", 'green'))
    # client_user.save_to_wallet(-amount, recipient, client_user.username)

#temporary method for updating chain length, length is updated by the server, 
#TODO: implement this
def c_len_update(blockchain: Blockchain):
    t = Blockchain(blockchain.name)
    t.load_blockchain()
    chain_length = len(t.chain)
    # send_data = make_json()

def req_bc_update(rec_name: str):
    client.send(json.dumps({"action": "UPDATE_BC", "sender": rec_name}).encode())



def sync_bc():
    # actual function with sync logic in process_sync_bc
    client.send(json.dumps({"action" :  "WANT_BC", "sender" : LONGEST_CHAIN_CLIENT_NAME, "reciever":client_user.username}).encode())

def chain_len_status():
    if IS_LONGEST_CHAIN:
        print(colored("Blockchain is up to date", 'green'))
        print(colored(f"Length of longest blockchain: {LONGEST_CHAIN_LENGTH}", 'green'))
    else:
        print(colored("Blockchain is not up to date", 'red'))
        print(colored(f"Length of longest blockchain: {LONGEST_CHAIN_LENGTH}", 'red'))

def check_bc_len(bc:Blockchain) -> bool:
    """
    Returns a bool value indicating whether the blockchain is the longest chain or not.
    uses the CHECK_BC_LEN action to check the length of the blockchain
    """
    debug_log("INSIDE CHECK_BC_LEN FUNCTION")
    client.send(json.dumps({"action": "CHECK_BC_LEN", "sender": client_user.username, "reciever": "server", "chain_length": len(bc)}).encode())
    return IS_LONGEST_CHAIN
def write(bc: Blockchain):
    # print("write thread started")
    while True:
        print("---------XITECOIN---------")
        payment: str = input("\nEnter payment: ")
        try:
            recipient = payment.split(' ')[0]
            amount = int(payment.split(' ')[1])
            print("Checking blockchain length before making transaction...")
            check_bc_len(bc)
            chain_len_status()
            if xc.verify_blockchain():
                colored("Blockchain verification successful before transaction", 'green')
                make_transaction(recipient, amount, client_user.blockchain)
            else:
                print("Error occurred while verifying blockchain")
                raise Exception("Blockchain verification failed")
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

def load_multiple_json_objects(data):
    try:
        objs = data.split('}{')
        json_objects = [json.loads(objs[0] + '}')]
        for obj in objs[1:]:
            json_objects.append(json.loads('{' + obj))
        return json_objects
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")

def recv_msg():
    buffer = ""
    while True:
        try:
            data = client.recv(100024).decode()
            buffer += data
            while buffer:
                try:
                    data_json, index = json.JSONDecoder().raw_decode(buffer)
                    buffer = buffer[index:].lstrip()
                    print(colored(data_json, 'cyan'))
                    if data_json:
                        cl_handle_json(client, data_json)
                    else:
                        print("No data received")
                except ValueError:
                    # Not enough data to decode, wait for more
                    break
        except Exception as e:
            print(colored(f"Error occurred while receiving json [recv_msg]: {e}", 'red'))
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

def args_parser():
    if len(sys.argv) != 4:
        print("Usage: python3 xiteclient.py <username> <password> [MINE]: True / False")
        sys.exit(1)

    # implement login system for username and password:

    username = sys.argv[1]
    password = sys.argv[2]
    set_mine(sys.argv[3])
    return username, password

if __name__ == "__main__":
    username, password = args_parser()
    xc = Blockchain(f"xc_{username}", init_load = True)

    client_user = XiteUser(username, password, xc)  
    # req_bc_update(client_user.username)

    #get updated blockchain from server which gets from other nodes so technically p2p then update the blockchain before making transaction
    # NOW UPDATE BLOCKCHAIN WITH SYNCED VERSION BEFORE ANY TRANSACTION

    client_user = XiteUser(username, password, xc)
    client.send(json.dumps({"sender": str(client_user.username), "action": "SENDER_NAME", "chain_length" : len(xc)}).encode())

    print("Checking blockchain length before making logging in...")
    check_bc_len(xc)

    print("printing LONGEST_CHAIN_LENGTH :-")
    print(LONGEST_CHAIN_LENGTH)
    write_thread = threading.Thread(target=write, args=(client_user.blockchain,))
    write_thread.start()
    receive_thread = threading.Thread(target=recv_msg)
    receive_thread.start()