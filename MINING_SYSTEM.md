# PythonCoin Mining System

## Overview
PythonCoin implements a Bitcoin-style Proof-of-Work mining system with dynamic difficulty adjustment and block reward halving.

## Mining Rewards

### Block Reward Halving
Mining rewards follow Bitcoin's halving schedule:

```python
Initial Reward: 50 PYC
Halving Interval: 210,000 blocks

Block Range          Reward
0 - 209,999         50.0 PYC
210,000 - 419,999   25.0 PYC
420,000 - 629,999   12.5 PYC
630,000 - 839,999   6.25 PYC
...and so on

Minimum Reward: 0.00000001 PYC (1 satoshi)
```

### Reward Calculation
```python
def calculate_block_reward(self):
    initial_reward = 50.0
    halving_interval = 210000
    halvings = self.index // halving_interval
    reward = initial_reward / (2 ** halvings)
    return max(reward, 0.00000001)
```

### Total Supply Cap
With halving, total supply approaches (but never exceeds):
```
Total Supply = 210,000 × 50 × 2 = 21,000,000 PYC
```

## Dynamic Difficulty Adjustment

### How It Works
The difficulty automatically adjusts every 10 blocks to maintain a target block time.

```python
Target Block Time: 60 seconds (1 minute)
Adjustment Interval: 10 blocks
Max Adjustment Factor: 4x per period
```

### Adjustment Algorithm
```python
class DifficultyAdjustment:
    def calculate_next_difficulty(self):
        # Get last 10 blocks
        recent_blocks = blockchain.chain[-10:]

        # Calculate actual time taken
        time_taken = recent_blocks[-1].timestamp - recent_blocks[0].timestamp
        expected_time = 60 * 9  # 9 intervals between 10 blocks

        # Calculate adjustment ratio
        adjustment_ratio = expected_time / time_taken

        # Limit to prevent wild swings
        adjustment_ratio = max(0.25, min(4.0, adjustment_ratio))

        # Calculate new difficulty
        new_difficulty = max(1, int(current_difficulty * adjustment_ratio))

        return new_difficulty
```

### Examples

**If blocks are too fast (30 seconds each):**
```
Time taken: 270 seconds
Expected: 540 seconds
Ratio: 540/270 = 2.0
New difficulty: current × 2 (INCREASES difficulty)
```

**If blocks are too slow (120 seconds each):**
```
Time taken: 1080 seconds
Expected: 540 seconds
Ratio: 540/1080 = 0.5
New difficulty: current × 0.5 (DECREASES difficulty)
```

### Starting Difficulty
```python
First 10 blocks: Difficulty = 4
(Requires hash to start with "0000")
```

## Proof of Work

### Mining Process
```python
def mine_block(self, mining_reward_address):
    # 1. Add coinbase transaction with calculated reward
    block_reward = self.calculate_block_reward()
    coinbase_tx = Transaction(
        sender="coinbase",
        inputs=[],
        outputs=[TransactionOutput(mining_reward_address, block_reward)]
    )

    # 2. Calculate merkle root
    self.calculate_merkle_root()

    # 3. Find valid nonce (Proof of Work)
    target = "0" * self.difficulty
    while True:
        self.calculate_hash()
        if self.hash.startswith(target):
            return True  # Valid block found!
        self.nonce += 1
```

### Hash Requirements
```
Difficulty 1:  Hash must start with "0"
Difficulty 2:  Hash must start with "00"
Difficulty 4:  Hash must start with "0000"
Difficulty 6:  Hash must start with "000000"
```

### Block Hash Calculation
```python
def calculate_hash(self):
    block_data = {
        "index": self.index,
        "timestamp": self.timestamp,
        "merkle_root": self.merkle_root,
        "previous_hash": self.previous_hash,
        "nonce": self.nonce,
        "difficulty": self.difficulty
    }
    block_string = json.dumps(block_data, sort_keys=True)
    return hashlib.sha256(block_string.encode()).hexdigest()
```

## Mining Statistics

### Hash Rate Calculation
```python
hashrate = nonce / elapsed_time
# Example: 100,000 nonces in 10 seconds = 10,000 H/s
```

### Network Difficulty vs Time
```
Difficulty 1:  ~milliseconds
Difficulty 2:  ~seconds
Difficulty 4:  ~minutes (target)
Difficulty 6:  ~hours
Difficulty 8:  ~days
```

## Mining Thread

