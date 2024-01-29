import xitelib.node as node
from termcolor import colored

tb = node.Blockchain("tb1")
tb.clear()
# tb.create_genesis_block()

tb.load_blockchain()
# tb.verify_blockchain()

user = node.User("user", tb)

data = node.Data(user, user, 0, "message message 123")
block = node.Block(data)

user.transaction(user, 0)
user.transaction(user, 0)


# tb.save_blockchain()

print(tb)

hash1 = tb.chain[1].hash_block()
hash2 = tb.chain[2].hash_block()
print("--------------------")
print("hash 1" + hash1)
print("hash 2" + hash2)
# print(block.hash)
# print(block.hash)
# tb.create_genesis_block()
# user.transaction(user, 0)
# print(tb)
# try:
#     # if tb.verify_PoW_singlePass(tb.chain[1]):
#     if tb.verify_blockchain():
#         print(colored("PoW verified successfully", 'green'))
# except Exception as e:
#     print(colored(f"PoW verification failed: {e}", 'red'))

# tb.save_blockchain()