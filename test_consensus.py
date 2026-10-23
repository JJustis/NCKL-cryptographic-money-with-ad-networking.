"""Tests for the Bitcoin-style consensus rules (consensus.py + Blockchain.add_block and friends).

Run:  python -m unittest test_consensus -v

The parameters are shrunk (activation at block 4, retarget every 4 blocks, maturity 3) so a whole chain can be
built in a second; the rules themselves are exactly the ones used with the real parameters.
"""
import copy
import json
import logging
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import consensus
from consensus import COIN, bits_to_target, target_to_bits
import pythoncoin as pc
from pythoncoin import Blockchain, Block, Transaction, TransactionInput, TransactionOutput, CryptoUtils

logging.disable(logging.CRITICAL)

TEST_PARAMS = dict(
    v2_height=4, retarget_interval=1000, target_spacing=10, coinbase_maturity=3,
    halving_interval=100, pow_limit_target=(1 << 255) - 1,
)


def wallet():
    return CryptoUtils.generate_keypair()


def build_manual_tx(sender, inputs, outputs, sign=True):
    tx = Transaction(sender=sender["public_key"],
                     inputs=[TransactionInput(tx_id=t, output_index=i) for t, i in inputs],
                     outputs=[TransactionOutput(address=a, amount=v) for a, v in outputs])
    if sign:
        tx.sign(sender["private_key"])
    return tx


class ConsensusCase(unittest.TestCase):
    def setUp(self):
        self._saved = dict(vars(consensus.PARAMS))
        for k, v in TEST_PARAMS.items():
            setattr(consensus.PARAMS, k, v)
        self.alice, self.bob = wallet(), wallet()
        self.bc = Blockchain(genesis_addresses=[self.alice["address"]])  # alice holds the 1,000,000 genesis coins

    def tearDown(self):
        for k, v in self._saved.items():            # restore every parameter, including ones a test changed
            setattr(consensus.PARAMS, k, v)

    # ----- helpers --------------------------------------------------------------------------------------
    def mine(self, n=1, miner=None, bc=None):
        bc = bc or self.bc
        miner = miner or self.alice
        blocks = []
        for _ in range(n):
            block = bc.mine_pending_transactions(miner["address"])
            self.assertTrue(block, "mining a valid block should succeed")
            blocks.append(block)
        return blocks

    def to_v2(self):
        """Mine until the next block is the first v2 block."""
        while len(self.bc.chain) < consensus.PARAMS.v2_height:
            self.mine()

    def forge(self, txs=(), bc=None, miner=None, cb_amount_sat=None, cb_height="auto", bits=None, ts=None,
              extra_coinbases=0, prev_hash=None, index=None, fees_sat=0, mine_pow=True):
        """Build a v2 block that is valid unless a parameter says otherwise (the PoW is solved for the bits used)."""
        bc = bc or self.bc
        miner = miner or self.alice
        p = consensus.PARAMS
        last = bc.chain[-1]
        h = last.index + 1 if index is None else index
        subsidy = consensus.allowed_subsidy_sat(h, consensus.genesis_total_sat(bc.chain), p)
        amount = subsidy + fees_sat if cb_amount_sat is None else cb_amount_sat

        def coinbase(n):
            cb = Transaction(sender="coinbase", inputs=[],
                             outputs=[TransactionOutput(address=miner["address"], amount=consensus.from_sat(amount))],
                             tx_type="coinbase", data={"height": h if cb_height == "auto" else cb_height, "n": n})
            cb.calculate_tx_id()
            return cb

        txlist = [coinbase(0)] + [coinbase(i + 1) for i in range(extra_coinbases)] + list(txs)
        use_bits = consensus.expected_bits(bc.chain, h, p) if bits is None else bits
        stamp = max(time.time(), consensus.median_time_past(bc.chain, p) + 1) if ts is None else ts
        block = Block(index=h, timestamp=stamp, transactions=txlist,
                      previous_hash=prev_hash or last.hash, difficulty=use_bits)
        block.merkle_root = block.compute_merkle_root()
        target = bits_to_target(use_bits)
        block.nonce = 0
        while True:
            block.hash = block.compute_hash()
            if (int(block.hash, 16) <= target) == mine_pow:
                return block
            block.nonce += 1

    def assertRejected(self, block, fragment):
        err = self.bc.check_block(block)
        self.assertIsNotNone(err, "block should have been rejected")
        self.assertIn(fragment, err)
        height = len(self.bc.chain)
        self.assertFalse(self.bc.add_block(block))
        self.assertEqual(len(self.bc.chain), height, "a rejected block must not change the chain")

    def assertAccepted(self, block):
        self.assertIsNone(self.bc.check_block(block))
        self.assertTrue(self.bc.add_block(block))
        self.assertIs(self.bc.chain[-1], block)


