from node import Block, Blockchain, User, Data
new_blockchain = Blockchain("new_blockchain_1")
new_blockchain.load_blockchain()
new_blockchain.verify_blockchain()

Banti = User("Banti", new_blockchain)
Rinki = User("Rinki", new_blockchain)
Raju = User("Raju", new_blockchain)

Banti.transaction(Rinki, 0)
Raju.transaction(Banti,0)
new_blockchain.save_blockchain()

print(new_blockchain)
