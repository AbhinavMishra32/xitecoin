from node import Block, Blockchain, User, Data

new_blockchain = Blockchain("new_blockchain")

Banti = User("Banti", new_blockchain)
Rinki = User("Rinki", new_blockchain)

# new_blockchain.create_genesis_block()
print(new_blockchain)
data = Banti.transaction(Rinki, 100)
print("----------")
print(data)
print(Banti.amount)
print(Rinki.amount)