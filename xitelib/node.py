# XiteCoin ($XITE), 2024
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
import rsa
# from settings.settings import Settings
import time
import os


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
    def __init__(self, data: Data, nonce: int = 0, prev_hash = None, hash = None, timestamp = None):
        self.merkel_root = ""
        if prev_hash is None:
            self.prev_hash = ""
        else:
            self.prev_hash = prev_hash
        if timestamp is None:
            self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # string
        else:
            self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        if hash is None:
            self.hash = self.hash_block()
        else:
            self.hash = hash

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
        if HASH_WITHOUT_TIMESTAMP:
            data_string = f"{self.data.sender.name}{self.data.amount}{self.data.recipient.name}{self.data.message}{self.prev_hash}{self.merkel_root})"
            # print("Data string: ", data_string)
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
        self.file_path = f"{self.name}.json"
        
        if init_load:
            self.load_blockchain()


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
                        blockchain_data = json.load(f)
                for block in blockchain_data:
                    sender = User(block['data']['sender_name'], self)
                    recipient = User(block['data']['recipient_name'], self)
                    data = Data(sender, recipient, block['data']['amount'], block['data']['message'])
                    timestamp = block['timestamp']
                    # new_block = Block(block['prev_hash'], block['hash'], data, block['nonce'])
                    new_block = Block(data, block['nonce'], timestamp = timestamp)
                    new_block.hash = new_block.hash_block()
                    if len(self.chain) > 0:
                        new_block.prev_hash = self.chain[-1].hash
                    self.chain.append(new_block)
                    # print(f"LOADED BLOCK: {block}")
                if len(self.chain) == 0:
                    return False
                return True
            except Exception as e:
                print(f"Failed to load blockchain: {e}")
                return False
        if initialize_blockchain():
            print(f"Blockchain loaded from {self.file_path}")
            return True
        else:
            print(f"Blockchain is either empty or failed to load from {self.file_path}")
            for i in range(3):
                for j in range(0, 7):
                    print(f'Generating the "{self.name}" blockchain'+j*".", end="\r")
                    time.sleep(0.25)
                print(" "*60, end="\r")
            print(f'Generating the "{self.name}" blockchain...')
            self.create_genesis_block()
            print("Genesis block created!")
            self.save_blockchain()
            return False
        

    def to_dict(self) ->list:
        return [block.to_dict() for block in self.chain]
    

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
        iteration = 0
        while self.valid_proof(block, block.nonce)[0] is False:
            iteration += 1
            block.nonce += 1
            print((self.valid_proof(block, block.nonce)[1] + " HASHES: " + str(iteration)), end="\r")
        return block.nonce

    def valid_proof(self, block: "Block", nonce: int) -> list:
        # guess = f"{block.hash}{block.prev_hash}{nonce}".encode() #old
        guess = f"{block.hash}{nonce}".encode()
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
            if auto_load:
                self.load_blockchain()
            if len(self.chain) > 0:
                block.prev_hash = self.chain[-1].hash
            nonce = self.proof_of_work(block)
            block.nonce = nonce
            self.update_merkel_root()
            self.chain.append(block)
            return block.is_mined()

    def verify_block_signature(self, block: "Block") -> bool:
        # print(f"Signature: {block.data.message}, PUBLIC KEY: {block.data.sender.public_key}, PRIVATE KEY: {block.data.sender._private_key}")
        signature = block.data.sender.sign(block.data.message)
        if rsa.verify(block.data.message.encode(), signature, block.data.sender.public_key) == "SHA-256":
            return True
        return False

    def verify_PoW_singlePass(self, block: Block) -> bool:
        # hash = block.hash_block()
        # guess = f"{block.hash}{block.prev_hash}{block.nonce}".encode()
        guess = f"{block.hash}{block.nonce}".encode()
        # guess = f"{block.merkel_root}{block.nonce}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        if guess_hash[:DIFFICULITY] == DIFFICULITY*"0":
            return True
        else:
            return False

    def verify_blockchain(self) -> bool:
        print("VERIFYING BLOCKCHAIN from [verify_PoW_singlePass]:")
        m = True
        i = 1
        for block in range(i, len(self.chain)):
            block = self.chain[i]
            if i > 0 and block.prev_hash != self.chain[i-1].hash: # also verifies the prev_hash of the each block
                return False
            if not self.verify_PoW_singlePass(block):
                m = False
                raise InvalidBlockchainException(f"Hash of block [{i} -- HASH : {self.chain[i].hash}] does not match!")
            else:
                # print(f"BLOCK [{i} ; HASH : {block.hash}] VERIFIED!")
                print(f"BLOCK [{i} ; HASH : {block.hash}] VERIFIED!")
                i += 1
        if m:
            print("BLOCKCHAIN VERIFIED!")
        else:
            print("BLOCKCHAIN NOT VERIFIED!")
        return m

    @staticmethod
    def verify_single_block(blockchain: 'Blockchain', block: 'Block'):
        if not blockchain.verify_PoW_singlePass(block):
                raise InvalidTransactionException("Hash does not match!")
        else:
            print("BLOCK VERIFIED!")

    def save_blockchain(self):
        with open(self.file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent = 4)
    
    # def save_blockchain(self):
    #     print(f"Saving blockchain to: {self.file_path}")  # Add this line
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
    #         print(f"Data to be written to file: {blockchain_data}")
    #         abs_file_path = os.path.abspath(self.file_path)
    #         with open(abs_file_path, 'w') as f:
    #             json.dump(blockchain_data, f)
    #         print(f"Data written to file: {abs_file_path}")
    #     except IOError as e:
    #         print(f"IOError: Failed to save blockchain: {e}")
    #     except Exception as e:
    #         print(f"Unexpected error: Failed to save blockchain: {e}")
