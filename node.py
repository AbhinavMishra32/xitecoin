import datetime
import hashlib


class Data:
    def __init__(self, sender, recipient, amount):
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

class Block: # data is words as example
    def __init__(self, hash: str, data: Data):
        self.hash = self.hash_block()
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.data = data

    def hash_block(self):
        data_string = f"{self.data.sender}{self.data.recipient}{self.data.amount}{self.data.timestamp}"
        return hashlib.sha256(self.data.encode()).hexdigest()
