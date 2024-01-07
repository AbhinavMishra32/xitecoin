from node import Block, Blockchain, User, Data

new_blockchain = Blockchain("new_blockchain_1")
new_blockchain.create_genesis_block()
# if not new_blockchain.load_blockchain():
#     raise ValueError("Failed to load blockchain!")
# else:
#     new_blockchain.verify_blockchain()

Banti = User("Banti", new_blockchain)
Rinki = User("Rinki", new_blockchain)

# new_blockchain.create_genesis_block()
print(new_blockchain)
data = Banti.transaction(Rinki, 0)

print("PROOF:")
if new_blockchain.valid_proof(new_blockchain[0], new_blockchain[0].nonce):
    print("Valid proof")

print("----------")
print(data)
print([Banti.amount, Rinki.amount])
print(new_blockchain)