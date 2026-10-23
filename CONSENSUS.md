# Nickles consensus rules

Every block is judged by the same rules no matter where it came from: your own miner, a peer, the MySQL
sync, or a whole chain sent during synchronisation. The code is in `consensus.py`; the single entry points are
`Blockchain.add_block()` (one block) and `Blockchain.replace_chain()` (a competing chain).

## What follows Bitcoin

| Rule | Value |
|---|---|
| Signatures / keys | secp256k1 ECDSA, Base58Check addresses (`RIPEMD160(SHA256(pubkey))`, version 0x00) |
| Block subsidy | 50 NCKL, halves every 210,000 blocks (integer shift, as Bitcoin) |
| Maximum supply | 21,000,000 NCKL **including** the genesis distribution; the last subsidy is clamped so the cap is never crossed |
| Fees | inputs - outputs; the miner's coinbase may claim subsidy + fees, no more |
| Coinbase | exactly one, first, no inputs, commits to the block height (BIP34); spendable after 100 blocks |
| Proof of work | `hash <= target`, target stored as a 32-bit compact "bits" value (Bitcoin's `nBits` encoding) |
| Retarget | every 2016 blocks, scaled by actual/expected timespan, clamped to 4x either way (`target_spacing` 600 s) |
| Timestamps | greater than the median of the previous 11 blocks, at most 2 hours ahead of the node clock |
| Spends | input exists and is unspent (also inside the same block), owned by the signer, valid signature, no duplicate inputs, outputs positive with at most 8 decimals, inputs >= outputs |
| Transaction id | hash of the contents with input signatures excluded, so it is the same before and after signing and cannot be changed by re-encoding a signature |
| Limits | 1,000,000 bytes and 5,000 transactions per block |
| Chain choice | the chain with the most cumulative proof of work wins, not simply the longest |
| Amounts | handled in whole base units (1 NCKL = 100,000,000), never as floats |

Relay policy (not consensus, local to each node): minimum fee 0.00001 NCKL per transaction, valid Base58Check
output addresses, change below 0.00001 NCKL goes to the fee, mempool capped at 5,000 transactions.

## What deliberately differs from Bitcoin (to keep your existing chain valid)

* Block and transaction hashing is still SHA-256 of canonical JSON, not double-SHA-256 of a binary header.
  Changing it would invalidate every existing block, wallet and peer.
* There is no script system; ownership is "the signer's address equals the output's address".
* The peer network is HTTP/JSON, not Bitcoin's wire protocol.
* The chain began with a **1,000,000 NCKL genesis distribution** to participating wallets. Bitcoin has no premine.
  It counts toward the 21M cap.
* Data (`data`, `dsa_verification`) transactions exist; they move no value, must be signed, and are limited to
  10,000 bytes.

## Activation

History before block `v2_height` (default **100**) is only checked structurally, exactly as before, so the
existing 12-block chain stays valid. Blocks at height 100 and above must satisfy every rule above. From that
height the block's `difficulty` field holds the compact target instead of a leading-zeros count; the first v2 block
carries the previous difficulty over as an equivalent target.

All nodes must run this version before the network reaches block 100, otherwise older nodes will build on blocks
the new rules reject and the network splits.

Override any parameter by creating `consensus_params.json` next to `consensus.py`, for example
`{"v2_height": 250}`. Do not change consensus values on only some nodes.

Note on pacing: with Bitcoin's 2016-block retarget and 600 s target, a young chain mined by a few CPUs stays at
the carried-over difficulty for the first 2016 blocks, then moves by at most 4x per period. If you want faster
adaptation, lower `retarget_interval` (and `target_spacing`) for every node before activation.

## Tests

```
python -m unittest test_consensus -v
```

The suite builds real chains (with shrunk parameters) and attacks them: overpaying or forging coinbases, double
spends, spending someone else's coins, immature coinbase spends, wrong difficulty, bad timestamps, oversize
blocks, supply cap, tampered peer blocks, competing chains, and replays the real `blockchain.json` to prove
the existing history is still valid.
