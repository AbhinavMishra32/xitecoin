import xitelib.node as node
from termcolor import colored

tb = node.Blockchain("tb1")
# tb.load_blockchain()
# tb.verify_blockchain()

user = node.User("user", tb)
tb.create_genesis_block()
user.transaction(user, 0)
print(tb)
try:
    # if tb.verify_PoW_singlePass(tb.chain[1]):
    if tb.verify_blockchain():
        print(colored("PoW verified successfully", 'green'))
except Exception as e:
    print(colored(f"PoW verification failed: {e}", 'red'))

tb.save_blockchain()