from xitelib.node import Blockchain, Data, User, Block
from settings.settings import Settings
import sqlite3
import json


BLOCKCHAIN_NAME = Settings.BLOCKCHAIN_NAME.value



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
    def save_block(XiteUser, block: Block):

        with open(XiteUser.blockchain.file_path, 'r') as f:
            blockchain_data = json.load(f)
        blockchain_data.append(block.to_dict())
        with open(XiteUser.blockchain.file_path, 'w') as f:
            json.dump(blockchain_data, f, indent=4)

        # print("Block saved successfully, but not mined yet \n THEREFORE VERIFYING INCORRECTLY:")
        # XiteUser.blockchain.verify_blockchain()
        
    
    # @staticmethod
    # def mine_block(json_data, client_user):
    #     sender_user = User(json_data["sender"], client_user.blockchain)
    #     recp_user = User(json_data["data"]["data"]["recipient_name"], client_user.blockchain)
    #     node_data = Data(sender_user, recp_user, int(json_data["data"]["data"]["amount"]), json_data["data"]["data"]["message"], timestamp = json_data["data"]["timestamp"])
    #     node_block = Block(node_data)
    #     XiteUser.save_block(client_user, node_block)
    #     print("Block saved successfully, but not mined yet \n THEREFORE VERIFYING INCORRECTLY:")
    #     Blockchain.verify_single_block(client_user.blockchain, node_block)
    

    @staticmethod
    def mine_block(json_data, blockchain: Blockchain, user: 'User'):
        """makes nonce for a transaction data (mining a block)"""
        block = make_node_block(json_data, user)
        blockchain.load_blockchain()
        blockchain.add_block(block)
        XiteUser.save_block(user, block)


def add_block_to_buffer(buffer_list, block: Block):
    buffer_list.append(block.to_dict())

def make_node_block(json_data, client_user) -> Block:
    sender_user = User(json_data["sender"], client_user.blockchain)
    recp_user = User(json_data["data"]["data"]["recipient_name"], client_user.blockchain)
    node_data = Data(sender_user, recp_user, int(json_data["data"]["data"]["amount"]), json_data["data"]["data"]["message"], timestamp = json_data["data"]["timestamp"])
    node_block = Block(node_data)
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
