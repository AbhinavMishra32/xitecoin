import socket
import threading


HOST = socket.gethostbyname(socket.gethostname())
PORT = 12345

def start_server(conn, addr):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")
    while True:
        client, address = server.accept()
        threading.Thread(target = handle_client, args =(conn, addr)).start() 

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Recieved from {addr}")
        conn.sendall(data)
    conn.close()

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.sendall(b'Hello, server!')
    data = client.recv(1024)
    print(f"Received from server: {data.decode()}")
    client.close()

if __name__ == "__main__":
    threading.Thread(target=start_server).start()
    threading.Thread(target=start_client).start()