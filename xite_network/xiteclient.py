from pydoc import cli
import socket
from tabnanny import check
import threading
import trace
import traceback

from annotated_types import T
from util import debug
from xitelib.node import Blockchain, InvalidTransactionException, User, Block, Data
from xite_network.xiteuser import XiteUser, add_block_to_buffer, make_node_block
import sys
import json
from util.debug import debug_log
from termcolor import colored
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    client.connect(("localhost", 50000))
except ConnectionRefusedError as e:
    debug_log(colored(f"Server currently offline. Please try again later", 'red'), env="dev")
    sys.exit(1)

nicknames = []
TRANSACTION_BUFFER = []
MINE = False

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
            debug_log(f"Error receiving data: {e}")
            break

        try:
            decoded_data = data.decode()
        except Exception as e:
            debug_log(f"Error decoding data: {e}")
            break

        try:
            cl_data_recvd = json.loads(decoded_data)
        except Exception as e:
            debug_log(f"Error parsing JSON: {e}")
            break


def cl_handle_json(client, data: dict):
    # debug_log("in cl_handle_json: ")
    try:
        sender = data.get("sender") or data.get("reciever")
        if sender:
            if sender not in nicknames:
                nicknames.append(sender)
                debug_log("Nicknames stored:")
                debug_log(nicknames)
                debug_log(f"New user connected: {sender}")
        else:
            debug_log(colored("No sender specified", 'light_red'))

        action = data.get("action")

        if action == "C_LEN_BROADCAST" and data["data"]["reciever"] == client_user.username:
            debug_log("reciever: " ,data["data"]["reciever"])
            debug_log(data)
            chain_length = data["data"]["chain_length"]
            debug_log(colored(f"RECIEVED CHAIN LENGTH: {chain_length}", 'yellow'))
            global LONGEST_CHAIN_CLIENT_NAME
            global LONGEST_CHAIN_LENGTH
            LONGEST_CHAIN_CLIENT_NAME = data["data"]["lgt_c_name"]
            LONGEST_CHAIN_LENGTH = chain_length

            if chain_length > len(client_user.blockchain):
                global IS_LONGEST_CHAIN
                IS_LONGEST_CHAIN = False
                sync_bc()
                # debug_log("There is a longer blockchain available. Requesting blockchain update.")
                #now that we know there is a longer chain available, we request the blockchain from the sender
                # sync_bc(client, data, client_user.username, recv = True) #this function here wont work as the data is this: {'action': 'C_LEN_BROADCAST', 'data': {'chain_length': 21, 'reciever': 'Abhinav2', 'lgt_c_name': 'Abhinav1'}}, we need the blockchain data to recieve, not the chain length broadcast data
                # client.send(json.dumps({"action" :  "WANT_BC", "sender" : LONGEST_CHAIN_CLIENT_NAME, "reciever":client_user.username}).encode())
                # sync_bc()

            elif chain_length <= len(client_user.blockchain):
                IS_LONGEST_CHAIN = True
                debug_log("Blockchain is up to date.")
            chain_len_status()
                # req_bc_update(client_user.username)

        if action == "WANT_BC" and data["sender"] == client_user.username and data["reciever"] != client_user.username:
            # debug_log("INSIDE WANT_BC ACTION")
            # the person wants the blockchain, so we send it to them because sender is our username, we are sending it to the "reciever" client
            process_sync_bc(client, data, reciever = data.get("reciever", KeyError("No sender found in WANT_BC action")), send = True)

        if action == "GIVE_BC" and data["reciever"] == client_user.username:
            debug_log("Received latest blockchain from server")
            debug_log("LATEST BLOCKCHAIN: ")
            debug_log(colored(data, 'light_cyan'))
            debug_log("Now starting sync_bc function with recv = True and process = True")
            try:
                process_sync_bc(client, data, reciever = data.get("sender", KeyError("No sender found in GIVE_BC action")), recv = True, process = True)
            except Exception as e:
                debug_log(f"Error occurred while in GIVE_BC action: {e}")
                # sync_bc()

        elif action == "BC_TRANSACTION_DATA":
            # check_bc_len(client_user.blockchain)
            block = make_node_block(data, client_user, data["prev_hash"], hash = data['data']['hash'])
            debug_log(colored(f"Block data before mining: {block}", 'yellow'))
            # debug_log(colored(f"Block prev_hash: {block.prev_hash}", 'yellow'))
            # debug_log(colored(f"Block hash: {block.hash}", 'yellow'))
            # if data["data"]["data"]["sender_name"] == "XiteNetwork" and data["data"]["data"]["recipient_name"] == client_user.username:
            #     debug_log(colored("Block sender is XiteNetwork, ignoring block", 'yellow'))
            #     block = make_node_block(data, client_user)
            #     client_user.blockchain.add_block(block)
            #     client_user.blockchain.save_blockchain()
            #     debug_log("Block added to blockchain without mining as it already has a nonce")
            #     # debug_log("Now syncing bc as latest transaction was from XiteNetwork")
            #     # sync_bc()


            if MINE:
                # if not block.is_mined(): # block isnt mined yet
                if data["data"]["nonce"] == 0:
                    debug_log(colored("Block not mined yet", attrs=['bold'], color='light_red', on_color='on_white'))
                    add_block_to_buffer(TRANSACTION_BUFFER, make_node_block(data, client_user, data["prev_hash"], hash = data['data']['hash']))
                    debug_log(colored("Transaction buffer:", attrs=['bold'], on_color='on_black'))
                    i = 0
                    for transaction in TRANSACTION_BUFFER:
                        i += 1
                        debug_log("----Transaction Data----")
                        debug_log(colored(f"[{i}]:", 'yellow', attrs=['bold']))
                        # debug_log(json.dumps(transaction, indent=4))
                        debug_log(colored(f"SENDER'S CHAIN LENGTH : {data['data']['data']['chain_length']}", 'light_cyan', attrs=['bold', 'underline']))  # Remove 'light_cyan' attribute
                        print_transaction_data(transaction)
                        debug_log("--------------------")
                    debug_log(colored(f"BUFFER SIZE: {len(TRANSACTION_BUFFER)}", attrs=['bold']))
                    #TODO: check if recieving block's prev hash matches the hash of the last block in the local blockchain
                    client_user.blockchain.load_blockchain()

                    # if client_user.blockchain.chain[-1].hash == data["prev_hash"]: #add later for more security
                    #     debug_log(colored("Previous hash matches with the last block in the blockchain", 'green'))
                    #     debug_log(colored("Now mining block...", 'yellow'))
                    data["data"]["data"]["prev_hash"] = block.prev_hash
                    debug_log(colored("NOW MINING BLOCK: ", 'yellow', attrs=['bold']))
                    if XiteUser.process_mined_block(data, client_user, use_multithreading=False, client_user=client_user):
                        # LOGIC FOR GIVING SOME REWARD FOR MINING BLOCK
                        t = Blockchain(client_user.blockchain.name)
                        t.load_blockchain()
                        client_user.blockchain = t
                        debug_log(f"client_user blockchain after mining: {client_user.blockchain}")
                        # debug_log(f"Blockchain after mining block: {t}")
                        # check_bc_len(client_user.blockchain)
                        chain_length = len(t.chain)
                        prev_hash = t.chain[-1].hash
                        debug_log(f"Previous hash: {prev_hash}")
                        if data.get('sender', KeyError("sender not in data")) == client_user.username:
                            #ignore the block and dont mine:
                            # debug_log(colored("Block sender is client user with nonce !=0, saving block", 'yellow'))
                            # block = make_node_block(data, client_user)
                            # client_user.blockchain.add_block(block)
                            # client_user.blockchain.save_blockchain()
                            # debug_log("Block added to blockchain without mining as it already has a nonce")
                            # debug_log("Now saving to wallet as latest transaction was from client user")
                            # colored(data, 'magenta')
                            debug_log(colored("Adding to wallet, sender is client user", 'yellow', attrs=['bold']))
                            client_user.save_to_wallet(-data['data']['data']['amount'], data['data']['data']['recipient_name'], data['sender'])
                            debug_log("Now syncing bc as latest transaction was from client user")
                            # sync_bc()
                        elif data['data']['data'].get("recipient_name", KeyError("recipient_name not found")) == client_user.username:
                            debug_log(colored('IN RECIPIENT_NAME THING', 'yellow'))
                            #block is already mined
                            # debug_log(colored("Block already mined", attrs=['bold'], color='green', on_color='on_white'))
                            # debug_log(colored(data["data"], attrs=['bold'], color='green'))
                            # debug_log("Saving already mined block")
                            # block = make_node_block(data, client_user)
                            # client_user.blockchain.add_block(block)
                            # client_user.blockchain.save_blockchain()
                            # debug_log("Block added to blockchain without mining as it already has a nonce")
                            debug_log(colored("Adding to wallet, receiver is client user", 'yellow', attrs=['bold']))
                            client_user.save_to_wallet(data['data']['data']['amount'], data['data']['data']['recipient_name'], data['sender'])
                            # sync_bc()

                        # client.send(json.dumps({"action": "MINE_STATUS", "sender": client_user.username}))

                        reward = data['data']['data']['amount'] / 10 # will be in float
                        client_user.save_to_wallet(reward, client_user.username, "XiteNetwork", message = f"Reward for hash: {data['data']['hash']}")

                        # return
                        # wallet = XiteUser("XiteNetwork", "pass", client_user.blockchain)
                        # #after mining the user tells to the server that it mined the block (the server "gets to know this") and then the server adds reward to that user's wallet database


                        # #making the block for reward where reward is given from server, after this we will mine this block ourselfs and broadcast transaction with the nonce also
                        # reward_data = wallet.nwtransaction(client_user, REWARD, save = False, return_as_json = True, check_balance=False)
                        # s_reward_data = make_json(data =reward_data, action = "BC_TRANSACTION_DATA", sender = client_user.username, prev_hash = prev_hash)
                        # s_reward_data = json.loads(s_reward_data)  # Convert send_data to a dictionary
                        # # send_data["data"]["data"]["chain_length"] = chain_length
                        # # debug_log(colored(send_data, "yellow"))

                        # mined_reward_block = XiteUser.mine_block(s_reward_data, client_user).to_dict()
                        # mined_reward_data = make_json(mined_reward_block, action = "BC_TRANSACTION_DATA", sender = client_user.username, prev_hash = prev_hash)
                        # mined_reward_data = json.loads(mined_reward_data)  # Convert send_data to a dictionary
                        # mined_reward_data["data"]["data"]["chain_length"] = chain_length
    
                        # # if mined_reward_data["data"]["nonce"] == 0:
                        # #     raise Exception("Block not mined yet")
                        # # else:
                        # #     debug_log("Mined reward data: ",mined_reward_data)
                        # # client.send(json.dumps(mined_reward_data).encode())
                        # # debug_log(colored("Sent reward transaction data", 'green'))
                else:
                    pass
                    # block is already mined
                    # debug_log(colored("Block already mined", attrs=['bold'], color='green', on_color='on_white'))
                    # debug_log(colored(data["data"], attrs=['bold'], color='green'))
                    # debug_log("Saving already mined block")
                    # block = make_node_block(data, client_user)
                    # client_user.blockchain.add_block(block)
                    # client_user.blockchain.save_blockchain()
                    # debug_log("Block added to blockchain without mining as it already has a nonce")
        else:
            debug_log(colored("No action specified", 'light_red'))
            debug_log(colored(data, 'light_grey'))

    except Exception as e:
        debug_log(colored(f"Error occurred while handling json: {e}", attrs=['bold'], color='light_red'))
        debug_log(colored("TRACEBACK OF CL_HANDLE_JSON:", attrs=['bold'], color='red'))
        traceback.print_exc()
        debug_log(colored(json.dumps(data, indent = 4), 'red'))

