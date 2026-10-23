# PythonCoin Dual Blockchain Consensus System

## Overview
PythonCoin uses a **hybrid blockchain architecture** combining local and MySQL-based blockchain for distributed consensus.

## Architecture

### 1. **Local Blockchain** (In-Memory)
- Fast validation and mining
- Each peer maintains their own copy
- Used for real-time operations
- File: `pythoncoin.py` (Blockchain class)

### 2. **MySQL Blockchain** (Central Consensus)
- Shared database at `adnetwrk` on localhost (can be secupgrade.com)
- All peers sync with this central database
- Source of truth for consensus
- File: `pyqt.py` (MySQLBlockchainManager class)

## How It Works

### Mining Process
```
1. Peer mines block locally
2. Block validated against local blockchain
3. Block saved to LOCAL blockchain
4. Block uploaded to MYSQL blockchain
5. Block broadcast to P2P network
6. Other peers receive block
7. Peers validate and add to LOCAL blockchain
8. Peers sync with MYSQL to verify consensus
```

### Consensus Verification
```
1. Each peer maintains LOCAL blockchain
2. Periodically syncs with MYSQL blockchain
3. If MYSQL has newer blocks → Download and verify
4. If LOCAL has newer blocks → Upload to MYSQL
5. Conflicts resolved by LONGEST VALID CHAIN
```

### Rebuilding Central Database
When the MySQL database needs reconstruction:

```
1. Collect blockchains from all connected peers
2. Verify each peer's blockchain is valid
3. Select the LONGEST valid blockchain
4. Clear MySQL blockchain tables
5. Rebuild MySQL from the longest valid chain
6. All peers re-sync with rebuilt MySQL blockchain
```

## Database Tables

### blockchain_blocks
- Stores all mined blocks
- Primary key: block_index (unique)
- block_hash, previous_hash, merkle_root
- miner_address, timestamp, nonce, difficulty

### blockchain_transactions
- All transactions in blocks
- Links to blocks via block_index
- tx_id (unique), tx_type, sender, signature

### blockchain_tx_inputs
- Transaction inputs (spent UTXOs)
- Links to source transaction

### blockchain_tx_outputs
- Transaction outputs (new UTXOs)
- recipient_address, amount, spent flag

### blockchain_utxo
- Current unspent transaction outputs
- Fast balance lookups
- Updated when blocks added

### blockchain_mempool
- Pending unconfirmed transactions
- Cleared when transaction included in block

### blockchain_peers
- Registry of all active peers
- peer_id, wallet_address, ip_address
- blockchain_height for sync tracking

### blockchain_sync_log
- Audit trail of all sync operations
- peer_id, action, block_index, success

## Key Methods

### MySQLBlockchainManager

#### `save_block_to_mysql(block)`
Saves a mined block to MySQL with all transactions

#### `load_blockchain_from_mysql()`
Downloads entire blockchain from MySQL

#### `sync_local_to_mysql(local_blockchain)`
Synchronizes local blockchain with MySQL:
- If local ahead → Upload new blocks
- If MySQL ahead → Download and verify blocks

#### `rebuild_mysql_from_peers(peer_blockchains)`
Rebuilds MySQL blockchain from peer consensus:
1. Collects all peer blockchains
2. Finds longest valid chain
3. Clears MySQL
4. Rebuilds from longest chain

#### `get_consensus_status()`
Returns sync status of all peers:
- MySQL blockchain height
- Each peer's height
- Number of peers in sync

#### `get_balance_from_mysql(address)`
Fast balance lookup using UTXO set

## Integration Points

### Mining Thread
```python
# After mining a block
if new_block:
    # Add to local blockchain
    self.blockchain.chain.append(new_block)

    # Save to MySQL
    if hasattr(self, 'mysql_blockchain'):
        self.mysql_blockchain.save_block_to_mysql(new_block)

    # Broadcast to network
    self.p2p_manager.broadcast_mined_block(new_block)
```

### P2P Network
```python
# When receiving a block from network
def _handle_new_block(self, message):
    block = reconstruct_block(message['block_data'])

    if block.is_valid():
        # Add to local chain
        self.blockchain.chain.append(block)

        # Sync with MySQL
        if hasattr(self, 'mysql_blockchain'):
            self.mysql_blockchain.sync_local_to_mysql(self.blockchain)
```

### Wallet Initialization
```python
# On startup
self.mysql_blockchain = MySQLBlockchainManager()
self.mysql_blockchain.connect()

# Register this peer
self.mysql_blockchain.register_peer(
    peer_id=self.client_id,
    wallet_address=self.wallet.address,
    ip_address=get_local_ip(),
    port=self.port
)

# Sync blockchain
self.mysql_blockchain.sync_local_to_mysql(self.blockchain)
```

## Consensus Rules

1. **Longest Chain Wins**
   - Chain with most blocks is considered valid
   - Must pass all validation checks

2. **Block Validation**
   - Proof of Work (hash starts with required zeros)
   - Merkle root matches transactions
   - Previous hash links correctly
   - All transactions are valid

3. **Transaction Validation**
   - Valid signatures (except coinbase/genesis)
   - Valid UTXO inputs
   - Input sum ≥ Output sum

4. **Peer Consensus**
   - Majority of peers must agree on blockchain state
   - Rebuilding uses longest valid chain from any peer
   - Invalid chains are rejected

## EnhancedNodeServer (Port 5000)

HTTP API for blockchain queries:

### GET Endpoints
- `/status` - Node status and blockchain height
- `/blockchain` - Current blockchain info
- `/pending_requests` - Pending payment requests

### POST Endpoints
- `/payment_request` - Submit payment request
- `/transaction` - Submit new transaction
- `/sync` - Sync blockchain with peer

## Usage Example

### Setup MySQL Tables
```bash
mysql -u root -p < create_blockchain_tables.sql
```

### Start Mining with Sync
```python
# Mining automatically syncs to MySQL
mining_thread = CryptoMiningThread(
    blockchain=self.blockchain,
    wallet=self.wallet,
    p2p_manager=self.p2p_manager
)
mining_thread.start()
```

### Check Consensus
```python
consensus = mysql_blockchain.get_consensus_status()
print(f"MySQL Height: {consensus['mysql_height']}")
print(f"Peers in sync: {consensus['peers_in_sync']}/{consensus['total_peers']}")
```

### Rebuild from Peers
```python
# Collect peer blockchains (from P2P network)
peer_blockchains = {
    'peer1': peer1_blockchain,
    'peer2': peer2_blockchain,
    'peer3': peer3_blockchain
}

# Rebuild MySQL from consensus
mysql_blockchain.rebuild_mysql_from_peers(peer_blockchains)
```

## Benefits

1. **Fast Local Operations** - Mining and validation use in-memory blockchain
2. **Distributed Consensus** - MySQL provides shared source of truth
3. **Fault Tolerance** - Can rebuild from any valid peer
4. **Verification** - Cross-check local vs MySQL vs other peers
5. **Scalability** - MySQL handles complex queries efficiently
6. **Audit Trail** - Complete history in database

## Security

- MySQL blockchain is read-only to peers (except new blocks)
- Only valid blocks accepted (PoW + validation)
- Longest chain rule prevents forks
- Peer verification prevents malicious blocks
- UTXO tracking prevents double-spending
