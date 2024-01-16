from xite_network.xiteuser import XiteUser
from xitelib.node import Blockchain

def create_user():
    if input("Does user already exist? [y/n]") == "y":
        try:
            bc_name = str(input("Blockchain name: "))
            bc = Blockchain(bc_name)
            username = str(input("Enter username: "))
            password = str(input("Enter password: "))
            XiteUser(username, password, bc)
        except Exception as e:
            print(f"Error occured: {e}")
    else:
        username = str(input("Enter username: "))
        password = str(input("Enter password: "))
        bc_name = str(input("Enter Blockchain name: "))
        bc = Blockchain(bc_name)
        XiteUser(username, password, bc)