def make_json(data, sender: str = "Default sender", action: str = "Default action", **kwargs) -> str:
    if isinstance(data, set):
        data = list(data)
    json_data = {"action": action, "sender": sender, "data": data, "bc_name": client_user.blockchain.name}
    for key, value in kwargs.items():
        json_data[key] = value
    # json_data["data"].update(kwargs)
    return json.dumps(json_data)
        
def process_sync_bc(client, data: dict, reciever = "Non Specific", recv = False, send = False, process = False):
    # debug_log("INSIDE SYNC_BC FUNCTION")
    #process is false when we are just broadcasting that we want the blockchain
    #process is true when we get the blockchain data also and now we will process it
    if recv:
        #just asking for the blockchain, dont want any data to save yet, for that we will call this function with process = True.
        pass
    if recv and process:
        debug_log("INSIDE SYNC_BC FUNCTION [RECV]")
        debug_log("Received blockchain from:", data.get("sender", KeyError("No sender found in data")))
        debug_log(colored(data, 'green'))
        data["bc_name"] = client_user.blockchain.name
        received_blockchain = Blockchain(data["bc_name"])
        if load_blockchain_from_data(received_blockchain, data["data"]):
            if received_blockchain.verify_blockchain():
                debug_log("Blockchain verification successful")
                # consensus algorithm in network (offline implementation done in node.py):
                if len(received_blockchain.chain) > len(client_user.blockchain.chain):
                    debug_log("Blockchain updated with longer chain from server")
                    client_user.blockchain = received_blockchain
                    debug_log("now printing the loaded blockchain:")
                    client_user.blockchain.load_blockchain()
                    client_user.blockchain.save_blockchain()
                    debug_log(client_user.blockchain)
                    debug_log("Blockchain saved successfully")
                # else:
                #     debug_log("Error occurred while verifying blockchain")
                    
                #     raise Exception("Blockchain verification failed")
        else:
            debug_log("Failed to synchronize and load blockchain")
            raise Exception("Failed to synchronize and load blockchain")
    if send:
        # debug_log("INSIDE SYNC_BC FUNCTION [SEND]")
        with open(client_user.blockchain.file_path, 'r') as f:
            blockchain_json = json.load(f)
            blockchain = Blockchain(client_user.blockchain.name)
            blockchain.load_blockchain()
            debug_log(make_json(blockchain_json, action = "GIVE_BC", sender = client_user.username, reciever=reciever).encode())
            client.send(make_json(blockchain_json, action = "GIVE_BC", sender = client_user.username, reciever=reciever).encode())
            debug_log("Blockchain data sent to client: ")
            # debug_log(blockchain)

