from xitelib.node import Blockchain, Data, User, Block
from settings.settings import Settings
import sqlite3
import json
from termcolor import colored
import threading
BLOCKCHAIN_NAME = Settings.BLOCKCHAIN_NAME.value

class BlockMiningFailedException(Exception):
    pass

class XiteUser(User):
    '''
    this class is used to create a user and store it in the database
    '''
    def __init__(self, username: str, password: str, blockchain: Blockchain):
        super().__init__(username, blockchain)
        self.username = username
        self.password = password
        self.blockchain = blockchain

    def login(self, username: str, password: str):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()

        conn.close()

        if result is None:
            print("Username not found")
            return False
        stored_password = result[0]
        if password == stored_password:
            print("Login successful")
            return True
        else:
            print("Incorrect password")
            return False


    def save(self) -> bool:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                    )''')
        
        c.execute("SELECT username FROM users WHERE username = ?", (self.username,))
        result = c.fetchone()

        if result is not None:
            print("Username already exists")
            return False
        
        c.execute('''
            INSERT INTO users (username, password) VALUES (?,?)''', (self.username, self.password))
        
        conn.commit()
        conn.close()
        print("User created successfully")
        return True
    
    def nwtransaction(self, recipient: User, amount: int, save: bool = True, return_block: bool = False, return_data: bool = False):
        return super().transaction(recipient, amount, save, return_block=return_block, return_data=return_data)
    
    def user_exists(self, username) -> bool:
        # blockchain = Blockchain(self.blockchain.name)
        # blockchain.load_blockchain()
        with open(self.blockchain.file_path, 'r') as f:
            blockchain_data = json.load(f)
        for block in blockchain_data:
            data = block['data']
            if data['sender_name'] == username or data['recipient_name'] == username:
                return True
        return False

    @staticmethod
    def mine_block(json_data: dict, user: 'XiteUser') -> Block:
        """Create a new block and add it to the blockchain."""
        
        block = make_node_block(json_data, user)
        if not user.blockchain.add_block(block):
            print(colored("Block mined successfully!", 'light_green'))
            return block
        else:
            raise BlockMiningFailedException("Failed to add block to blockchain")

    @staticmethod
    def save_block(user: 'XiteUser', block: Block):
        """Save a block."""
        print(colored("Saving block", 'light_green'))
        try:         
            with open(user.blockchain.file_path, 'r') as f:
                blockchain_data = json.load(f)
            blockchain_data.append(block.to_dict())
            with open(user.blockchain.file_path, 'w') as f:
                json.dump(blockchain_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error occured while saving block: {e}")
            return False

    @staticmethod
    def verify_blockchain(user: 'XiteUser'):
        from xite_network.xiteclient import synchronize_blockchain #circular import
        """Verify the blockchain."""
        print(colored("Verifying blockchain", 'yellow'))
        if not user.blockchain.verify_blockchain():
            print(colored("Blockchain verification failed", 'light_red'))
            print("Requesting latest blockchain from other nodes")
            synchronize_blockchain(user)
        else:
            print(colored("Blockchain verified successfully", 'light_green'))

    @staticmethod
    def process_mined_block(un_mined_block: dict, user: 'XiteUser', use_multithreading: bool = False):
        """Process a mined block."""
        # for un_mined_block in un_mined_block_list:
        def mine_and_process_block(json_data: dict):
            print("Mining block...")
            block = make_node_block(json_data, user)
            try:
                print("--------------------")
                mined_block = XiteUser.mine_block(un_mined_block, user)
                print(colored(f"Block {mined_block} mined successfully", 'light_green'))
                print("--------------------")
                XiteUser.verify_blockchain(user)
                XiteUser.save_block(user, mined_block)
            except BlockMiningFailedException:
                print(colored("Block mining failed", 'light_red'))

        if use_multithreading:
            # Start a new thread that will mine and process the block
            threading.Thread(target=mine_and_process_block, args=un_mined_block).start()
        else:
            # Mine and process the block in the current thread
            mine_and_process_block(un_mined_block)



def add_block_to_buffer(buffer_list, block: Block):
    buffer_list.append(block.to_dict())

def make_node_block(json_data: dict, client_user, prev_hash = None, hash = None) -> Block:

    sender = json_data["data"]["data"].get("sender_name")
    if sender is None:
        raise ValueError("Missing 'sender_name' in json_data")
    sender_user = User(sender, client_user.blockchain)
    recipient_name = json_data["data"]["data"].get("recipient_name")
    if recipient_name is None:
        raise ValueError("Missing 'recipient_name' in json_data")
    recp_user = User(recipient_name, client_user.blockchain)
    amount = int(json_data["data"]["data"].get("amount"))
    message = json_data["data"]["data"].get("message")
    timestamp = json_data["data"].get("timestamp")
    node_data = Data(sender_user, recp_user, amount, message, timestamp=timestamp)
    nonce = int(json_data["data"].get("nonce"))
    node_block = Block(node_data, nonce, prev_hash, hash)
    return node_block



def create_user() -> XiteUser | None:
    print("-----Login/Signup-----")
    option = input("Does the user already exist? [y/n]: ")
    if option == "y":
        try:
            bc_name = str(input("Blockchain name: "))
            bc = Blockchain(bc_name)
            username = str(input("Enter username: "))
            password = str(input("Enter password: "))
            XiteUser(username, password, bc).save()
            return XiteUser(username, password, bc)
        except Exception as e:
            print(f"Error occured: {e}")
    elif option == "n":
        username = str(input("Enter username: "))
        password = str(input("Enter password: "))
        bc_name = str(input("Enter Blockchain name: "))
        bc = Blockchain(bc_name)
        XiteUser(username, password, bc).save()
    elif option =="quit":
        return 
    else:
        print("Enter the correct option!")
        create_user()


    def __repr__(self):
        return f"XiteUser({self.username}, {self.password}, {self.blockchain})"

    @staticmethod
    def delete(username: str) -> bool:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute("SELECT username FROM users WHERE username = ?", (username,))
        result = c.fetchone()

        if result is None:
            print("Username not found")
            return False

        c.execute("DELETE FROM users WHERE username = ?", (username,))

        conn.commit()
        conn.close()

        print("User deleted successfully")
        return True
    

def print_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    rows = c.fetchall()

    for row in rows:
        print(row)

    conn.close()


if __name__ == "__main__":
    # testUser = XiteUser("abhisnsdfsdf123", "myasp124124", Blockchain("testsetestset"))
    # print(testUser.blockchain)
    # print_database()
    # print(XiteUser("Abhinav122", "adfs", Blockchain("testsetestset")))
    # print_database()
    pass
