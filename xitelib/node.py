# XiteCoin ($XC), 2024
# Created by Abhinav Mishra

# This file contains the code for the node of the XiteCoin blockchain network.
# The node is responsible for creating and verifying transactions, and mining
# blocks. The node also contains the blockchain, which is a list of blocks.

# The node is also responsible for creating and storing the public and private
# keys of the users. The public key is used to verify the signature of the
# transaction, and the private key is used to sign the transaction.

# The node also contains the code for the wallet, which is used to store the
# public and private keys of the user. The wallet is also used to create
# transactions, and to sign them.

#*  XITECOIN IMPLEMENTATION (WORKING):
#*  Difficulity (DIFFICULITY) of set for the whole blockchain instead of one block separately.
#*  Each block has a single transaction (Will later update to multiple transactions in a single block with seperate difficulity of each block)
#*  User broadcasts a single block and another user hashes that block and gets reward
#*

from datetime import datetime
import hashlib
import json
import traceback
import rsa
# from settings.settings import Settings
import time
import os
from util import debug
from util.debug import debug_log

# DIFFICULITY = Settings.BLOCKCHAIN_DIFFICULITY.value
DIFFICULITY = 4
HASH_WITHOUT_TIMESTAMP = True #for static hashing [same hash of a block everytime with the same variables, but time isnt a variable when this is enabled], wont change with different time (used for testing hashes of the blockchain comparing other changing factors than just time)
BLOCK_REWARD = 2.5

class Data:
    def __init__(self, sender: 'User', recipient: 'User', amount: int, message: str, timestamp = None):
        if timestamp is None:
            self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        else:
            self.timestamp = timestamp
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.message = message
        self.transaction = {"sender_name":sender.name, "recipient_name": recipient.name, "amount": amount, "message": message}

    def __str__(self):
        return self.message
class Block:
    def __init__(self, data: Data, nonce: int = 0, prev_hash: str = "", hash = None, timestamp = None):
        self.merkel_root = ""
        self.added_to_bc = False
        # if prev_hash is None:
        #     self.prev_hash = ""
        # else:
        self.prev_hash = prev_hash
        if timestamp is None:
            self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # string
        else:
            self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        if data.sender.name == "Genesis":
                self.hash = "xite"
        # elif hash is None:
        #     self.hash = self.hash_block()
        # else:
        #     self.hash = hash
        if hash:
            self.hash = hash
        else:
            self.hash = self.hash_block() 
            

        # debug_log("Previous hash while initializing Block: ", self.prev_hash)

    def __str__(self):
        return f"HASH: {self.hash} | PREV_HASH: {self.prev_hash} TIMESTAMP: {self.timestamp} DATA: {self.data}, NONCE: {self.nonce}"

    def is_mined(self) -> bool:
        return self.hash[:DIFFICULITY] == DIFFICULITY*"0"

    def to_dict(self):
        return {
            'prev_hash': self.prev_hash,
            'hash':self.hash,
            'data': self.data.transaction,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
        }

    def hash_block(self) -> str:
        if self.data.sender.name == "Genesis":
            return "xite"
        if HASH_WITHOUT_TIMESTAMP:
            if self.prev_hash == "" and self.data.sender.name != "Genesis" and self.added_to_bc:
                raise InvalidBlockchainException("Previous hash is empty while hashing!")
            data_string = f"{self.data.sender.name}{self.data.amount}{self.data.recipient.name}{self.data.message}{self.prev_hash}{self.merkel_root})"
            # debug_log("Data string: ", data_string)
            debug_log("Previous Hash in hash_block: ", self.prev_hash)
            return hashlib.sha256(data_string.encode()).hexdigest()
        else:
            # data_string = f"{self.data.sender.name}{self.data.amount}{self.data.recipient.name}{self.data.message}{self.prev_hash}{self.data.timestamp}{self.merkel_root}" #old
            data_string = f"{self.data.sender.name}{self.data.amount}{self.data.recipient.name}{self.data.message}{self.prev_hash}{self.data.timestamp}"
            return hashlib.sha256(data_string.encode()).hexdigest()
        
