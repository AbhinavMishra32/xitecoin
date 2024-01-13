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
#*
#*

from datetime import datetime
import hashlib
import json
import rsa
import random

DIFFICULITY = 4
HASH_WITHOUT_TIMESTAMP = True #for static hashing, wont change with different time (used for testing hashes of the blockchain comparing other changing factors than just time)
BLOCK_REWARD = 2.5

class Data:
    def __init__(self, sender: 'User', recipient: 'User', amount: int, message: str):
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.message = message
        self.transaction = {"sender_name":sender.name, "recipient_name": recipient.name, "amount": amount, "message": message}

    def __str__(self):
        return self.message


class Block:
    def __init__(self, data: Data, nonce: int = 0):
        self.prev_hash = ""
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # string
        self.data = data
        self.nonce = nonce
        self.hash = self.hash_block()

    def __str__(self):
        return f"HASH: {self.hash} | PREV_HASH: {self.prev_hash} TIMESTAMP: {self.timestamp} DATA: {self.data}, NONCE: {self.nonce}"

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
            data_string = f"{self.data.sender.name}{self.data.amount}{self.data.recipient.name}{self.data.message}{self.prev_hash}"
            # print("Data string: ", data_string)
            return hashlib.sha256(data_string.encode()).hexdigest()
        else:
            data_string = f"{self.data.sender.name}{self.data.amount}{self.data.recipient.name}{self.data.message}{self.prev_hash}{self.data.timestamp}"
            return hashlib.sha256(data_string.encode()).hexdigest()
        
class Blockchain:
    def __init__(self, name: str):
        self.chain: list[Block] = []
        self.name: str = name
        self.file_path = f"{self.name}.json"

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
    
    def load_blockchain(self) -> bool:
        try:
            self.chain = []
            with open(self.file_path, 'r') as f:
                    blockchain_data = json.load(f)
            for block in blockchain_data:
                sender = User(block['data']['sender_name'], self)
                recipient = User(block['data']['recipient_name'], self)
                data = Data(sender, recipient, block['data']['amount'], block['data']['message'])
                # new_block = Block(block['prev_hash'], block['hash'], data, block['nonce'])
                new_block = Block(data, block['nonce'])
                new_block.hash = new_block.hash_block()
                if len(self.chain) > 0:
                    new_block.prev_hash = self.chain[-1].hash
                self.chain.append(new_block)
                # print(f"LOADED BLOCK: {block}")
            return True
        except Exception as e:
            print(f"Failed to load blockchain: {e}")
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
        guess = f"{block.hash}{nonce}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        
        return [guess_hash[:DIFFICULITY] == DIFFICULITY*"0", guess_hash]

    def add_block(self, block: 'Block'):
        if len(self.chain) > 0:
            block.prev_hash = self.chain[-1].hash
        nonce = self.proof_of_work(block)
        block.nonce = nonce
        self.chain.append(block)

    def verify_block(self, block: "Block") -> bool:
        # print(f"Signature: {block.data.message}, PUBLIC KEY: {block.data.sender.public_key}, PRIVATE KEY: {block.data.sender._private_key}")
        signature = block.data.sender.sign(block.data.message)
        if rsa.verify(block.data.message.encode(), signature, block.data.sender.public_key) == "SHA-256":
            return True
        return False

    def verify_PoW_singlePass(self, block) -> bool:
        guess = f"{block.hash}{block.nonce}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        if guess_hash[:DIFFICULITY] == DIFFICULITY*"0":
            return True
        else:
            return False


    def verify_blockchain(self):
        i = 0
        print("VERIFYING BLOCKCHAIN: ")
        for block in range(1, len(self.chain)):
            if not self.verify_PoW_singlePass(self.chain[block]):
                raise ValueError("Invalid blockchain: hash does not match!")
            else:
                print(f"BLOCK [{i}] VERIFIED!")
                i += 1

    def save_blockchain(self):
        with open(self.file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent = 4)


class User:
    def __init__(self, name: str, blockchain: "Blockchain"):
        self.name = name
        self.blockchain = blockchain
        self.amount = self.get_balance()
        self.public_key, self._private_key = rsa.newkeys(512)

    def __str__(self):
        return f"Name: {self.name}, User on the {self.blockchain} Blockchain, User balance at time of transaction: {self.amount}"

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

    def transaction(self, recipient: "User", amount: int) -> Data:
        """
        Returns Data and also adds new Block to the Blockchain automatically.
        """
        if self.amount < amount:
            print("Insufficient balance")
            return # type: ignore
        recipient.amount += amount
        self.amount -= amount
        # print(f"{user1.name} gave {user2.name} {amount} $XITE")
        self.message = f"{self.name} gave {recipient.name} {amount} $XITE" #this message has to be signed
        transaction_data = Data(self, recipient, amount, self.message)
        # transaction_hash = hashlib.sha256(self.message.encode()).hexdigest()
        new_block = Block(transaction_data) #* gives current transaction data's hash to the current block but add_block() method automatically gives the hash of the current block to the next block. (or current block has previous block's hash)
        if self.blockchain.verify_block(new_block):
            self.blockchain.add_block(new_block)
            print("Transaction was verified! ")
        else: 
            print("Transaction was not able to be verified!")
        return transaction_data

    def mine_block(self):
        pass
        # User this later for listening and broadcasting the blocks after mining from socket
        

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