def make_block(recipient: str, amount: int, prev_hash = None):
    recp_user = User(recipient,client_user.blockchain)
    try:
        return client_user.nwtransaction(recp_user, amount, save = False, return_as_json = True)
    except InvalidTransactionException as e:
        debug_log(colored(f"Error occurred while making transaction: {e}", 'red'))
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
        # future functionality: add timestamp when updating through blockchain so that in wallet it shows when the transaction occured, not when it was updated
        XiteUser.update_wallet_through_blockchain(client_user)
        return True
    except Exception as e:
        debug_log(f"Failed to synchronize blockchain [{colored('load_blockchain_from_data', 'light_magenta')}]: {e}")
        return False

def make_transaction(recipient: str, amount: int, blockchain: Blockchain):
    t = Blockchain(blockchain.name)
    t.load_blockchain()
    chain_length = len(t.chain)
    debug_log("printing blockchain before prev_hash", 'magenta')
    debug_log(t, 'magenta')
    if chain_length > 0:
        prev_hash = t.chain[-1].hash
        block = make_block(recipient, amount)
        debug_log(f"Previous hash: {prev_hash}")
        send_data = make_json(data = block, action = "BC_TRANSACTION_DATA", sender = client_user.username, prev_hash = prev_hash)
        send_data = json.loads(send_data)  # Convert send_data to a dictionary
        send_data["data"]["data"]["chain_length"] = chain_length
        debug_log(colored(send_data, "yellow"))
        client.send(json.dumps(send_data).encode())
        debug_log(f"""BLOCKCHAIN LENGTH AFTER TRANSACTION: {len(t)}\n
                  Blockchain: {t}""")
    debug_log(colored("Sent transaction data", 'green'))
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
    # actual function with sync logic in process_sync_bc()

    client.send(json.dumps({"action" :  "WANT_BC", "sender" : LONGEST_CHAIN_CLIENT_NAME, "reciever":client_user.username}).encode())

