# p2p_node.py
from flask import Flask, request
import requests
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, this is node!'

def run_server(port):
    app.run(port=port)

def connect_to_peer(port):
    response = requests.get(f'http://localhost:{port}/')
    print(response.text)

if __name__ == '__main__':
    # Start the server in a new thread
    server_thread = threading.Thread(target=run_server, args=(5001,))
    server_thread.start()

    # Connect to a peer
    connect_to_peer(5000)