class User:
    def __init__(self, name: str, blockchain: "Blockchain"):
        self.name = name
        self.blockchain = blockchain
        self.amount = self.get_balance()
        self.public_key, self._private_key = rsa.newkeys(512)

    def __str__(self):
        return f"Name: {self.name}, User on the {self.blockchain} Blockchain, User balance: {self.amount}"

    def get_balance(self):
        balance = 0
        for block in self.blockchain.chain: 
            if block.data.sender.name == self.name:
                balance -= block.data.amount
            if block.data.recipient.name == self.name:
                balance += block.data.amount
        return balance

    def sign(self, message: str) -> bytes:
        signature = rsa.sign(message.encode(), self._private_key, "SHA-256")
        return signature
    
    # def to_dict(self) ->list:
    #     return [block.to_dict() for block in self.chain]

    def transaction(self, recipient: "User", amount: int, save=True, return_block=False, return_data=False, reward: int = 0) -> Data | dict | None:
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
        if reward > 0:
            self.amount += reward
            self.message = f"{self.name} mined a block and got {reward} $XITE"
            transaction_data = Data(self, recipient, amount, self.message)
            new_block = Block(transaction_data)
            if save:
                if self.blockchain.verify_block_signature(new_block):
                    self.blockchain.add_block(new_block)
                    print("Transaction was verified! ")
                else:
                    print("Transaction was not able to be verified!")
            if return_data:
                return transaction_data
            if return_block:
                return new_block.to_dict()
        if self.amount < amount:
            print("Insufficient balance")
            raise InvalidTransactionException(f"Insufficient balance for {self.name}")
        recipient.amount += amount
        self.amount -= amount
        # print(f"{user1.name} gave {user2.name} {amount} $XITE")
        self.message = f"{self.name} gave {recipient.name} {amount} $XITE"  # this message has to be signed
        transaction_data = Data(self, recipient, amount, self.message)
        # transaction_hash = hashlib.sha256(self.message.encode()).hexdigest()

        new_block = Block(transaction_data) #* gives current transaction data's hash to the current block but add_block() method automatically gives the hash of the current block to the next block. (or current block has previous block's hash)
        if save:
            if self.blockchain.verify_block_signature(new_block):
                self.blockchain.add_block(new_block)
                print("Transaction was verified! ")
            else:
                print("Transaction was not able to be verified!")
        if return_data:
            return transaction_data
        if return_block:
            return new_block.to_dict()
            

        
class InvalidTransactionException(Exception):
    pass

class InvalidBlockchainException(Exception):
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