class Blockchain:
    """
    Represents a blockchain.

    Attributes:
    - chain (list[Block]): The list of blocks in the blockchain.
    - name (str): The name of the blockchain.
    - file_path (str): The file path to save the blockchain.

    Methods:
    - update_merkel_root(): Updates the merkel root for each block in the blockchain.
    - __getitem__(index) -> Block: Returns the block at the specified index.
    - __str__() -> str: Returns a string representation of the blockchain.
    - clear(save_to_file=False, delete_file=False): Clears the chain and optionally saves the blockchain to a file and/or deletes the file.
    - load_blockchain() -> bool: Loads the blockchain from a file or creates a new one if it doesn't exist.
    - to_dict() -> list: Converts the blockchain to a list of dictionaries.
    - create_genesis_block(): Creates the genesis block of the blockchain.
    - proof_of_work(block) -> int: Performs the proof of work algorithm to find the nonce for the given block.
    - valid_proof(block: Block, nonce: int) -> list: Checks if the given nonce is a valid proof of work for the block.
    - add_block(block: Block) -> bool: Adds a new block to the blockchain.
    - verify_block_signature(block: Block) -> bool: Verifies the signature of a block.
    - verify_PoW_singlePass(block: Block) -> bool: Verifies the proof of work of a block in a single pass.
    - verify_blockchain() -> bool: Verifies the entire blockchain for valid proof of work.
    - verify_single_block(blockchain: Blockchain, block: Block): Verifies the proof of work of a single block.
    - save_blockchain(): Saves the blockchain to a file.
    """
    def __init__(self, name: str, init_load = False):
        self.chain: list[Block] = []
        self.name: str = name
        self.file_path = os.path.join("LocalBlockchain", self.name + "_lbc.json")

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        
        if init_load:
            self.load_blockchain()

    def append(self, block: Block):
        block.hash = block.hash_block()
        block.added_to_bc = True
        if self.update_prev_hash():
            debug_log(f"Previous hash of {block} updated in Blockchain.append!")
            self.chain.append(block)

    # gives the merkel root to each block
    def update_merkel_root(self):
        m_root = ""
        for block in self.chain:
            m_root += block.hash
            m_root = hashlib.sha256(m_root.encode()).hexdigest()
            block.merkel_root = hashlib.sha256(m_root.encode()).hexdigest()

    def __len__(self) -> int:
        return len(self.chain)

    def __getitem__(self, index) -> Block:
        return self.chain[index]

    def __str__(self):
        chain_data: str = ""
        block_index: int = -1
        for block in self.chain:
            block_index += 1
            chain_data += f"BLOCK: {block_index} "
            chain_data += str(block)
            chain_data += "\n"
        return chain_data
    
    def update_prev_hash(self):
        if len(self.chain) > 1:
            for block in self.chain:
                block.prev_hash = self.chain[self.chain.index(block)-1].hash
                debug_log(f"Previous hash updated to: {block.prev_hash}, for block: {block}")
                return True

    def verify_prev_hash(self) -> bool:
        for block in self.chain:
            if block.prev_hash != self.chain[self.chain.index(block)-1].hash:
                return False
        return True
    
    def clear(self, save_to_file=False, delete_file=False):
            """
            Clears the chain and optionally saves the blockchain to a file and/or deletes the file.

            Parameters:
            - save_to_file (bool): If True, saves the blockchain to a file. Default is False.
            - delete_file (bool): If True, deletes the file containing the blockchain. Default is False.
            """
            self.chain.clear()
            if save_to_file:
                self.save_blockchain()
            if delete_file:
                if os.path.exists(self.file_path):
                    os.remove(self.file_path)
                else:
                    raise FileNotFoundError(f"File {self.file_path} does not exist!")
    
    def load_blockchain(self) -> bool:
        def initialize_blockchain():
            try:
                self.chain = []
                with open(self.file_path, 'r') as f:
                    blockchain_data = f.read()
                if not blockchain_data:
                    return False
                blockchain_data = json.loads(blockchain_data)
                for index, block in enumerate(blockchain_data):
                    sender = User(block['data']['sender_name'], self)
                    recipient = User(block['data']['recipient_name'], self)
                    data = Data(sender, recipient, block['data']['amount'], block['data']['message'])
                    timestamp = block['timestamp']
                    prev_hash = block['prev_hash'] if index > 0 else ""
                    new_block = Block(data, block['nonce'], prev_hash, block['hash'], timestamp)
                    self.chain.append(new_block)
                if len(self.chain) == 0:
                    return False
                return True
            except FileNotFoundError:
                debug_log(f"Blockchain file not found at {self.file_path}", env="dev")
                return False
            except json.JSONDecodeError:
                debug_log(f"Failed to decode blockchain file at {self.file_path}", env="dev")
                return False
            except Exception as e:
                debug_log(f"Failed to load blockchain: {e}", env="dev")
                traceback.print_exc()
                return False
        
        if initialize_blockchain():
            debug_log(f"Blockchain loaded from {self.file_path}")
            return True
        else:
            debug_log(f"Blockchain is either empty or failed to load from {self.file_path}")
            print(f'Generating the "{self.name}" blockchain...')
            self.create_genesis_block()
            debug_log("Genesis block created!")
            self.save_blockchain()
            return False

    def to_dict(self) ->list:
        return [block.to_dict() for block in self.chain]
    

    # def create_genesis_block(self): # function for creating hash of the genesis block instead of adding "xite" which can cause a lot of errors
    #     prev_hash = ""
    #     # first_hash = "xite"
    #     # first_nonce = 32
    #     data = Data(User("Genesis", self), User("Genesis", self), 0, "Genesis Block")
    #     genesis_block = Block(data)
    #     genesis_block.prev_hash = prev_hash
    #     genesis_block.hash = genesis_block.hash_block()
    #     genesis_block.nonce = self.proof_of_work(genesis_block)
    #     self.chain.append(genesis_block)
    def create_genesis_block(self):
        first_prev_hash = ""
        first_hash = "xite"
        first_nonce = 32
        data = Data(User("Genesis", self), User("Genesis", self), 0, "Genesis Block")
        genesis_block = Block(data, first_nonce)
        genesis_block.prev_hash = first_prev_hash
        genesis_block.hash = first_hash
        self.chain.append(genesis_block)

    def proof_of_work(self, block) -> int:
        # self.update_prev_hash()
        iteration = 0
        while self.valid_proof(block, block.nonce)[0] is False:
            iteration += 1
            block.nonce += 1
            print((self.valid_proof(block, block.nonce)[1] + " HASHES: " + str(iteration)), end="\r")
        return block.nonce

    def valid_proof(self, block: "Block", nonce: int) -> list:
        # if self.update_prev_hash():
        #     debug_log(f"prev_hash of {block} updated in valid_proof!")
        
        if block.prev_hash =="" or None and block.data.sender.name != "Genesis": # because genesis block has no previous hash
            raise IncompleteBlockException("Previous hash is empty while verifying in node.proof_of_work!\n",
                                           f"Block: {block}, Previous hash: SHA256({block.prev_hash} x {block.nonce}) != {block.hash_block()}")

        guess = f"{block.hash}{block.prev_hash}{nonce}".encode() #old
        # guess = f"{block.hash}{nonce}".encode()
        # guess = f"{nonce}{block.merkel_root}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        
        return [guess_hash[:DIFFICULITY] == DIFFICULITY*"0", guess_hash]

    def add_block(self, block: 'Block', auto_load = False) -> bool:
            """
            Adds a block to the blockchain.

            Parameters:
            - block: The block to be added.
            - auto_load: If True, the blockchain will be loaded before adding the block.

            Returns:
            - bool: True if the block is successfully added and mined, False otherwise.
            """
            # block.prev_hash = self.chain[-1].hash
            if auto_load:
                self.load_blockchain()
            if len(self.chain) > 0:
                block.prev_hash = self.chain[-1].hash
                debug_log("Previous hash in add_block: ", block.prev_hash)
            nonce = self.proof_of_work(block) #where actual "mining" happens, it finds the nonce of the block
            block.nonce = nonce
            self.update_merkel_root()
            self.chain.append(block)
            return block.is_mined()

    def verify_block_signature(self, block: "Block") -> bool:
        # debug_log(f"Signature: {block.data.message}, PUBLIC KEY: {block.data.sender.public_key}, PRIVATE KEY: {block.data.sender._private_key}")
        signature = block.data.sender.sign(block.data.message)
        if rsa.verify(block.data.message.encode(), signature, block.data.sender.public_key) == "SHA-256":
            return True
        return False

    def verify_PoW_singlePass(self, block: Block) -> bool:
        # hash = block.hash_block()
        guess = f"{block.hash}{block.prev_hash}{block.nonce}".encode()
        if block.hash == "xite":
            return True

        debug_log("Previous hash in verify_PoW_singlePass: ", block.prev_hash)
        # guess = f"{block.hash}{block.nonce}".encode()
        # guess = f"{block.merkel_root}{block.nonce}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        if guess_hash[:DIFFICULITY] == DIFFICULITY*"0":
            return True
        else:
            return False

    def verify_blockchain(self) -> bool:
        debug_log("VERIFYING BLOCKCHAIN from [verify_PoW_singlePass]:")
        m = True
        i = 1
        for block in range(i, len(self.chain)):
            block = self.chain[i]
            if i > 0 and block.prev_hash != self.chain[i-1].hash: # also verifies the prev_hash of the each block
                return False
            if not self.verify_PoW_singlePass(block):
                m = False
                raise InvalidBlockchainException(f"Hash of block [{i} -- HASH : {self.chain[i].hash}] does not match!\n",
                                                 f"Block: {block}, Previous hash: SHA256({block.prev_hash} x {block.nonce}) != {block.hash_block()}\n",
                                                 f"SHA256({block.hash} x {block.prev_hash} x {block.nonce}) = ({hashlib.sha256(f'{block.hash}{block.prev_hash}{block.nonce})'.encode()).hexdigest()} != {block.hash}")
            else:
                # debug_log(f"BLOCK [{i} ; HASH : {block.hash}] VERIFIED!")
                debug_log(f"BLOCK [{i} ; HASH : {block.hash}] VERIFIED!")
                i += 1
        if m:
            debug_log("BLOCKCHAIN VERIFIED!")
        else:
            debug_log("BLOCKCHAIN NOT VERIFIED!")
        return m

    @staticmethod
    def verify_single_block(blockchain: 'Blockchain', block: 'Block'):
        if not blockchain.verify_PoW_singlePass(block):
                raise InvalidTransactionException("Hash does not match!")
        else:
            debug_log("BLOCK VERIFIED!")

    def save_blockchain(self):
        with open(self.file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent = 4)
    
    # def save_blockchain(self):
    #     debug_log(f"Saving blockchain to: {self.file_path}")  # Add this line
    #     try:
    #         blockchain_data = []
    #         for block in self.chain:
    #             block_data = {
    #                 'prev_hash': block.prev_hash,
    #                 'hash': block.hash,
    #                 'data': {
    #                     'sender_name': block.data.sender.name,
    #                     'recipient_name': block.data.recipient.name,
    #                     'amount': block.data.amount,
    #                     'message': block.data.message
    #                 },
    #                 'nonce': block.nonce
    #             }
    #             blockchain_data.append(block_data)
    #         debug_log(f"Data to be written to file: {blockchain_data}")
    #         abs_file_path = os.path.abspath(self.file_path)
    #         with open(abs_file_path, 'w') as f:
    #             json.dump(blockchain_data, f)
    #         debug_log(f"Data written to file: {abs_file_path}")
    #     except IOError as e:
    #         debug_log(f"IOError: Failed to save blockchain: {e}")
    #     except Exception as e:
    #         debug_log(f"Unexpected error: Failed to save blockchain: {e}")
