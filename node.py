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
from multiprocessing import pool
import rsa
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives import serialization

class Data:
    def __init__(self, sender: "User", recipient: "User", amount: int, message: str):
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.message = message

    def __str__(self):
        return self.message


class Block:
    def __init__(self, hash: str, data: Data, nonce: int = 0):
        # self.hash = self.hash_block()
        self.hash = hash
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # string
        self.data = data
        self.nonce = nonce

    def __str__(self):
        return f"HASH: {self.hash} TIMESTAMP: {self.timestamp} DATA: {self.data}, NONCE: {self.nonce}"

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
            chain_data += f"INDEX: {block_index} "
            chain_data += str(block)
            chain_data += "\n"
        return chain_data

    def create_genesis_block(self):
        first_hash = "xite"
        first_nonce = 32
        data = Data(None, None, 0, "Genesis Block") # type: ignore
        genesis_block = Block(first_hash, data, first_nonce)
        self.chain.append(genesis_block)

    def proof_of_work(self, block) -> int:
        while self.valid_proof(block, block.nonce)[0] is False:
            # while self.valid_proof(block, block.nonce) is False:
            block.nonce += 1
            print(self.valid_proof(block, block.nonce)[1], end="\r")
        return block.nonce

    def valid_proof(self, block: "Block", nonce: int) -> list:
        guess = f"{block.hash_block()}{nonce}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return [guess_hash[:4] == "00000", guess_hash]
        # return guess_hash[:4] == "00000"

    def add_block(self, block):
        nonce = self.proof_of_work(block)
        block.nonce = nonce
        self.chain.append(block)


class User:
    def __init__(self, name: str, amount: int, blockchain: "Blockchain", public_key: str = None, private_key: str = None):
        self.name = name
        self.amount = amount
        self.blockchain = blockchain
        (self.public_key, self.private_key) = rsa.newkeys(512)

    #public key: Sign(Message, private key) = signature
    #private key: Verify(Message, public key, signature) = True/False
    def sign(self, message: str, data: 'Data') -> str:
        message = f"{data.sender}{data.recipient}{data.amount}{data.timestamp}"
        signature = rsa.sign(message.encode(), self.private_key, "SHA-256")
        return signature

    def transaction(self, recipient: "User", amount: int) -> Data:
        if self.amount < amount:
            print("Insufficient balance")
            return # type: ignore
        recipient.amount += amount
        self.amount -= amount
        # print(f"{user1.name} gave {user2.name} {amount} $XITE")
        message = f"{self.name} gave {recipient.name} {amount} $XITE"
        transaction_data = Data(self, recipient, amount, message)
        transaction_hash = hashlib.sha256(message.encode()).hexdigest()
        new_block = Block(transaction_hash, transaction_data)
        self.blockchain.add_block(new_block)
        return transaction_data


test_blockchain = Blockchain()
test_blockchain.create_genesis_block()
# print(test_blockchain[0])

Jason = User("Jason", 200, test_blockchain)
Mones = User("Mones", 825, test_blockchain)

print(Jason.transaction(Mones, 100))
print(Jason.amount)
print(Mones.amount)

print(test_blockchain)
