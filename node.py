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

from datetime import datetime
import hashlib
import json
from os import error
from textwrap import indent
# from multiprocessing import pool
import rsa
import random



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
    def __init__(self, hash: str, data: Data, nonce: int = 0):
        self.hash = hash
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # string
        self.data = data
        self.nonce = nonce

    def __str__(self):
        return f"HASH: {self.hash} TIMESTAMP: {self.timestamp} DATA: {self.data}, NONCE: {self.nonce}"
    
    def to_dict(self):
        return {
            'hash': self.hash,
            'data': self.data.transaction,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
        }

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            return json.load(f)


    def hash_block(self) -> str:
        data_string = f"{self.data.sender}{self.data.recipient}{self.data.amount}{self.data.timestamp}"
        return hashlib.sha256(data_string.encode()).hexdigest()


class Blockchain:
    def __init__(self, name: str):
        self.chain: list = []
        self.name: str = name
        try:
            with open(f"{self.name}.json", 'r') as f:
                blockchain_data = json.load(f)
            if(self.verify_blockchain()):
                for block in blockchain_data:
                    sender = User(block['data']['sender_name'], self)
                    recipient = User(block['data']['recipient_name'], self)
                    data = Data(sender, recipient, block['data']['amount'], block['data']['message'])
                    new_block = Block(block['hash'], data, block['nonce'])
                    self.chain.append(new_block)
        except:
            first_hash = "xite"
            first_nonce = 32
            data = Data(User("Genesis", self), User("Genesis", self), 0, "Genesis Block") # type: ignore
            genesis_block = Block(first_hash, data, first_nonce)
            self.add_block(genesis_block)

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
    
    def to_dict(self) ->list:
        return [block.to_dict() for block in self.chain]
    

    def create_genesis_block(self):
        first_hash = "xite"
        first_nonce = 32
        data = Data(User("Genesis", self), User("Genesis", self), 0, "Genesis Block") # type: ignore
        genesis_block = Block(first_hash, data, first_nonce)
        self.chain.append(genesis_block)

    def proof_of_work(self, block) -> int:
        iteration = 0
        while self.valid_proof(block, block.nonce)[0] is False:
            # while self.valid_proof(block, block.nonce) is False:
            iteration += 1
            block.nonce += 1
            print((self.valid_proof(block, block.nonce)[1] + " HASHES: " + str(iteration)), end="\r")
        return block.nonce

    def valid_proof(self, block: "Block", nonce: int) -> list:
        difficulity = "0000"
        guess = f"{block.hash_block()}{nonce}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return [guess_hash[:int(len(difficulity))] == difficulity, guess_hash]
    
    def add_block(self, block):
        nonce = self.proof_of_work(block)
        block.nonce = nonce
        self.chain.append(block)
        if(self.verify_blockchain):
            with open(f"{self.name}.json", 'w') as f:
                json.dump(self.to_dict(), f, indent = 4)
                print("Blockchain Verified!")
        else:
            print("Blockchain incorrect!")

    def verify_block(self, block: "Block") -> bool:
        # print(f"Signature: {block.data.message}, PUBLIC KEY: {block.data.sender.public_key}, PRIVATE KEY: {block.data.sender._private_key}")
        signature = block.data.sender.sign(block.data.message)
        if rsa.verify(block.data.message.encode(), signature, block.data.sender.public_key) == "SHA-256":
            return True
        return False
    
    def verify_blockchain(self) -> bool:
        for i in range(1, len(self.chain)):
            if self.valid_proof(self[i-1], self[i-1].nonce)[1] != self[i].hash:
                raise ValueError("Invalid blockchain: hash does not match!")
                return False
        print("BLOCKCHAIN VERIFIED AND OPENED!")
        return True


class User:
    def __init__(self, name: str, blockchain: "Blockchain"):
        self.name = name
        self.blockchain = blockchain
        self.amount = self.get_balance()
        self.public_key, self._private_key = rsa.newkeys(512)

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
        transaction_hash = hashlib.sha256(self.message.encode()).hexdigest()
        new_block = Block(transaction_hash, transaction_data)
        if self.blockchain.verify_block(new_block):
            self.blockchain.add_block(new_block)
            print("Transaction was verified! ")
        else: 
            print("Transaction was not able to be verified!")
        return transaction_data


if __name__ == "__main__":
    xite_blockchain = Blockchain("xite_blockchain")
    # test_blockchain.create_genesis_block()
    # print(test_blockchain[0])

    # Jason = User("Jason", 200, test_blockchain)
    # Mones = User("Mones", 825, test_blockchain)
    # Jordi = User("Jordi", 10000, test_blockchain)


    # print(Jason.transaction(Mones, 1000))
    # print(Jordi.transaction(Jason, 2632))
    # List of user names
    users = ["Alice", "Bob", "Charlie", "Dave", "Eve"]

    # Generate random transactions
    # for _ in range(10):
    #     sender = random.choice(users)
    #     recipient = random.choice(users)
    #     amount1 = random.randint(1, 1000)
    #     amount2 = random.randint(1, 1000)
    #     amount3 = random.randint(1, 300)
    #     sender_user = User(sender, amount1, test_blockchain)
    #     recipient_user = User(recipient, amount2, test_blockchain)
    #     sender_user.transaction(recipient_user, amount3)

    # print(Jason.amount)
    # print(Mones.amount)
    Alice = User("Alice", xite_blockchain)
    Bob = User("Bob", xite_blockchain)
    Charlie = User("Charlie", xite_blockchain)
    Dave = User("Dave", xite_blockchain)
    Eve = User("Eve", xite_blockchain)

    print([Alice.amount, Bob.amount, Charlie.amount, Dave.amount, Eve.amount])

    print(xite_blockchain)

#user makes a seperate private and public key for each transaction, then the transaction has a signature to it. that signature was only created by the user. the next block checks the transaction by verifying by public key

#TODO: implement server based or peer based blockchain network, which verifies the most work done in a blockchain and only the most work done blockchain is accepted.
#TODO: implement a wallet class to store the public and private keys of the user.

#TODO: store the blockchain in a file of sort, and make a user system where i (a user) can log into my wallet and mine blocks to somehow gather $XITE (fake money for now as an int somewhere)
#TODO: make it so that $XITE cant just be given to a user, like how we are giving currently to user objects. 