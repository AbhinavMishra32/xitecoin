# XITECOIN (Technical Demo)

XiteCoin is a unique blockchain-based cryptocurrency that uses a bootstrap server architecture instead of the traditional peer-to-peer (P2P) approach. This README provides an overview of how XiteCoin works, its protocol, and how you can get started with the project.

## How XiteCoin Works

Every client connects to the Xite server, which broadcasts the presence of each new user to other peers on the network. Users can then send transactions to other users on the network. Transactions can also be sent to usernames that are not currently online. When the user with the username that isn’t on the network creates a new account, they will inherit the balance from the blockchain record.

### XiteCoin Protocol

- **Bootstrap Server:** XiteCoin uses a bootstrap server instead of a traditional P2P solution. The XiteCoin blockchain utilizes Proof of Work (PoW) to maintain the longest blockchain. The Xite Server informs each user making a transaction about the longest blockchain before the transaction occurs, ensuring that everyone operates on a single global blockchain.

- **Security:** The bootstrap server architecture also serves as a safety precaution to prevent client-to-client connections from being hijacked and causing security issues.

- **Broadcasting Actions:** Every transaction or blockchain synchronization action is broadcast to all users. Only the clients that require the action will accept it.

### Extras

- **Genesis Block:** The hash of the genesis block is `"xite"`. This is followed by the first actual transaction with a non-predefined hash, which is generated by the `Block.hash_block` method in the `xitelib.node` module.

- **Local Blockchain:** Local blockchains are downloaded or created as transactions occur in the `LocalBlockchain` folder.

## Getting Started

### Account Creation

An account in the blockchain can be created once the server is active. Account creation is unavailable if the server is offline.

```python3 -m xite_network.xiteclient "<username>" "<password>" [MINE]```

- **MINE:** An optional parameter to enable mining through the client. Setting it to `True` enables the client to mine transactions and earn XiteCoins. Currently, only `True` is supported; `False` will be added later.

After creating an account, you can mine transactions to earn XiteCoins. For instance, you can send 0 XiteCoins to a random person; your client will mine this transaction, and you will receive some XiteCoins as a mining reward. The reward is determined by the Xite server.

### How to Pay Users

After logging into the client, you will see a menu like this:
```
---------XITECOIN---------
1. Check balance
2. Check blockchain length
3. Make transaction
4. Print blockchain
5. Exit
--------------------------
```

Pressing the corresponding number will allow you to perform actions related to payments.

### Starting a Server Locally

The Xite server can be started locally for a sandbox-like experience.

```python3 -m xite_network.xiteserver```

<img width="301" alt="Screenshot 2024-09-05 at 11 19 41 PM" src="https://github.com/user-attachments/assets/26a806f9-77fd-48eb-b3e5-a3a256ae11e0">


The console will dump logs onto the main menu terminal, this can be changed by changing the $ENV to `prod` or `dev`.

Dont be discouraged if you see a ton of errors while sending transactions, its just the logs, the xiteclient engine tries to fix the bugs automatically.
<img width="927" alt="Screenshot 2024-09-05 at 11 30 55 PM" src="https://github.com/user-attachments/assets/0cb70c64-0c44-4106-8818-98923ac98ebe">

The blockchain is in json format, could be further converted to a binary file.

<img width="276" alt="Screenshot 2024-09-05 at 11 35 32 PM" src="https://github.com/user-attachments/assets/532dc89f-34fc-43cd-9cdc-56a48889570f">


This is how the synced blockchain looks, all having the same length and same transaction.
<img width="1058" alt="Screenshot 2024-09-05 at 11 40 29 PM" src="https://github.com/user-attachments/assets/915b939c-5657-4f24-b62c-48a53769c691">


### Contributing
Contributions to XiteCoin are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