def chain_len_status():
    if IS_LONGEST_CHAIN:
        debug_log(colored("Blockchain is up to date", 'green'))
        debug_log(colored(f"Length of longest blockchain: {LONGEST_CHAIN_LENGTH} [Client]", 'green'))
    else:
        debug_log(colored("Blockchain is not up to date", 'red'))
        debug_log(colored(f"Length of longest blockchain: {LONGEST_CHAIN_LENGTH}", 'red'))

def check_bc_len(bc:Blockchain) -> bool:
    """
    Returns a bool value indicating whether the blockchain is the longest chain or not.
    uses the CHECK_BC_LEN action to check the length of the blockchain.
    
    Does NOT update the blockchain, only updates the length to the longest chain length.
    """
    debug_log("INSIDE CHECK_BC_LEN FUNCTION")
    bc.load_blockchain()
    client.send(json.dumps({"action": "CHECK_BC_LEN", "sender": client_user.username, "reciever": "server", "chain_length": len(bc)}).encode())
    return IS_LONGEST_CHAIN

def console_cli(client_user: XiteUser): 
    while True:
        print("---------XITECOIN---------")
        print("1. Check balance")
        print("2. Check blockchain length")
        print("3. Make transaction")
        print("4. Print blockchain")
        print("5. Exit")
        choice = input("Enter choice: ")
        if choice == '1':
            print("Checking balance...")
            # client_user.check_balance()
        elif choice == '2':
            print("Checking blockchain length...")
            print("Length: ", len(client_user.blockchain))
        elif choice == '3':
            print("Making transaction...")
            recipient = input("Enter recipient: ")
            amount = int(input("Enter amount: "))
            if xc_transaction(recipient, amount, client_user.blockchain):
                print("Transaction successful")
        elif choice == '4':
            print("Printing blockchain...")
            print(client_user.blockchain)
        elif choice == '5':
            client.close()
            print("Exiting...")
            quit()
        else:
            print("Invalid choice")