### Implementation
```python
class CryptoMiningThread(QThread):
    def run(self):
        while self.running:
            # Create dummy transaction if no pending transactions
            if len(self.blockchain.pending_transactions) == 0:
                dummy_tx = DataTransaction(
                    sender=self.wallet.public_key,
                    data_content=f"Mining block at {time.time()}"
                )
                self.blockchain.add_transaction(dummy_tx)

            # Mine block with dynamic difficulty
            new_block = self.blockchain.mine_pending_transactions(
                self.wallet.address
            )

            if new_block:
                # Save to MySQL blockchain
                self.mysql_blockchain.save_block_to_mysql(new_block)

                # Broadcast to P2P network
                self.p2p_manager.broadcast_mined_block(new_block)

                # Update UI
                self.new_block.emit(new_block)
```

## Coinbase Transaction

### Structure
```python
{
    "tx_id": "coinbase_a1b2c3d4...",
    "tx_type": "coinbase",
    "sender": "coinbase",
    "inputs": [],  # No inputs (created from nothing)
    "outputs": [
        {
            "address": "miner_wallet_address",
            "amount": block_reward  # Calculated with halving
        }
    ],
    "timestamp": 1234567890.123,
    "signature": ""  # Coinbase doesn't need signature
}
```

### Validation
```python
# Coinbase transactions are exempt from normal validation
if tx.tx_type == "coinbase":
    # Skip signature verification
    # Skip input validation
    # Only verify it's first transaction in block
    return True
```

## Enhanced Node Server (Port 5000)

### Auto-Start
The Enhanced Node Server now **starts automatically** on initialization:
- Listens on `0.0.0.0:5000` (all interfaces)
- Provides HTTP API for blockchain queries
- Handles payment requests
- Enables blockchain sync

### API Endpoints

**GET /status**
```json
{
    "success": true,
    "blockchain_height": 1234,
    "pending_transactions": 5,
    "wallet_address": "PYC_abc123..."
}
```

**GET /blockchain**
```json
{
    "success": true,
    "height": 1234,
    "latest_block": {...}
}
```

**POST /payment_request**
```json
{
    "recipient": "PYC_xyz789...",
    "amount": 10.5,
    "reason": "Ad click payment"
}
```

**POST /sync**
```json
{
    "peer_id": "peer_abc123",
    "blockchain_height": 1200
}
```

## Mining Rewards Over Time

### First Year (Assuming 1 block/minute)
```
Blocks: 525,600 (365 days × 24 hours × 60 minutes)
Halving at: 210,000 blocks
Year 1 blocks: 210,000 @ 50 PYC = 10,500,000 PYC
Year 1 blocks: 315,600 @ 25 PYC = 7,890,000 PYC
Total Year 1: 18,390,000 PYC
```

### Supply Schedule
```
Year    Blocks     Reward    Annual Supply    Total Supply
1       525,600    50→25     18,390,000      18,390,000
2       525,600    25        13,140,000      31,530,000
3       525,600    25→12.5   9,855,000       41,385,000
4       525,600    12.5      6,570,000       47,955,000
...
∞       ∞          →0        →0              ~21,000,000
```

## Consensus Rules

### Block Acceptance
1. Block hash meets difficulty target
2. Previous hash links to last block
3. Merkle root matches transactions
4. All transactions are valid
5. Coinbase reward equals calculated reward
6. Timestamp is reasonable

### Chain Selection
- **Longest valid chain wins**
- Must pass all validation checks
- Synced with MySQL blockchain
- Verified by peer consensus

## Performance Optimization

### Mining Threads
```python
# Multi-threaded mining (CPU cores)
threads = os.cpu_count()
mining_thread = CryptoMiningThread(
    blockchain=blockchain,
    wallet=wallet,
    threads=threads
)
```

### Difficulty Limits
```python
# Prevent difficulty from going too high or low
min_difficulty = 1
max_difficulty = 20  # Practical limit
```

## Summary

✅ **Mining Rewards**: Bitcoin-style halving every 210,000 blocks
✅ **Difficulty**: Dynamic adjustment every 10 blocks (target: 60s/block)
✅ **Enhanced Node Server**: Auto-starts on port 5000
✅ **Total Supply**: ~21 million PYC (asymptotic limit)
✅ **Proof of Work**: SHA-256 hash with difficulty-based leading zeros
✅ **Consensus**: Longest valid chain + MySQL verification