class User:
    def __init__(self, name: str, blockchain: "Blockchain"):
        self.name = name
        if self.name != "Genesis":
            self.blockchain = blockchain
            self.public_key, self._private_key = rsa.newkeys(512)
            self.wallet = {}
            self.wallet_name = os.path.join("wallets", self.name + "_wallet.json")

            os.makedirs(os.path.dirname(self.wallet_name), exist_ok=True)

            if not os.path.exists(self.wallet_name):
                self.wallet = {"bc_name": self.blockchain.name, "name": self.name, "net_amount": 10, "history": []}
                with open(self.wallet_name, 'w') as f:
                    json.dump(self.wallet, f , indent = 4)
                
                # Giving welcome amount of 10 $XC to the user when they create a wallet
                self.amount = 10

            else:
                if self.name:
                    with open(self.wallet_name, 'r') as f:
                        self.wallet = json.load(f)

                if 'history' not in self.wallet:
                    self.wallet['history'] = []
                
                self.amount = self.get_balance()

    def __str__(self):
        return f"Name: {self.name}, User on the {self.blockchain} Blockchain, User balance: {self.amount}"
    
    def update_balance(self):
        self.amount = self.get_balance()

    def save_to_wallet(self, amount: int, recipient: str, sender: str, message = None):
        # self.amount += amount #might be temporary only, could reset after stopping the script, commenting for now
        transaction = {
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "amount": amount,
                    "sender": sender,
                    "recipient": recipient
                    }  
        # debug_log(f"Transaction: {transaction}")
        
        self.wallet['bc_name'] = self.blockchain.name
        self.wallet['name'] = self.name
        self.wallet['net_amount'] = self.amount
        
        if message:
            transaction['message'] = message
          
        if 'history' in self.wallet:
            self.wallet['history'].append(transaction)
        else:
            self.wallet['history'] = [transaction]


        with open(self.wallet_name, 'w') as f:
            json.dump(self.wallet, f, indent = 4)

        self.update_balance()

    def print_wallet_history(self):
        for transaction in self.wallet.get('history', []):
            debug_log(f"TIMESTAMP: {transaction['timestamp']}, AMOUNT: {transaction['amount']}, SENDER: {transaction['sender']}, NET AMOUNT: {transaction['net_amount']}")

    def get_balance(self):
        balance = 0
        self.update_wallet()
        
        if self.wallet.get('history', KeyError("No history found!")) == []:
            balance = self.wallet.get('net_amount', KeyError("No net amount found in wallet!"))
        else:
            for transaction in self.wallet.get('history', KeyError("No history found!")):
                balance += transaction['amount']

        self.wallet['net_amount'] = balance

        with open(self.wallet_name, 'w') as f:
            json.dump(self.wallet, f, indent = 4)

        # for block in self.blockchain.chain: 
        #     if block.data.sender.name == self.name and block.data.recipient.name != self.name and block.data.sender.name != "XiteNetwork":
        #         balance -= block.data.amount
        #     if block.data.recipient.name == self.name and block.data.sender.name != self.name:
        #         balance += block.data.amount
                
        return balance
    
    # def update_wallet(self):
        ## commenting as it will create new transactions everytime we restart the script, creating duplicate transactions
    #     debug_log('IN UDATE_WALLET FUNCTION')
    #     debug_log(f"Updating wallet for {self.name}")
    #     for block in self.blockchain.chain: 
    #         if block.data.sender.name == self.name and block.data.recipient.name != self.name:
    #             # balance -= block.data.amount
    #             self.save_to_wallet(-block.data.amount, block.data.recipient.name, block.data.sender.name)
    #         if block.data.recipient.name == self.name and block.data.sender.name != self.name:
    #             # balance += block.data.amount
    #             self.save_to_wallet(block.data.amount, block.data.recipient.name, block.data.sender.name)

    def update_wallet(self):
        with open(self.wallet_name, 'r') as f:
            self.wallet = json.load(f)

    def sign(self, message: str) -> bytes:
        signature = rsa.sign(message.encode(), self._private_key, "SHA-256")
        return signature
    
    # def to_dict(self) ->list:
    #     return [block.to_dict() for block in self.chain]

    def transaction(self, recipient: "User", amount: int, save=True, return_block=False, return_data=False, reward: int = 0, check_balance: bool = True) -> Data | dict | None:
        """
        Executes a transaction between two users.

        Args:
            recipient (User): The recipient of the transaction.
            amount (int): The amount of XITE to be transferred.
            save (bool, optional): Whether to save the transaction to the blockchain. Defaults to True.
            return_block (bool, optional): Whether to return the new block as a dictionary. Defaults to False.
            return_data (bool, optional): Whether to return the transaction data. Defaults to False.
            reward (int, optional): The reward amount for mining a block. Defaults to 0.

        Returns:
            Data or dict or None: The transaction data or the new block as a dictionary, depending on the specified return type.

        Raises:
            InvalidTransactionException: If the sender has insufficient balance.

        """
        self.update_balance()
        self.blockchain.update_prev_hash()
        if reward > 0:
            self.amount += reward
            self.message = f"{self.name} mined a block and got {reward} $XITE"
            transaction_data = Data(self, recipient, amount, self.message)
            prev_hash = self.blockchain.chain[-1].hash
            new_block = Block(transaction_data)
            new_block.prev_hash = prev_hash
            # debug_log("prev_hash in User.transaction: ", prev_hash)
            if save:
                if self.blockchain.verify_block_signature(new_block):
                    self.blockchain.add_block(new_block)
                    debug_log("Transaction was verified! ")
                else:
                    debug_log("Transaction was not able to be verified!")
            if return_data:
                return transaction_data
            if return_block:
                return new_block.to_dict()
        if check_balance:
            if self.amount < amount:
                debug_log("Insufficient balance")
                raise InvalidTransactionException(f"Insufficient balance for {self.name}")

        # recipient.amount += amount
        # recipient.save_to_wallet(amount, recipient.name, self.name)
        # self.save_to_wallet(-amount, "self", "self")
        # self.amount -= amount
        # debug_log(f"{user1.name} gave {user2.name} {amount} $XITE")
        self.message = f"{self.name} gave {recipient.name} {amount} $XITE"  # this message has to be signed
        transaction_data = Data(self, recipient, amount, self.message)
        # transaction_hash = hashlib.sha256(self.message.encode()).hexdigest()

        new_block = Block(transaction_data) #* gives current transaction data's hash to the current block but add_block() method automatically gives the hash of the current block to the next block. (or current block has previous block's hash)
        prev_hash = self.blockchain.chain[-1].hash
        new_block.prev_hash = prev_hash
        new_block.hash = new_block.hash_block()
        if save:
            if self.blockchain.verify_block_signature(new_block):
                self.blockchain.add_block(new_block)
                debug_log("Transaction was verified! ")
            else:
                debug_log("Transaction was not able to be verified!")
        if return_data:
            return transaction_data
        if return_block:
            return new_block.to_dict()

    @staticmethod    
    def update_wallet_through_blockchain(user, reset: bool = False):
        if reset:
            user.wallet['net_amount'] = 10
            user.wallet['history'] = []
            with open(user.wallet_name, 'w') as f:
                json.dump(user.wallet, f, indent = 4)
            user.update_wallet()
        for block in user.blockchain.chain:
            if block.data.sender.name == user.name and block.data.recipient.name != user.name:
                user.save_to_wallet(-block.data.amount, block.data.recipient.name, block.data.sender.name)
            if block.data.recipient.name == user.name and block.data.sender.name != user.name:
                user.save_to_wallet(block.data.amount, block.data.recipient.name, block.data.sender.name)
            

        