def xc_transaction(recipient: str, amount: int, bc: Blockchain) -> bool:
    try:
        debug_log("Checking blockchain length before making transaction...")
        # check_bc_len(bc)
        chain_len_status()
        debug_log(f"Blockchain length before sync_bc(): {len(bc)}")
        # sync_bc()
        # bc.update_prev_hash()
        # print(bc)
        if xc.verify_blockchain():
            debug_log(colored("Blockchain verification successful before transaction", 'green'))
            make_transaction(recipient, amount, client_user.blockchain)

            check_bc_len(bc)
            return True
        else:
            debug_log("Error occurred while verifying blockchain")
            raise Exception("Blockchain verification failed\n",
                            f"Blockchain: {bc}")
    except Exception as e:
        debug_log(colored(f"Error occurred during transaction: {e}", 'red'))
        traceback.print_exc()
        return False


def write(bc: Blockchain):
    while True:
        try:
            console_cli(client_user)
        except IndexError:
            debug_log(colored("Please enter transaction correctly. [Username] [Amount]",'red',attrs =['bold']), env="dev")
        except ValueError:
            debug_log(colored("Please enter transaction correctly. [Username] [Amount]",'red',attrs =['bold']) , env="dev")
        except Exception as e:
            debug_log(colored(f"Error occurred while making transaction: {e}", 'red') , env="dev")
            traceback.print_exc()


def send_message(action: str, message):
    message_dict = json.loads(message)
    msg_json = json.dumps({
        "action": action, 
        "message": message_dict.get("message", "No message"),  # Use a default value if "message" key is not present
        "sender": client_user.username, 
        "data": message_dict.get("data", {})  # Use a default value if "data" key is not present
    }) 
    debug_log(msg_json)
    client.send(msg_json.encode())

def load_multiple_json_objects(data):
    try:
        objs = data.split('}{')
        json_objects = [json.loads(objs[0] + '}')]
        for obj in objs[1:]:
            json_objects.append(json.loads('{' + obj))
        return json_objects
    except json.JSONDecodeError as e:
        debug_log(f"JSONDecodeError: {e}")

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
                    debug_log(colored(data_json, 'cyan'))
                    if data_json:
                        cl_handle_json(client, data_json)
                    else:
                        debug_log("No data received")
                except ValueError:
                    # Not enough data to decode, wait for more
                    break
        except Exception as e:
            debug_log(colored(f"Error occurred while receiving json [recv_msg]: {e}", 'red'))
            traceback.print_exc()
            break
        # finally:
        #     debug_log("actual data recieved:")
        #     debug_log(data)
        

