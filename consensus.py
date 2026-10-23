"""Nickles consensus rules (Bitcoin-style).

Every rule here is applied to a block no matter who mined it: your own miner, a peer, a database sync or a
chain sent during synchronisation.  History before ``v2_height`` is only checked structurally (so the existing
chain stays valid); blocks at ``v2_height`` and above must satisfy all of the rules below.

Rules for v2 blocks (Bitcoin equivalents in brackets):
  * height/previous-hash linkage, header hash recomputed, Merkle root recomputed
  * proof of work: hash <= 256-bit target stored in compact "bits" form (nBits)
  * bits must equal the retarget result: every ``retarget_interval`` blocks the target is scaled by
    actual/expected timespan, clamped to a factor of ``max_adjust`` (GetNextWorkRequired)
  * timestamp > median of the previous 11 blocks and <= now + 2 hours (median-time-past, max future drift)
  * block size and transaction-count limits
  * exactly one coinbase, first in the block, no inputs, carrying the block height (BIP34)
  * coinbase pays at most subsidy(height) + fees; subsidy halves every ``halving_interval`` blocks and total
    supply can never exceed ``max_money`` (21,000,000)
  * coinbase outputs cannot be spent until ``coinbase_maturity`` blocks old (100)
  * every spend: input exists and is unspent (also inside the same block), owned by the signer, valid
    signature, tx_id equals the hash of its contents, no duplicate inputs, outputs > 0 with at most 8 decimals,
    inputs >= outputs (the difference is the fee the miner may claim)
"""
import json
import os
import time
from decimal import Decimal, InvalidOperation

COIN = 100_000_000  # 1 NCKL in base units ("satoshis")


class ConsensusError(Exception):
    pass


class Params:
    """Consensus parameters.  Defaults are Bitcoin's; v2_height is where the stricter rules begin."""

    def __init__(self, **overrides):
        self.v2_height = 100                  # first block that must satisfy the v2 rules
        self.coin_name = "Nickles"         # display name (set in consensus_params.json)
        self.ticker = "NCKL"
        self.address_version = 0x00           # Base58Check version byte; the version decides the first letter of addresses
        self.genesis_file = "genesis.json"    # the one fixed genesis block every node loads
        self.max_money = 21_000_000 * COIN
        self.initial_subsidy = 50 * COIN
        self.halving_interval = 210_000
        self.coinbase_maturity = 100
        self.target_spacing = 600             # seconds per block
        self.retarget_interval = 2016         # blocks between difficulty adjustments
        self.max_adjust = 4                   # timespan is clamped to [1/4, 4] x expected
        self.mtp_span = 11
        self.max_future_seconds = 2 * 60 * 60
        self.max_block_bytes = 1_000_000
        self.max_block_txs = 5000
        self.max_data_bytes = 10_000          # payload limit for data / dsa_verification transactions
        self.pow_limit_target = (1 << 252) - 1  # easiest allowed target (about one leading hex zero)
        # relay policy (not consensus): what a node will accept into its mempool
        self.min_relay_fee_sat = 1_000        # 0.00001 NCKL
        self.dust_sat = 1_000
        self.max_mempool_txs = 5000
        for key, value in overrides.items():
            if not hasattr(self, key):
                raise AttributeError(f"unknown consensus parameter: {key}")
            setattr(self, key, value)

    @property
    def target_timespan(self):
        return self.target_spacing * self.retarget_interval


def _load_params():
    p = Params()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "consensus_params.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            for key, value in json.load(fh).items():
                setattr(p, key, value)
    return p


PARAMS = _load_params()

STANDARD_TYPE = "standard"
DATA_TYPES = ("data", "dsa_verification")