class InvalidTransactionException(Exception):
    pass

class InvalidBlockchainException(Exception):
    pass

class IncompleteBlockException(Exception):
    pass


if __name__ == "__main__":
    pass

#TODO:(done) user makes a seperate private and public key for each transaction, then the transaction has a signature to it. that signature was only created by the user. the next block checks the transaction by verifying by public key

#TODO: implement server based or peer to peer based blockchain network, which verifies the most work done in a blockchain and only the most work done blockchain is accepted.
#TODO: implement a wallet class to store the public and private keys of the user.

#TODO: store the blockchain in a file of sort, and make a user system where i (a user) can log into my wallet and mine blocks to somehow gather $XITE (fake money for now as an int somewhere)
#TODO:(done) make it so that $XITE cant just be given to a user, like how we are giving currently to user objects. 

#MINING IMPLEMENTATION:
# For normal transaction anybody can do a transaction and it will be added to a block.
# A function will be recurring once every 1-2 min and hashing the transactions into the blockchain with each block
# for using that function to hash blocks into the blockchain, there will be a reward!
    

#MINING IMPLEMENTATION (SOCKET:
    # Each transaction when occurs is broadcasted to other users.

    # For mining: Collect transactions and then find the proof of work for that block (DIFFICULITY amount of zeroes 
    # at the beginning of the hash), when you find the POW then you get a BLOCK_REWARD amount of coins. Users are insentivised 
    # to include as much transactions as possible as they will get transaction fees as reward from each transaction. if there are 
    # no transcation (dead blockchain) in each block then the user mining that block will get less reward as there will be no transaction 
    # fees to be collected from each transaction

"""
When a new transaction occurs, it gets broadcast, each user listens for transactions, then a new block is made by that user after a certain amount of time(BLOCK_TIME).
The amount of transactions that were listened by the user gets added to the block and then the proof of work for that block is found. when found the 





"""