# def mining_thread():
#     while True:
#         if TRANSACTION_BUFFER:
#             debug_log("NOW MINING BLOCK: ")
#             XiteUser.process_mined_block(TRANSACTION_BUFFER, client_user, use_multithreading=False)
        



def print_transaction_data(transaction_data, repeat=False):
    try:
        debug_log(colored("\nBlock Data:", 'yellow'), end="\r" if repeat else "\n")
        debug_log(colored(f"Previous Hash: {transaction_data['prev_hash']}", 'light_cyan'), end="\r" if repeat else "\n")
        debug_log(colored(f"Hash: {transaction_data['hash']}", 'light_cyan'), end="\r" if repeat else "\n")
        debug_log(colored(f"Timestamp: {transaction_data['timestamp']}", 'light_cyan'), end="\r" if repeat else "\n")
        debug_log(colored(f"Nonce: {transaction_data['nonce']}", 'light_cyan'), end="\r" if repeat else "\n")
        debug_log(colored("\nTransaction Details:", 'yellow'), end="\r" if repeat else "\n")
        debug_log(colored(f"Sender Name: {transaction_data['data']['sender_name']}", 'light_cyan'), end="\r" if repeat else "\n")
        debug_log(colored(f"Recipient Name: {transaction_data['data']['recipient_name']}", 'light_cyan'), end="\r" if repeat else "\n")
        debug_log(colored(f"Amount: {transaction_data['data']['amount']}", 'light_cyan'), end="\r" if repeat else "\n")
        debug_log(colored(f"Message: {transaction_data['data']['message']}", 'light_cyan'), end="\r" if repeat else "\n")
    except:
        debug_log(colored("Error occurred while printing transaction data", 'red'))
        traceback.print_exc()

def args_parser():
    if len(sys.argv) != 4:
        debug_log("Usage: python3 xiteclient.py <username> <password> [MINE]: True / False")
        sys.exit(1)

    # implement login system for username and password:

    username = sys.argv[1]
    password = sys.argv[2]
    set_mine(sys.argv[3])
    return username, password

class Transaction(BaseModel):
    username: str
    amount: int
    status: str

class Balance(BaseModel):
    bc_name: str
    name: str
    net_amount: int
    history: List[dict]

@app.post("/tr/{username}/{amount}")
def send_transaction(username: str, amount: int):
    try:
        xc_transaction(username, amount, client_user.blockchain)
        return Transaction(username=username, amount=amount, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wallet")
def get_balance():
    try:
        with open(client_user.wallet_name, 'r') as f:
            data = json.load(f)

        net_amount = data["net_amount"]
        history = data["history"]

        latest_transaction = history[-1] if history else None

        for item in data:
            # if i["name"] == client_user.username:
            return Balance(bc_name="xc_Abhinav2", name=client_user.username, net_amount=net_amount, history=history)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main(client_user: XiteUser, client: socket.socket):
    client.send(json.dumps({"sender": str(client_user.username), "action": "SENDER_NAME", "chain_length" : len(xc)}).encode())

    debug_log("Checking blockchain length before making logging in...")
    check_bc_len(xc)

    debug_log("printing LONGEST_CHAIN_LENGTH :-")
    debug_log(LONGEST_CHAIN_LENGTH)
    # client_user.blockchain.update_prev_hash()
    debug_log("Blockchain before starting threads:")
    debug_log(colored(client_user.blockchain, 'cyan'))
    write_thread = threading.Thread(target=write, args=(client_user.blockchain,))
    write_thread.start()
    receive_thread = threading.Thread(target=recv_msg)
    receive_thread.start()

    uvicorn.run(app, host="localhost", port=8000)


if __name__ == "__main__":
    username, password = args_parser()
    xc = Blockchain(f"xc_{username}", init_load = True)

    client_user = XiteUser(username, password, xc)
    client_user.blockchain.load_blockchain()
    main(client_user, client)