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
# from multiprocessing import pool
import rsa

class Data:
    def __init__(self, sender: 'User', recipient: 'User', amount: int, message: str):
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.message = message
        self.transaction ={"sender":sender.name, "recipient": recipient.name, "amount": amount, "message": message}

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
        }

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            return json.load(f)


    def hash_block(self) -> str:
        data_string = f"{self.data.sender}{self.data.recipient}{self.data.amount}{self.data.timestamp}"
        return hashlib.sha256(data_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []

    def __getitem__(self, index):
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
        return [block.data.transaction for block in self.chain]
    
    def __call__(self):
        with open("xite_blockchain", 'w') as f:
            json.dump(self.to_dict(), f)

    def create_genesis_block(self):
        first_hash = "xite"
        first_nonce = 32
        data = Data(User("Genesis", 0, self), User("Genesis", 0, self), 0, "Genesis Block") # type: ignore
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

        with open("xite_blockchain.json", 'w') as f:
            json.dump(self.to_dict(), f)

    def verify_block(self, block: "Block") -> bool:
        # print(f"Signature: {block.data.message}, PUBLIC KEY: {block.data.sender.public_key}, PRIVATE KEY: {block.data.sender._private_key}")
        signature = block.data.sender.sign(block.data.message)
        if rsa.verify(block.data.message.encode(), signature, block.data.sender.public_key) == "SHA-256":
            return True
        return False


class User:
    def __init__(self, name: str, amount: int, blockchain: "Blockchain"): # type: ignore
        self.name = name
        self.amount = amount
        self.blockchain = blockchain
        self.public_key, self._private_key = rsa.newkeys(512)

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
            print("Transaction was verified!")
        else: 
            print("Transaction was not able to be verified!")
        return transaction_data



test_blockchain = Blockchain()
test_blockchain.create_genesis_block()
# print(test_blockchain[0])

Jason = User("Jason", 200, test_blockchain)
Mones = User("Mones", 825, test_blockchain)


print(Jason.transaction(Mones, 100))
# print(Jason.amount)
# print(Mones.amount)

print(test_blockchain)

#user makes a seperate private and public key for each transaction, then the transaction has a signature to it. that signature was only created by the user. the next block checks the transaction by verifying by public key

#TODO: implement server based or peer based blockchain network, which verifies the most work done in a blockchain and only the most work done blockchain is accepted.
#TODO: implement a wallet class to store the public and private keys of the user.

#TODO: store the blockchain in a file of sort, and make a user system where i (a user) can log into my wallet and mine blocks to somehow gather $XITE (fake money for now as an int somewhere)
#TODO: make it so that $XITE cant just be given to a user, like how we are giving currently to user objects. 