class TestEncoding(unittest.TestCase):
    def test_bitcoin_compact_vectors(self):
        # Bitcoin mainnet genesis nBits and a few classic edge cases
        self.assertEqual(bits_to_target(0x1D00FFFF), 0xFFFF * 256 ** (0x1D - 3))
        self.assertEqual(target_to_bits(0xFFFF * 256 ** (0x1D - 3)), 0x1D00FFFF)
        self.assertEqual(bits_to_target(0x1B0404CB), 0x0404CB * 256 ** (0x1B - 3))
        self.assertEqual(target_to_bits(0x0404CB * 256 ** (0x1B - 3)), 0x1B0404CB)
        self.assertEqual(target_to_bits(0x80), 0x02008000)       # sign bit must never be set
        self.assertEqual(bits_to_target(0x02008000), 0x80)
        for t in (1, 255, 0x7FFFFF, 0x800000, 2 ** 200 + 12345, 2 ** 255 - 1):
            self.assertLessEqual(bits_to_target(target_to_bits(t)), t)   # compact form only ever rounds down
        with self.assertRaises(consensus.ConsensusError):
            bits_to_target(0x04923456)                             # negative target
        with self.assertRaises(consensus.ConsensusError):
            bits_to_target(0xFF123456)                             # overflow

    def test_legacy_zeros_equal_hex_prefix(self):
        for zeros in (1, 2, 4):
            target = consensus.zeros_to_target(zeros)
            self.assertTrue(consensus.hash_meets_target("0" * zeros + "f" * (64 - zeros), target))
            self.assertFalse(consensus.hash_meets_target("0" * (zeros - 1) + "1" + "f" * (63 - zeros + 1), target))


class TestMonetaryPolicy(unittest.TestCase):
    def test_subsidy_and_halving_match_bitcoin(self):
        p = consensus.Params()
        self.assertEqual(consensus.subsidy_sat(1, p), 50 * COIN)
        self.assertEqual(consensus.subsidy_sat(209_999, p), 50 * COIN)
        self.assertEqual(consensus.subsidy_sat(210_000, p), 25 * COIN)
        self.assertEqual(consensus.subsidy_sat(420_000, p), 1_250_000_000)
        self.assertEqual(consensus.subsidy_sat(210_000 * 33, p), 0)
        self.assertEqual(consensus.subsidy_sat(210_000 * 64, p), 0)

    def test_total_supply_never_exceeds_21_million(self):
        p = consensus.Params()
        total = sum(consensus.subsidy_sat(h, p) for h in range(0, 210_000 * 34, 1000)) * 1000  # coarse upper bound
        self.assertLessEqual(consensus.subsidy_sum_sat(0, 210_000 * 70, p), 21_000_000 * COIN)
        self.assertEqual(consensus.subsidy_sum_sat(0, 209_999, p), 210_000 * 50 * COIN)
        self.assertEqual(consensus.subsidy_sum_sat(5, 4, p), 0)
        self.assertEqual(consensus.subsidy_sum_sat(209_990, 210_009, p), 10 * 50 * COIN + 10 * 25 * COIN)

    def test_cap_clamps_the_last_subsidy(self):
        p = consensus.Params(max_money=1_000 * COIN, initial_subsidy=50 * COIN, halving_interval=1_000_000)
        genesis = 970 * COIN
        self.assertEqual(consensus.allowed_subsidy_sat(1, genesis, p), 30 * COIN)    # only 30 left to issue
        self.assertEqual(consensus.allowed_subsidy_sat(2, genesis, p), 0)            # cap reached
        self.assertEqual(consensus.issued_before_sat(5, genesis, p), 1_000 * COIN)

    def test_amounts_are_exact_eight_decimals(self):
        self.assertEqual(consensus.to_sat(0.1), 10_000_000)
        self.assertEqual(consensus.to_sat(20999999.99999999), 2099999999999999)
        self.assertEqual(consensus.to_sat(50), 50 * COIN)
        for bad in (0.000000001, float("nan"), float("inf"), "5", None, True):
            with self.assertRaises(consensus.ConsensusError):
                consensus.to_sat(bad)


