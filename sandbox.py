from node import Block, Blockchain, User, Data

new_blockchain = Blockchain("new_blockchain_1")
new_blockchain.load_blockchain()
new_blockchain.verify_blockchain()
# new_blockchain.create_genesis_block()
# if not new_blockchain.load_blockchain():
#     raise ValueError("Failed to load blockchain!")
# else:
#     new_blockchain.verify_blockchain()

Banti = User("Banti", new_blockchain)
Rinki = User("Rinki", new_blockchain)
Raju = User("Raju", new_blockchain)

# new_blockchain.create_genesis_block()
# Raju.transaction(Banti, 0)
# Banti.transaction(Rinki, 0)
# data = Rinki.transaction(Raju, 0)
# new_blockchain.save_blockchain()

print(new_blockchain)
# print("PROOF:")
# print(new_blockchain.proof_of_work(new_blockchain[0]))

# if(new_blockchain.proof_of_work(new_blockchain[0])):
#     print()

print("----------")
# print(data)
# print([Banti.amount, Rinki.amount])
# print(new_blockchain)