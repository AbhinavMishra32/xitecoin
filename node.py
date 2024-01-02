from datetime import datetime
import hashlib

# XiteCoin ($XITE), 2024
# Created by Abhinav Mishra

class Data:
    def __init__(self, sender: 'User', recipient: 'User', amount: int):
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.sender = sender
        self.recipient = recipient

class Block:
    def __init__(self, hash: str, data: Data):
        self.hash = self.hash_block()
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S") #string
        self.data = data

    def hash_block(self):
        data_string = f"{self.data.sender}{self.data.recipient}{self.data.amount}{self.data.timestamp}"
        return hashlib.sha256(self.data.encode()).hexdigest()

# one user can send another use a transaction, a user has a wallet(total money)

class User: 
    def __init__(self, name: str, amount: int, recipient):
        self.name = name
        self.amount = amount 
        
    def transaction(self, recipient: 'User', amount: int) -> Data:
        if self.amoutn < amount: 
            print("Insufficient balance")
            return
        recipient.amount += amount
        # print(f"{user1.name} gave {user2.name} {amount} $XITE")
        self.message = f"{self.name} gave {recipient.name} {amount} $XITE"
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        return 