# ---------------------------------------------------------------------------------------------------------
# amounts
# ---------------------------------------------------------------------------------------------------------
def to_sat(value, strict=True):
    """Convert a coin amount (float/int) to integer base units.  Strict mode rejects more than 8 decimals."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConsensusError("amount is not a number")
    try:
        exact = Decimal(repr(value)) * COIN
    except InvalidOperation:
        raise ConsensusError("amount is not a finite number")
    if not exact.is_finite():
        raise ConsensusError("amount is not finite")
    sat = int(exact.to_integral_value())
    if strict and exact != sat:
        raise ConsensusError("amount has more than 8 decimal places")
    return sat


def from_sat(sat):
    return sat / COIN


# ---------------------------------------------------------------------------------------------------------
# targets / proof of work (compact "bits" encoding exactly as Bitcoin's arith_uint256::SetCompact/GetCompact)
# ---------------------------------------------------------------------------------------------------------
def zeros_to_target(zeros):
    """Legacy difficulty (number of leading hex zeros) -> equivalent 256-bit target."""
    if not isinstance(zeros, int) or zeros < 0 or zeros > 64:
        raise ConsensusError("legacy difficulty out of range")
    return (1 << (256 - 4 * zeros)) - 1


def bits_to_target(bits):
    if not isinstance(bits, int) or isinstance(bits, bool) or bits < 0 or bits > 0xFFFFFFFF:
        raise ConsensusError("bits is not a 32-bit integer")
    exponent = bits >> 24
    mantissa = bits & 0x007FFFFF
    if bits & 0x00800000 and mantissa:
        raise ConsensusError("negative target")
    if exponent <= 3:
        target = mantissa >> (8 * (3 - exponent))
    else:
        target = mantissa << (8 * (exponent - 3))
    if target >= (1 << 256):
        raise ConsensusError("target overflow")
    return target


def target_to_bits(target):
    if target <= 0:
        raise ConsensusError("target must be positive")
    size = (target.bit_length() + 7) // 8
    if size <= 3:
        compact = target << (8 * (3 - size))
    else:
        compact = target >> (8 * (size - 3))
    if compact & 0x00800000:  # would be read as a sign bit
        compact >>= 8
        size += 1
    return compact | (size << 24)


def block_target(block, p=PARAMS):
    if block.index == 0 or block.index < p.v2_height:
        return zeros_to_target(block.difficulty)
    return bits_to_target(block.difficulty)


def block_work(block, p=PARAMS):
    return (1 << 256) // (block_target(block, p) + 1)


def chain_work(blocks, p=PARAMS):
    return sum(block_work(b, p) for b in blocks)


def hash_meets_target(hash_hex, target):
    if not isinstance(hash_hex, str) or len(hash_hex) != 64:
        return False
    try:
        return int(hash_hex, 16) <= target
    except ValueError:
        return False


# ---------------------------------------------------------------------------------------------------------
# monetary policy
# ---------------------------------------------------------------------------------------------------------
def subsidy_sat(height, p=PARAMS):
    halvings = height // p.halving_interval
    return 0 if halvings >= 64 else p.initial_subsidy >> halvings


def subsidy_sum_sat(first, last, p=PARAMS):
    """Sum of the nominal subsidies for heights first..last inclusive."""
    if last < first:
        return 0
    total, k = 0, first // p.halving_interval
    while True:
        seg_start = max(first, k * p.halving_interval)
        seg_end = min(last, (k + 1) * p.halving_interval - 1)
        if seg_start > last:
            break
        if seg_end >= seg_start:
            total += (seg_end - seg_start + 1) * (0 if k >= 64 else p.initial_subsidy >> k)
        k += 1
    return total


def issued_before_sat(height, genesis_total_sat, p=PARAMS):
    """Coins in existence before the block at `height` is added."""
    return min(genesis_total_sat + subsidy_sum_sat(1, height - 1, p), p.max_money)


def allowed_subsidy_sat(height, genesis_total_sat, p=PARAMS):
    """Subsidy the block at `height` may create, never pushing supply over max_money."""
    return max(0, min(subsidy_sat(height, p), p.max_money - issued_before_sat(height, genesis_total_sat, p)))


def genesis_total_sat(chain):
    return sum(to_sat(o.amount, strict=False) for tx in chain[0].transactions for o in tx.outputs)


# ---------------------------------------------------------------------------------------------------------
# time and difficulty
# ---------------------------------------------------------------------------------------------------------
def median_time_past(chain, p=PARAMS):
    stamps = sorted(b.timestamp for b in chain[-p.mtp_span:])
    return stamps[len(stamps) // 2]


def expected_bits(chain, height, p=PARAMS):
    """The compact target the block at `height` must carry (chain holds blocks 0..height-1)."""
    prev = chain[height - 1]
    prev_target = block_target(prev, p)
    at_retarget = height >= p.retarget_interval and height % p.retarget_interval == 0
    if not at_retarget:
        if height == p.v2_height:
            # first v2 block: carry the old leading-zeros difficulty over as an equivalent compact target
            return target_to_bits(min(prev_target, p.pow_limit_target))
        return prev.difficulty
    # Bitcoin's retarget: scale by actual/expected timespan of the last interval, clamped to 4x either way
    first = chain[height - p.retarget_interval]
    timespan = int(prev.timestamp) - int(first.timestamp)
    timespan = max(p.target_timespan // p.max_adjust, min(timespan, p.target_timespan * p.max_adjust))
    new_target = min(prev_target * timespan // p.target_timespan, p.pow_limit_target)
    return target_to_bits(max(new_target, 1))


# ---------------------------------------------------------------------------------------------------------
# unspent outputs
# ---------------------------------------------------------------------------------------------------------
class UtxoView:
    """Read/write overlay on a UTXO dict: lets a block be checked without touching the real set."""

    def __init__(self, base):
        self.base = base
        self.added = {}
        self.removed = set()

    def get(self, key):
        if key in self.added:
            return self.added[key]
        if key in self.removed:
            return None
        return self.base.get(key)

    def __contains__(self, key):
        return self.get(key) is not None

    def spend(self, key):
        if key in self.added:
            del self.added[key]
        else:
            self.removed.add(key)

    def add(self, key, entry):
        self.removed.discard(key)
        self.added[key] = entry


def utxo_entry(tx, index, height):
    out = tx.outputs[index]
    is_cb = tx.tx_type in ("genesis", "coinbase")
    return {
        "owner": "system" if is_cb else tx.sender,
        "recipient": out.address,
        "amount": out.amount,
        "tx_id": tx.tx_id,
        "output_index": index,
        "height": height,
        "coinbase": tx.tx_type == "coinbase",
    }


def apply_tx(view, tx, height):
    for inp in tx.inputs:
        view.spend(f"{inp.tx_id}:{inp.output_index}")
    for i in range(len(tx.outputs)):
        view.add(f"{tx.tx_id}:{i}", utxo_entry(tx, i, height))


def _legacy_spend_is_valid(utxo, tx):
    """Pre-v2 history was written before spends were checked, so some transactions spend a coin that was already
    spent (the same genesis coin paid out 24 times in block 1) or pay out more than they take in.  Read it as
    Bitcoin would: the FIRST spend of a coin stands; a transaction whose inputs are missing, repeated, or worth less
    than its outputs is void and its outputs never existed.  Blocks and hashes are untouched."""
    seen, total_in = set(), 0
    for inp in tx.inputs:
        key = f"{inp.tx_id}:{inp.output_index}"
        entry = utxo.get(key)
        if key in seen or entry is None:
            return False
        seen.add(key)
        try:
            total_in += to_sat(entry["amount"], strict=False)
        except ConsensusError:
            return False
    try:
        total_out = sum(to_sat(o.amount, strict=False) for o in tx.outputs)
    except ConsensusError:
        return False
    return total_out <= total_in


def apply_block(utxo, block):
    """Apply a block to a real UTXO dict in place (used by Blockchain.update_utxo and chain replay)."""
    legacy = block.index != 0 and block.index < PARAMS.v2_height
    for tx in block.transactions:
        if legacy and tx.inputs and not _legacy_spend_is_valid(utxo, tx):
            continue        # void double-spend / inflating transaction from before the checks existed
        for inp in tx.inputs:
            utxo.pop(f"{inp.tx_id}:{inp.output_index}", None)
        for i in range(len(tx.outputs)):
            utxo[f"{tx.tx_id}:{i}"] = utxo_entry(tx, i, block.index)


# ---------------------------------------------------------------------------------------------------------
# transactions
# ---------------------------------------------------------------------------------------------------------
def _address_of(pubkey):
    from pythoncoin import CryptoUtils
    return CryptoUtils.pubkey_to_address(pubkey)


_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def decode_address(address):
    """Base58Check decode.  Returns (version byte, 20-byte hash) or None if malformed / checksum wrong."""
    import hashlib
    if not isinstance(address, str) or not 25 <= len(address) <= 36:
        return None
    num = 0
    for ch in address:
        i = _B58.find(ch)
        if i < 0:
            return None
        num = num * 58 + i
    if num.bit_length() > 200:
        return None
    raw = num.to_bytes(25, "big")
    if hashlib.sha256(hashlib.sha256(raw[:21]).digest()).digest()[:4] != raw[21:]:
        return None
    return raw[0], raw[1:21]


def encode_address(version, hash160):
    import hashlib
    payload = bytes([version]) + bytes(hash160)
    raw = payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    num = int.from_bytes(raw, "big")
    out = ""
    while num:
        num, r = divmod(num, 58)
        out = _B58[r] + out
    return "1" * (len(raw) - len(raw.lstrip(b"\0"))) + out


def is_valid_address(address, p=PARAMS):
    """A Base58Check P2PKH address of THIS coin (right version byte, 4-byte double-SHA256 checksum).  Relay policy."""
    decoded = decode_address(address)
    return decoded is not None and decoded[0] == p.address_version


def convert_address(address, new_version=None, p=PARAMS):
    """Re-encode an address of another version (e.g. an old Bitcoin-format one) with this coin's version byte.
    The hash160 is unchanged, so whoever held the key still owns it.  Returns None if `address` is not valid."""
    decoded = decode_address(address)
    if decoded is None:
        return None
    return encode_address(p.address_version if new_version is None else new_version, decoded[1])


def check_transaction(tx, view, height, p=PARAMS):
    """Validate a non-coinbase transaction against `view`.  Returns (error or None, fee in base units)."""
    try:
        if tx.compute_tx_id() != tx.tx_id:
            return "tx_id does not match transaction contents", 0
        if tx.tx_type in DATA_TYPES:
            if tx.inputs or tx.outputs:
                return "data transaction must not move value", 0
            if len(json.dumps(tx.data or {}, sort_keys=True)) > p.max_data_bytes:
                return "data transaction payload too large", 0
            if not tx.verify():
                return "invalid signature", 0
            return None, 0
        if tx.tx_type != STANDARD_TYPE:
            return f"transaction type '{tx.tx_type}' is not allowed", 0
        if not tx.inputs or not tx.outputs:
            return "transaction needs at least one input and one output", 0
        owner = _address_of(tx.sender)
        seen, in_sat = set(), 0
        for inp in tx.inputs:
            key = f"{inp.tx_id}:{inp.output_index}"
            if key in seen:
                return "duplicate input", 0
            seen.add(key)
            entry = view.get(key)
            if entry is None:
                return f"input {key} is missing or already spent", 0
            if entry["recipient"] != owner:
                return f"input {key} is not owned by the signer", 0
            if height >= p.v2_height and entry.get("coinbase") and height - entry.get("height", 0) < p.coinbase_maturity:
                return f"input {key} is an immature coinbase output", 0
            in_sat += to_sat(entry["amount"], strict=False)
        out_sat = 0
        for out in tx.outputs:
            amount = to_sat(out.amount)
            if amount <= 0:
                return "output amount must be positive", 0
            if not isinstance(out.address, str) or not out.address:
                return "output has no address", 0
            out_sat += amount
            if out_sat > p.max_money:
                return "outputs exceed the maximum money supply", 0
        if out_sat > in_sat:
            return "outputs exceed inputs", 0
        for i in range(len(tx.outputs)):
            if f"{tx.tx_id}:{i}" in view:
                return "transaction id already exists", 0
        if not tx.verify():
            return "invalid signature", 0
        return None, in_sat - out_sat
    except ConsensusError as exc:
        return str(exc), 0
    except Exception as exc:  # malformed peer data must reject, never crash the node
        return f"malformed transaction: {exc}", 0


# ---------------------------------------------------------------------------------------------------------
# blocks
# ---------------------------------------------------------------------------------------------------------
def check_block_structure(chain, block):
    """Linkage and integrity checks shared by legacy and v2 blocks.  Returns an error string or None."""
    if not chain:
        if block.index != 0:
            return "first block must have index 0"
        if block.previous_hash != "0" * 64:
            return "genesis previous_hash must be all zeros"
    else:
        prev = chain[-1]
        if block.index != prev.index + 1:
            return f"expected block index {prev.index + 1}, got {block.index}"
        if block.previous_hash != prev.hash:
            return "previous_hash does not match the chain tip"
    if block.compute_hash() != block.hash:
        return "block hash does not match its header"
    if block.compute_merkle_root() != block.merkle_root:
        return "merkle root does not match transactions"
    return None


def check_block(chain, block, utxo, p=PARAMS, now=None):
    """Full validation of `block` as the next block after `chain`.  Returns (error or None, fees)."""
    try:
        err = check_block_structure(chain, block)
        if err:
            return err, 0
        if block.index == 0 or block.index < p.v2_height:
            return _check_legacy_block(block), 0

        now = time.time() if now is None else now
        height = block.index
        if not isinstance(block.difficulty, int) or isinstance(block.difficulty, bool):
            return "difficulty/bits must be an integer", 0
        if block.difficulty != expected_bits(chain, height, p):
            return "bits do not match the required difficulty", 0
        target = bits_to_target(block.difficulty)
        if target <= 0 or target > p.pow_limit_target:
            return "target outside the allowed range", 0
        if not hash_meets_target(block.hash, target):
            return "proof of work does not meet the target", 0
        if not isinstance(block.timestamp, (int, float)) or isinstance(block.timestamp, bool):
            return "timestamp is not a number", 0
        if block.timestamp <= median_time_past(chain, p):
            return "timestamp is not after the median of the previous blocks", 0
        if block.timestamp > now + p.max_future_seconds:
            return "timestamp is too far in the future", 0
        txs = block.transactions
        if not txs or len(txs) > p.max_block_txs:
            return "block has no transactions or too many", 0
        if len(json.dumps(block.to_dict())) > p.max_block_bytes:
            return "block is too large", 0
        ids = [t.tx_id for t in txs]
        if len(set(ids)) != len(ids):
            return "duplicate transaction in block", 0

        coinbase = txs[0]
        if coinbase.tx_type != "coinbase" or coinbase.inputs or coinbase.sender != "coinbase":
            return "first transaction must be a coinbase with no inputs", 0
        if any(t.tx_type == "coinbase" for t in txs[1:]):
            return "block contains more than one coinbase", 0
        if any(t.tx_type == "genesis" for t in txs):
            return "genesis transactions are only allowed in block 0", 0
        if coinbase.compute_tx_id() != coinbase.tx_id:
            return "coinbase tx_id does not match its contents", 0
        if not isinstance(coinbase.data, dict) or coinbase.data.get("height") != height:
            return "coinbase does not commit to the block height", 0
        if not coinbase.outputs:
            return "coinbase has no outputs", 0

        view = UtxoView(utxo)
        fees = 0
        for tx in txs[1:]:
            err, fee = check_transaction(tx, view, height, p)
            if err:
                return f"transaction {tx.tx_id[:12]}: {err}", 0
            apply_tx(view, tx, height)
            fees += fee

        claimed = 0
        for out in coinbase.outputs:
            amount = to_sat(out.amount)
            if amount < 0:
                return "coinbase output cannot be negative", 0
            claimed += amount
        limit = allowed_subsidy_sat(height, genesis_total_sat(chain), p) + fees
        if claimed > limit:
            return f"coinbase pays {from_sat(claimed)} but only {from_sat(limit)} is allowed", 0
        return None, fees
    except ConsensusError as exc:
        return str(exc), 0
    except Exception as exc:
        return f"malformed block: {exc}", 0


def _check_legacy_block(block):
    """History before v2_height: hash, legacy proof of work and signatures only (as always)."""
    zeros = block.difficulty
    if not isinstance(zeros, int) or not 0 <= zeros <= 64:
        return "legacy difficulty out of range"
    if not block.hash.startswith("0" * zeros):
        return "legacy proof of work not met"
    for tx in block.transactions:
        if tx.tx_type not in ("coinbase", "genesis") and not tx.verify():
            return "invalid transaction signature"
    return None


def validate_chain(blocks, p=PARAMS, now=None):
    """Replay a whole chain from genesis.  Returns (error or None, utxo set, total work)."""
    utxo, accepted = {}, []
    for block in blocks:
        err, _ = check_block(accepted, block, utxo, p, now)
        if err:
            return f"block {block.index}: {err}", {}, 0
        apply_block(utxo, block)
        accepted.append(block)
    return None, utxo, chain_work(accepted, p)
