# How does XiteCoin work?

Every client connects to the Xite server which broadcasts each new connecting user about other peers on the network. Then each user can send transactions to other users on the network, they can also send transactions to usernames not on the network currently, when the user with the username which isnt on the network makes a new account, they will inherit the balance from the blockchain record.

### Xitecoin Protocol

- Xitecoin works uniquely -- as in it uses a bootstrap server instead of a p2p solution. The Xitecoin blockchain uses PoW to acquire the largest blockchain, the Xite Server forwards each user making a transaction about the info of the longest blockchain before the transaction occurs, this way everyone should have a single global blockchain.

- The bootstrap server architecture is also a safety precausion so that client-client connection doesnt get hijacked and cause safety issues.

- Every transaction / blockchain-sync 'ACTION' is broadcasted to everyone and only those clients will accept the action that require it.



### Extras
The hash of the genesis block is _"xite"_ which is proceeded by the first actual transaction with a non pre-defined hash that is generated by the `Block.hash_block` method in `xitelib.node` module.
