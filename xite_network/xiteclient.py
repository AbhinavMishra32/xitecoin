import socket
import threading
from xitelib.node import Blockchain
from .xiteuser import XiteUser

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 12345))

def recieve():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == "NICK":
                client.send(nickname.encode())
            else:
                print(message)
        except Exception as e:
            print(f"Error occurred: {e}")
            break

def write():
    while True:
        message = f"{nickname}: {input('')}"
        client.send(message.encode())



if __name__ == "__main__":
    tb = Blockchain("tb")
    client_user = XiteUser("clientname", "clientpass", tb)
    nickname = client_user.username

    recieve_thread = threading.Thread(target = recieve)
    recieve_thread.start()

    write_thread = threading.Thread(target = write)
    write_thread.start()