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
    def __init__(self, hash: str, data: Data):
        self.hash = self.hash_block()
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S") #string
        self.data = data

    def hash_block(self):
        data_string = f"{self.data.sender}{self.data.recipient}{self.data.amount}{self.data.timestamp}"
        return hashlib.sha256(self.data.encode()).hexdigest()

class Blockchain:
    def __init__(self, block: 'Block'):
        self.chain = []

    def proof_of_work(self, block):
        proof = 0
        while self.valid_proof(block, proof) is False:
            proof +=1
        return proof
    
    def valid_proof(self, block, proof):
        guess = f'{block.data}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    def add_block(self, block):
        proof = self.proof_of_work(block)
        block.proof = self.chain.append(block)

class User: 
    def __init__(self, name: str, amount: int):
        self.name = name
        self.amount = amount 
        
    def transaction(self, recipient: 'User', amount: int) -> Data:
        if self.amount < amount: 
            print("Insufficient balance")
            return
        recipient.amount += amount
        self.amount -= amount
        # print(f"{user1.name} gave {user2.name} {amount} $XITE")
        message = f"{self.name} gave {recipient.name} {amount} $XITE"
        transaction_data = Data(self, recipient, amount, message)
        new_block = Block()
        return transaction_data
    

Jason = User("Jason", 200)
Mones = User("Mones", 825)

print(Jason.transaction(Mones, 100))