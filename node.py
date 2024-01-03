from datetime import datetime
import hashlib

# XiteCoin ($XITE), 2024
# Created by Abhinav Mishra

class Data:
    def __init__(self, sender: 'User', recipient: 'User', amount: int, message: str):
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
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S") #string
        self.data = data
        self.nonce = nonce

    def hash_block(self) -> str:
        data_string = f"{self.data.sender}{self.data.recipient}{self.data.amount}{self.data.timestamp}"
        return hashlib.sha256(data_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []

    def create_genesis_block(self):
        first_hash = "xite"
        first_nonce = 32
        data = Data(None, None, 0, "Genesis Block")
        genesis_block = Block(first_hash, data, first_nonce)
        self.chain.append(genesis_block)

    def proof_of_work(self, block) -> int:
        while self.valid_proof(block, block.nonce) is False:
            block.nonce +=1
        return block.nonce

    def valid_proof(self, block: 'Block', nonce: int) -> bool:
        guess = f'{block.hash_block()}{nonce}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def add_block(self, block):
        nonce = self.proof_of_work(block)
        block.nonce = nonce
        self.chain.append(block)

class User: 
    def __init__(self, name: str, amount: int, blockchain: 'Blockchain'):
        self.name = name
        self.amount = amount 
        self.blockchain = blockchain
        
    def transaction(self, recipient: 'User', amount: int) -> Data:
        if self.amount < amount: 
            print("Insufficient balance")
            return
        recipient.amount += amount
        self.amount -= amount
        # print(f"{user1.name} gave {user2.name} {amount} $XITE")
        message = f"{self.name} gave {recipient.name} {amount} $XITE"
        transaction_data = Data(self, recipient, amount, message)
        transaction_hash = hashlib.sha256(message.encode).hexdigest()
        new_block = Block(transaction_hash, transaction_data)
        self.blockchain.add_block(new_block)
        return transaction_data
    

test_blockchain = Blockchain()
test_blockchain.create_genesis_block()

Jason = User("Jason", 200, test_blockchain)
Mones = User("Mones", 825, test_blockchain)

print(Jason.transaction(Mones, 100))