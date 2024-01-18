from xite_network.xiteuser import XiteUser  
from xitelib.node import Blockchain

def create_user():
    print("-----Login/Signup-----")
    option = input("Does the user already exist? [y/n]: ")
    if option == "y":
        try:
            bc_name = str(input("Blockchain name: "))
            bc = Blockchain(bc_name)
            username = str(input("Enter username: "))
            password = str(input("Enter password: "))
            XiteUser(username, password, bc).save()
        except Exception as e:
            print(f"Error occured: {e}")
    elif option == "n":
        username = str(input("Enter username: "))
        password = str(input("Enter password: "))
        bc_name = str(input("Enter Blockchain name: "))
        bc = Blockchain(bc_name)
        XiteUser(username, password, bc)
    elif option =="quit":
        return
    else:
        print("Enter the correct option!")
        create_user()

if __name__ == "__main__":
    create_user()