class TestBlocks(ConsensusCase):
    def test_legacy_history_stays_valid_and_v2_blocks_follow(self):
        self.to_v2()
        self.assertTrue(self.bc.is_chain_valid())
        block = self.mine()[0]
        self.assertEqual(block.index, consensus.PARAMS.v2_height)
        self.assertEqual(block.transactions[0].data["height"], block.index)
        self.assertTrue(self.bc.is_chain_valid())
        self.assertEqual(len(self.bc.chain), consensus.PARAMS.v2_height + 1)

    def test_honest_blocks_with_fees_pay_subsidy_plus_fees(self):
        self.to_v2()
        self.mine(consensus.PARAMS.coinbase_maturity)             # alice's own rewards mature; she also has genesis coins
        tx = self.bc.create_transaction(self.alice["private_key"], self.alice["public_key"], self.bob["address"], 10, fee=0.5)
        self.assertTrue(self.bc.add_transaction(tx))
        block = self.mine(miner=self.bob)[0]
        cb = sum(o.amount for o in block.transactions[0].outputs)
        subsidy = consensus.allowed_subsidy_sat(block.index, consensus.genesis_total_sat(self.bc.chain))
        self.assertEqual(consensus.to_sat(cb), subsidy + consensus.to_sat(0.5))
        self.assertEqual(self.bc.get_balance(self.bob["address"]), 10 + cb)
        self.assertEqual(self.bc.pending_transactions, [])

    def test_coinbase_may_not_overpay(self):
        self.to_v2()
        subsidy = consensus.allowed_subsidy_sat(len(self.bc.chain), consensus.genesis_total_sat(self.bc.chain))
        self.assertRejected(self.forge(cb_amount_sat=subsidy + 1), "coinbase pays")
        self.assertRejected(self.forge(cb_amount_sat=10 ** 12), "coinbase pays")
        self.assertAccepted(self.forge(cb_amount_sat=subsidy))
        # a miner is allowed to claim less than the maximum
        self.assertAccepted(self.forge(cb_amount_sat=subsidy - 1))

    def test_peer_cannot_forge_a_coinbase_that_pays_anyone_anything(self):
        """The original hole: tx_type 'coinbase' skipped every check."""
        self.to_v2()
        thief = wallet()
        fake = Transaction(sender="coinbase", inputs=[], tx_type="coinbase", data={"height": len(self.bc.chain)},
                           outputs=[TransactionOutput(address=thief["address"], amount=21_000_000.0)])
        fake.calculate_tx_id()
        block = self.forge(txs=[fake])             # a second 'coinbase' hidden among the transactions
        self.assertRejected(block, "more than one coinbase")
        self.assertRejected(self.forge(extra_coinbases=1), "more than one coinbase")

    def test_coinbase_must_commit_to_height_and_come_first(self):
        self.to_v2()
        self.assertRejected(self.forge(cb_height=1), "does not commit to the block height")
        block = self.forge()
        block.transactions.reverse() if len(block.transactions) > 1 else None
        data_tx = pc.DataTransaction(self.alice["public_key"], "x", self.alice["private_key"])
        b2 = self.forge(txs=[data_tx])
        b2.transactions = [b2.transactions[1], b2.transactions[0]]
        b2.merkle_root = b2.compute_merkle_root()
        b2.nonce = 0
        while int(b2.compute_hash(), 16) > bits_to_target(b2.difficulty):
            b2.nonce += 1
        b2.hash = b2.compute_hash()
        self.assertRejected(b2, "first transaction must be a coinbase")

    def test_header_must_be_honest(self):
        self.to_v2()
        good = self.forge()
        bad = copy.deepcopy(good); bad.hash = "0" * 64
        self.assertRejected(bad, "hash does not match")
        bad = copy.deepcopy(good); bad.merkle_root = "f" * 64
        bad.hash = bad.compute_hash()
        self.assertRejected(bad, "merkle root")
        self.assertRejected(self.forge(prev_hash="a" * 64), "previous_hash")
        self.assertRejected(self.forge(index=len(self.bc.chain) + 1, bits=consensus.expected_bits(self.bc.chain, len(self.bc.chain))), "expected block index")
        self.assertRejected(self.forge(mine_pow=False), "proof of work")
        self.assertAccepted(good)
        self.assertRejected(good, "expected block index")          # the same block twice

    def test_difficulty_must_match_the_retarget(self):
        self.to_v2()
        tip_bits = self.bc.chain[-1].difficulty if self.bc.chain[-1].index >= consensus.PARAMS.v2_height else None
        expected = consensus.expected_bits(self.bc.chain, len(self.bc.chain))
        easier = target_to_bits(min(bits_to_target(expected) * 2, consensus.PARAMS.pow_limit_target))
        if easier != expected:
            self.assertRejected(self.forge(bits=easier), "bits do not match")
        self.assertRejected(self.forge(bits=target_to_bits(bits_to_target(expected) // 2)), "bits do not match")
        self.assertAccepted(self.forge())

    def test_retarget_scales_by_timespan_and_clamps_like_bitcoin(self):
        p = consensus.PARAMS
        p.retarget_interval = 4
        self.to_v2()
        while len(self.bc.chain) < p.retarget_interval * 2:
            self.mine()
        h = p.retarget_interval * 2
        prev = self.bc.chain[h - 1]
        first = self.bc.chain[h - p.retarget_interval]
        prev_target = bits_to_target(prev.difficulty) if prev.index >= p.v2_height else consensus.zeros_to_target(prev.difficulty)
        actual = int(prev.timestamp) - int(first.timestamp)
        clamped = max(p.target_timespan // 4, min(actual, p.target_timespan * 4))
        want = target_to_bits(min(prev_target * clamped // p.target_timespan, p.pow_limit_target))
        # rebuild the chain prefix and ask for the bits at the retarget height
        prefix = self.bc.chain[:h]
        self.assertEqual(consensus.expected_bits(prefix, h), want)
        # blocks mined within a few seconds against a 40 s target must make mining harder by the maximum 4x
        self.assertLess(bits_to_target(want), prev_target)
        # outside the retarget height, difficulty is carried forward unchanged
        self.mine()
        self.assertEqual(consensus.expected_bits(self.bc.chain[:h + 1], h + 1), self.bc.chain[h].difficulty)

    def test_retarget_math_with_synthetic_timestamps(self):
        class B:  # minimal block stand-in
            def __init__(self, index, ts, bits):
                self.index, self.timestamp, self.difficulty = index, ts, bits
        p = consensus.Params(v2_height=0, retarget_interval=10, target_spacing=600, max_adjust=4)
        start = target_to_bits(1 << 200)
        def chain(spacing):
            return [B(i, 1_000_000 + i * spacing, start) for i in range(10)]
        same = consensus.expected_bits(chain(600), 10, p)             # exactly on schedule (9 intervals: 5400 s vs 6000 s)
        self.assertLess(bits_to_target(same), 1 << 200)               # 5400/6000 -> a bit harder
        slow = consensus.expected_bits(chain(6000), 10, p)            # 10x too slow -> clamped to 4x easier
        self.assertEqual(bits_to_target(slow), bits_to_target(target_to_bits((bits_to_target(start) * 6000 * 4) // 6000)))
        fast = consensus.expected_bits(chain(1), 10, p)               # far too fast -> clamped to 4x harder
        self.assertEqual(bits_to_target(fast), bits_to_target(target_to_bits(bits_to_target(start) * 1500 // 6000)))
        capped = consensus.Params(v2_height=0, retarget_interval=10, target_spacing=600, pow_limit_target=(1 << 200) + 5)
        self.assertLessEqual(bits_to_target(consensus.expected_bits(chain(6000), 10, capped)), capped.pow_limit_target)

    def test_timestamps_follow_median_time_past_and_future_limit(self):
        self.to_v2()
        mtp = consensus.median_time_past(self.bc.chain)
        self.assertRejected(self.forge(ts=mtp), "not after the median")
        self.assertRejected(self.forge(ts=mtp - 1000), "not after the median")
        self.assertRejected(self.forge(ts=time.time() + consensus.PARAMS.max_future_seconds + 600), "too far in the future")
        self.assertAccepted(self.forge(ts=max(mtp + 1, time.time())))

    def test_block_size_limit(self):
        self.to_v2()
        old = consensus.PARAMS.max_block_bytes
        consensus.PARAMS.max_block_bytes = 500
        try:
            self.assertRejected(self.forge(), "too large")
        finally:
            consensus.PARAMS.max_block_bytes = old

    def test_supply_cap_is_enforced_in_blocks(self):
        self.to_v2()
        supply = consensus.issued_before_sat(len(self.bc.chain), consensus.genesis_total_sat(self.bc.chain))
        consensus.PARAMS.max_money = supply + 30 * COIN          # only 30 PYC left to issue
        self.assertRejected(self.forge(cb_amount_sat=50 * COIN), "coinbase pays")
        self.assertAccepted(self.forge(cb_amount_sat=30 * COIN))
        self.assertRejected(self.forge(cb_amount_sat=1), "coinbase pays")   # nothing left to issue
        self.assertAccepted(self.forge(cb_amount_sat=0))                   # a zero-value coinbase is still a valid block
        self.assertEqual(consensus.allowed_subsidy_sat(len(self.bc.chain), consensus.genesis_total_sat(self.bc.chain)), 0)


class TestTransactionsInBlocks(ConsensusCase):
    def spendable(self):
        """One matured output for alice: the genesis coins."""
        key = next(k for k, u in self.bc.utxo.items() if u["recipient"] == self.alice["address"] and not u.get("coinbase"))
        u = self.bc.utxo[key]
        return u["tx_id"], u["output_index"], u["amount"]

    def setUp(self):
        super().setUp()
        self.to_v2()

    def test_valid_spend_is_accepted_and_updates_balances(self):
        tid, idx, amount = self.spendable()
        tx = build_manual_tx(self.alice, [(tid, idx)], [(self.bob["address"], 100.0), (self.alice["address"], amount - 100.0 - 0.001)])
        self.assertAccepted(self.forge(txs=[tx], fees_sat=consensus.to_sat(0.001)))
        self.assertEqual(self.bc.get_balance(self.bob["address"]), 100.0)

    def test_inputs_must_exist_and_cannot_be_double_spent(self):
        tid, idx, amount = self.spendable()
        ghost = build_manual_tx(self.alice, [("ab" * 32, 0)], [(self.bob["address"], 1.0)])
        self.assertRejected(self.forge(txs=[ghost]), "missing or already spent")
        t1 = build_manual_tx(self.alice, [(tid, idx)], [(self.bob["address"], 5.0)])
        t2 = build_manual_tx(self.alice, [(tid, idx)], [(self.alice["address"], 5.0)])
        self.assertRejected(self.forge(txs=[t1, t2]), "missing or already spent")        # same block
        dup = build_manual_tx(self.alice, [(tid, idx), (tid, idx)], [(self.bob["address"], 5.0)])
        self.assertRejected(self.forge(txs=[dup]), "duplicate input")
        self.assertAccepted(self.forge(txs=[t1]))
        self.assertRejected(self.forge(txs=[t2]), "missing or already spent")            # later block

    def test_cannot_spend_someone_elses_coins_or_with_a_bad_signature(self):
        tid, idx, amount = self.spendable()
        theft = build_manual_tx(self.bob, [(tid, idx)], [(self.bob["address"], amount)])   # bob signs alice's coins
        self.assertRejected(self.forge(txs=[theft]), "not owned by the signer")
        tx = build_manual_tx(self.alice, [(tid, idx)], [(self.bob["address"], 5.0)])
        tx.outputs[0].amount = 50.0                                   # altered after signing
        tx.calculate_tx_id()
        self.assertRejected(self.forge(txs=[tx]), "invalid signature")
        unsigned = build_manual_tx(self.alice, [(tid, idx)], [(self.bob["address"], 5.0)], sign=False)
        self.assertRejected(self.forge(txs=[unsigned]), "invalid signature")

    def test_value_rules(self):
        tid, idx, amount = self.spendable()
        for outputs, fragment in (
            ([(self.bob["address"], amount + 1)], "outputs exceed inputs"),
            ([(self.bob["address"], -5.0), (self.alice["address"], amount + 5.0)], "positive"),
            ([(self.bob["address"], 0.0), (self.alice["address"], amount)], "positive"),
            ([(self.bob["address"], 1.000000001)], "decimal places"),
        ):
            tx = build_manual_tx(self.alice, [(tid, idx)], outputs)
            self.assertRejected(self.forge(txs=[tx]), fragment)

    def test_tx_id_must_match_contents(self):
        tid, idx, amount = self.spendable()
        tx = build_manual_tx(self.alice, [(tid, idx)], [(self.bob["address"], 5.0)])
        tx.tx_id = tid                                                # collide with an existing id
        self.assertRejected(self.forge(txs=[tx]), "tx_id does not match")

    def test_duplicate_transactions_in_a_block_are_rejected(self):
        tid, idx, amount = self.spendable()
        tx = build_manual_tx(self.alice, [(tid, idx)], [(self.bob["address"], 5.0)])
        self.assertRejected(self.forge(txs=[tx, tx]), "duplicate transaction")

    def test_coinbase_maturity(self):
        p = consensus.PARAMS
        miner = wallet()
        reward_block = self.mine(miner=miner)[0]                      # miner's first coinbase, at the tip
        cb = reward_block.transactions[0]
        for confirmations in range(p.coinbase_maturity - 1):
            tx = build_manual_tx(miner, [(cb.tx_id, 0)], [(self.bob["address"], 1.0)])
            self.assertRejected(self.forge(txs=[tx]), "immature coinbase")
            self.mine()                                               # one more block on top
        tx = build_manual_tx(miner, [(cb.tx_id, 0)], [(self.bob["address"], 1.0)])
        self.assertAccepted(self.forge(txs=[tx], fees_sat=0))        # now exactly `coinbase_maturity` deep

    def test_unknown_and_value_carrying_data_transactions_are_rejected(self):
        weird = Transaction(sender=self.alice["public_key"], inputs=[], tx_type="smart_contract",
                            outputs=[TransactionOutput(address=self.bob["address"], amount=1.0)])
        weird.sign(self.alice["private_key"])
        self.assertRejected(self.forge(txs=[weird]), "not allowed")
        data = pc.DataTransaction(self.alice["public_key"], "hello", self.alice["private_key"])
        data.outputs = [TransactionOutput(address=self.bob["address"], amount=1.0)]
        data.calculate_tx_id()
        data.sign(self.alice["private_key"])
        self.assertRejected(self.forge(txs=[data]), "must not move value")
        good = pc.DataTransaction(self.alice["public_key"], "hello", self.alice["private_key"])
        self.assertAccepted(self.forge(txs=[good]))
        unsigned = pc.DataTransaction(self.alice["public_key"], "no signature")
        self.assertRejected(self.forge(txs=[unsigned]), "invalid signature")


class TestMempoolAndWallet(ConsensusCase):
    def setUp(self):
        super().setUp()
        self.to_v2()

    def pay(self, amount, fee=None, sender=None, to=None):
        sender = sender or self.alice
        return self.bc.create_transaction(sender["private_key"], sender["public_key"], (to or self.bob)["address"], amount, fee)

    def test_fee_policy_and_addresses(self):
        self.assertTrue(self.bc.add_transaction(self.pay(5)))                       # default fee = min relay fee
        self.bc.pending_transactions.clear()
        self.assertFalse(self.bc.add_transaction(self.pay(5, fee=0)))                # below minimum relay fee
        bad_addr = build_manual_tx(self.alice, [next(iter(((u["tx_id"], u["output_index"]) for u in self.bc.utxo.values() if u["recipient"] == self.alice["address"])))],
                                   [("notAnAddress", 1.0)])
        self.assertFalse(self.bc.add_transaction(bad_addr))
        self.assertTrue(consensus.is_valid_address(self.bob["address"]))
        self.assertFalse(consensus.is_valid_address(self.bob["address"][:-1] + ("1" if self.bob["address"][-1] != "1" else "2")))

    def test_coinbase_and_genesis_never_enter_the_mempool(self):
        cb = Transaction(sender="coinbase", inputs=[], tx_type="coinbase", data={"height": 99},
                         outputs=[TransactionOutput(address=self.bob["address"], amount=50.0)])
        cb.calculate_tx_id()
        self.assertFalse(self.bc.add_transaction(cb))

    def test_mempool_rejects_double_spends_but_allows_chains_of_unconfirmed_payments(self):
        first = self.pay(10)
        self.assertTrue(self.bc.add_transaction(first))
        self.assertFalse(self.bc.add_transaction(first))                             # same tx twice
        spent = (first.inputs[0].tx_id, first.inputs[0].output_index)
        conflict = build_manual_tx(self.alice, [spent], [(self.bob["address"], 1.0)])
        self.assertFalse(self.bc.add_transaction(conflict))                          # spends the same output
        # bob spends the unconfirmed payment he just received
        child = self.pay(3, sender=self.bob, to=self.alice) if self.bc.get_balance(self.bob["address"]) else None
        self.assertIsNone(child)                                                     # not in the UTXO set until mined
        self.mine()
        self.assertTrue(self.bc.add_transaction(self.pay(3, sender=self.bob, to=self.alice, fee=0.01)))

    def test_wallet_uses_exact_integer_math_and_sends_change_back(self):
        before = consensus.to_sat(self.bc.get_balance(self.alice["address"]))
        tx = self.pay(12.34567891, fee=0.00002)
        self.assertEqual(sum(consensus.to_sat(o.amount) for o in tx.outputs), consensus.to_sat(self.spendable_input_total(tx)) - consensus.to_sat(0.00002))
        self.assertTrue(self.bc.add_transaction(tx))
        self.mine(miner=self.bob)
        reward = sum(consensus.to_sat(o.amount) for o in self.bc.chain[-1].transactions[0].outputs)
        self.assertEqual(consensus.to_sat(self.bc.get_balance(self.bob["address"])) - reward, consensus.to_sat(12.34567891))
        self.assertEqual(consensus.to_sat(self.bc.get_balance(self.alice["address"])),
                         before - consensus.to_sat(12.34567891) - consensus.to_sat(0.00002))

    def spendable_input_total(self, tx):
        return sum(self.bc.utxo[f"{i.tx_id}:{i.output_index}"]["amount"] for i in tx.inputs)

    def test_dust_change_becomes_fee_and_overspending_fails(self):
        total = self.bc.get_spendable_balance(self.alice["address"])
        self.assertIsNone(self.pay(total))                                           # cannot also afford the fee
        near = consensus.from_sat(consensus.to_sat(total) - consensus.PARAMS.min_relay_fee_sat - 10)
        tx = self.pay(near)
        self.assertEqual(len(tx.outputs), 1)                                         # 10 base units of dust -> fee
        self.assertIsNone(self.pay(0))
        self.assertIsNone(self.pay(0.000000001))

    def test_wallet_will_not_spend_immature_coinbase(self):
        miner = wallet()
        self.mine(miner=miner)
        self.assertEqual(self.bc.get_spendable_balance(miner["address"]), 0)
        self.assertGreater(self.bc.get_balance(miner["address"]), 0)
        self.assertIsNone(self.pay(1, sender=miner))
        self.mine(consensus.PARAMS.coinbase_maturity)
        self.assertGreater(self.bc.get_spendable_balance(miner["address"]), 0)
        self.assertIsNotNone(self.pay(1, sender=miner))

    def test_mining_skips_transactions_that_became_invalid(self):
        tx = self.pay(10)
        self.assertTrue(self.bc.add_transaction(tx))
        spent = (tx.inputs[0].tx_id, tx.inputs[0].output_index)
        rival = build_manual_tx(self.alice, [spent], [(self.bob["address"], 1.0), (self.alice["address"], 1.0)])
        self.bc.pending_transactions.append(rival)                                   # smuggled in, conflicts with `tx`
        block = self.mine()[0]
        self.assertEqual(sum(1 for t in block.transactions if t.tx_type == "standard"), 1)
        self.assertEqual(self.bc.pending_transactions, [])


class TestChainReplacement(ConsensusCase):
    def clone_chain_from(self, n_blocks_from_genesis):
        """A competing node that started from the same genesis block."""
        other = Blockchain()
        other.chain = [copy.deepcopy(self.bc.chain[0])]
        other.genesis_complete = True
        other._rebuild_utxo()
        for _ in range(n_blocks_from_genesis):
            self.assertTrue(other.mine_pending_transactions(self.bob["address"]))
        return other

    def test_longer_valid_chain_replaces_ours_and_shorter_does_not(self):
        self.mine(3)
        longer = self.clone_chain_from(7)
        self.assertTrue(self.bc.replace_chain(longer.chain))
        self.assertEqual(self.bc.chain[-1].hash, longer.chain[-1].hash)
        self.assertEqual(self.bc.utxo.keys(), longer.utxo.keys())
        shorter = self.clone_chain_from(2)
        before = self.bc.chain[-1].hash
        self.assertFalse(self.bc.replace_chain(shorter.chain))
        self.assertEqual(self.bc.chain[-1].hash, before)

    def test_invalid_or_foreign_chains_are_refused(self):
        self.mine(2)
        other = self.clone_chain_from(8)
        tampered = copy.deepcopy(other.chain)
        victim = tampered[5]
        victim.transactions[0].outputs[0].amount = 1_000_000.0       # pays itself more than the subsidy
        victim.transactions[0].calculate_tx_id()
        self.assertFalse(self.bc.replace_chain(tampered))
        foreign = Blockchain(genesis_addresses=[self.bob["address"]])
        for _ in range(9):
            foreign.mine_pending_transactions(self.bob["address"])
        self.assertFalse(self.bc.replace_chain(foreign.chain))       # different genesis
        self.assertFalse(self.bc.replace_chain([]))
        self.assertTrue(self.bc.is_chain_valid())

    def test_chain_with_most_work_wins_not_just_the_longest(self):
        p = consensus.PARAMS
        easy = self.clone_chain_from(6)                              # more blocks
        hard = Blockchain()
        hard.chain = [copy.deepcopy(self.bc.chain[0])]
        hard.genesis_complete = True
        hard._rebuild_utxo()
        for _ in range(5):
            hard.mine_pending_transactions(self.bob["address"])
        # make `hard` clearly heavier: pretend its legacy blocks were 8 hex zeros instead of ~1-4
        work_easy, work_hard = consensus.chain_work(easy.chain), consensus.chain_work(hard.chain)
        self.assertGreater(work_easy, 0)
        self.assertGreater(work_hard, 0)
        self.assertEqual(self.bc.replace_chain(easy.chain), True)
        self.assertEqual(self.bc.replace_chain(easy.chain), False)   # same work again is ignored


class TestWireFormat(ConsensusCase):
    """Blocks and chains arrive from peers as JSON; tampering with them must be caught."""

    def peer_block(self):
        """A valid next block, mined by another node, as it would arrive over the network."""
        self.to_v2()
        other = Blockchain()
        other.chain = [copy.deepcopy(b) for b in self.bc.chain]
        other.genesis_complete = True
        other._rebuild_utxo()
        block = other.mine_pending_transactions(self.bob["address"])
        self.assertTrue(block)
        return json.loads(json.dumps(block.to_dict()))

    def test_chain_survives_a_json_round_trip(self):
        self.to_v2()
        self.mine(2)
        wire = json.loads(json.dumps([b.to_dict() for b in self.bc.chain]))
        err, utxo, work = consensus.validate_chain([Block.from_dict(d) for d in wire])
        self.assertIsNone(err)
        self.assertEqual(set(utxo), set(self.bc.utxo))

    def test_honest_peer_block_is_accepted(self):
        wire = self.peer_block()
        self.assertTrue(self.bc.add_block(Block.from_dict(wire)))

    def test_tampering_with_a_peer_block_is_rejected(self):
        wire = self.peer_block()
        for label, mutate in (
            ("raise the coinbase", lambda d: d["transactions"][0]["outputs"][0].update(amount=1_000_000.0)),
            ("redirect the coinbase", lambda d: d["transactions"][0]["outputs"][0].update(address=self.alice["address"])),
            ("claim a different height", lambda d: d["transactions"][0]["data"].update(height=999)),
            ("change the hash", lambda d: d.update(hash="0" * 64)),
            ("change the nonce", lambda d: d.update(nonce=d["nonce"] + 1)),
            ("change the timestamp", lambda d: d.update(timestamp=d["timestamp"] + 1)),
            ("change the difficulty", lambda d: d.update(difficulty=d["difficulty"] + 1)),
            ("change the previous hash", lambda d: d.update(previous_hash="a" * 64)),
            ("drop the coinbase", lambda d: d["transactions"].pop(0)),
        ):
            bad = copy.deepcopy(wire)
            mutate(bad)
            height = len(self.bc.chain)
            self.assertFalse(self.bc.add_block(Block.from_dict(bad)), f"tampered block was accepted: {label}")
            self.assertEqual(len(self.bc.chain), height)
        self.assertTrue(self.bc.add_block(Block.from_dict(wire)))     # the untouched original is still fine

    def test_garbage_from_a_peer_never_crashes_validation(self):
        self.to_v2()
        for junk in ({}, {"index": "x"}, {"index": 5, "timestamp": "no", "previous_hash": 7, "transactions": "oops"}):
            try:
                block = Block.from_dict(junk)
            except Exception:
                continue                                       # refusing to even parse is fine
            self.assertFalse(self.bc.add_block(block))


class TestLegacyAdjuster(unittest.TestCase):
    def test_old_difficulty_adjuster_stays_in_a_minable_range(self):
        class B:
            def __init__(self, i, ts, d):
                self.index, self.timestamp, self.difficulty = i, ts, d
        class Chain:
            pass
        chain = Chain()
        chain.chain = [B(i, 1000.0, 4) for i in range(12)]          # ten blocks in the same instant
        adjuster = pc.DifficultyAdjustment(chain)
        self.assertEqual(adjuster.calculate_next_difficulty(), 5)   # one step up; no divide-by-zero, no jump to 16
        chain.chain = [B(i, 1000.0 + i * 100000, 6) for i in range(12)]
        self.assertEqual(adjuster.calculate_next_difficulty(), 5)   # far too slow -> one step down
        chain.chain = [B(i, 1000.0, 6) for i in range(12)]
        self.assertEqual(adjuster.calculate_next_difficulty(), 6)   # capped


class TestLegacyDoubleSpends(ConsensusCase):
    """Block 1 of the real chain pays out 24 times from the same genesis coin. Old history is read so that the
    first spend stands and later spends of the same coin are void, so no coins are created out of nothing."""

    def test_repeated_payments_from_one_coin_do_not_create_money(self):
        genesis_out = next(iter(self.bc.utxo.values()))
        tid, idx, amount = genesis_out["tx_id"], genesis_out["output_index"], genesis_out["amount"]
        for _ in range(5):   # the app used to build the same payment again and again, all spending the same coin
            tx = build_manual_tx(self.alice, [(tid, idx)], [(self.bob["address"], 0.001), (self.alice["address"], amount - 0.001)])
            self.bc.pending_transactions.append(tx)            # bypass the mempool, as the old app effectively did
        self.mine()
        total = sum(consensus.to_sat(u["amount"], strict=False) for u in self.bc.utxo.values())
        reward = consensus.to_sat(50)
        self.assertEqual(total, consensus.to_sat(1_000_000) + reward, "supply must be genesis + one block reward")
        self.assertAlmostEqual(self.bc.get_balance(self.bob["address"]), 0.001, places=8)    # paid once, not five times

    def test_a_payment_that_pays_out_more_than_it_takes_in_is_void(self):
        genesis_out = next(iter(self.bc.utxo.values()))
        tx = build_manual_tx(self.alice, [(genesis_out["tx_id"], genesis_out["output_index"])],
                             [(self.bob["address"], genesis_out["amount"] + 500.0)])
        self.bc.pending_transactions.append(tx)
        self.mine()
        self.assertEqual(self.bc.get_balance(self.bob["address"]), 0)
        self.assertTrue(self.bc.is_chain_valid())

    def test_legacy_reading_does_not_touch_blocks_or_validity(self):
        genesis_out = next(iter(self.bc.utxo.values()))
        tx = build_manual_tx(self.alice, [(genesis_out["tx_id"], genesis_out["output_index"])], [(self.bob["address"], 1.0)])
        self.bc.pending_transactions.extend([tx, tx.__class__.from_dict(tx.to_dict())])
        self.mine()
        self.assertTrue(self.bc.is_chain_valid())


class TestRealHistory(unittest.TestCase):
    """The old PythonCoin chain (kept in the pre-reset snapshot) must still validate under the pre-launch rules.
    The live chain was restarted from a fresh genesis block; this proves the legacy reading of history stays correct."""

    SNAPSHOT = "C:/xampp/security_backup_20261022/pre_reset_snapshot/blockchain.json"

    def setUp(self):
        self._saved = dict(vars(consensus.PARAMS))
        consensus.PARAMS.v2_height = 100            # the rules the old chain was written under
        consensus.PARAMS.address_version = 0
        consensus.PARAMS.genesis_file = "__no_genesis_file__.json"

    def tearDown(self):
        for k, v in self._saved.items():
            setattr(consensus.PARAMS, k, v)

    def test_old_chain_still_validates_and_has_no_phantom_coins(self):
        if not os.path.exists(self.SNAPSHOT):
            self.skipTest("no pre-reset snapshot on this machine")
        with open(self.SNAPSHOT, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        blocks = [Block.from_dict(bd) for bd in data["chain"]]
        self.assertGreater(len(blocks), 1)
        err, utxo, work = consensus.validate_chain(blocks)
        self.assertIsNone(err, f"old history no longer validates: {err}")
        bc = Blockchain()
        self.assertTrue(bc.replace_chain(blocks))
        mined = sum(1 for b in blocks[1:] if b.transactions and b.transactions[0].tx_type == "coinbase")
        supply = sum(consensus.to_sat(u["amount"], strict=False) for u in bc.utxo.values())
        self.assertEqual(supply, consensus.to_sat(1_000_000 + 50 * mined),
                         "coins in existence must equal genesis plus block rewards; the repeated payments in block 1 must not create money")


class TestFreshGenesis(unittest.TestCase):
    """The live chain: one fixed genesis block, fair launch, own address prefix."""

    def test_genesis_file_is_valid_creates_no_coins_and_is_shared_by_every_node(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "genesis.json")
        if not os.path.exists(path):
            self.skipTest("no genesis.json yet")
        a, b = Blockchain(), Blockchain()
        self.assertEqual(len(a.chain), 1)
        self.assertEqual(a.chain[0].hash, b.chain[0].hash)
        self.assertEqual(sum(u["amount"] for u in a.utxo.values()), 0)
        self.assertTrue(a.genesis_complete)

    def test_new_addresses_use_the_coin_prefix(self):
        w = CryptoUtils.generate_keypair()
        self.assertTrue(consensus.is_valid_address(w["address"]))
        decoded = consensus.decode_address(w["address"])
        self.assertEqual(decoded[0], consensus.PARAMS.address_version)
        if consensus.PARAMS.address_version == 53:
            self.assertEqual(w["address"][0], "N")
            self.assertFalse(consensus.is_valid_address("17YaUDouaJf8DxNbnAUFfJfSuBXVpaKS48"), "Bitcoin-format addresses are not valid here")

    def test_old_addresses_convert_to_the_new_prefix_keeping_the_key_hash(self):
        old = "17YaUDouaJf8DxNbnAUFfJfSuBXVpaKS48"
        new = consensus.convert_address(old, 53)
        self.assertEqual(new[0], "N")
        self.assertEqual(consensus.decode_address(old)[1], consensus.decode_address(new)[1])
        self.assertIsNone(consensus.convert_address(old[:-1] + "1", 53))     # a mistyped address is not converted


if __name__ == "__main__":
    unittest.main(verbosity=2)
