from node import Block, Blockchain, User, Data
import random
new_blockchain = Blockchain("new_blockchain_1")
new_blockchain.load_blockchain()
new_blockchain.verify_blockchain()

Banti = User("Banti", new_blockchain)
Rinki = User("Rinki", new_blockchain)
Raju = User("Raju", new_blockchain)

# new_blockchain.create_genesis_block()
# Raju.transaction(Banti, 0)
# Banti.transaction(Rinki, 0)
# data = Rinki.transaction(Raju, 0)
# new_blockchain.save_blockchain()



users = ["Alice", "Bob", "Charlie", "Dave", "Eve"]

for _ in range(10):
    sender = random.choice(users)
    recipient = random.choice(users)
    sender_user = User(sender, new_blockchain)
    recipient_user = User(recipient, new_blockchain)
    sender_user.transaction(recipient_user, 0)

new_blockchain.save_blockchain()

print(new_blockchain)
