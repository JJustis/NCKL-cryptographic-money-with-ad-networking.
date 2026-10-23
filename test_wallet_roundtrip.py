"""The wallet app saves the chain to blockchain.json and rebuilds it on the next start. That round trip must not change
anything the consensus rules check (it once dropped the coinbase's `data`, which made every mined block invalid).

    python -m unittest test_wallet_roundtrip -v
"""
import inspect
import json
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import consensus
import pythoncoin as pc


def _reconstruct():
    import pyqt
    for _, cls in inspect.getmembers(pyqt, inspect.isclass):
        if "reconstruct_transaction" in cls.__dict__:
            return cls.__dict__["reconstruct_transaction"]
    raise unittest.SkipTest("reconstruct_transaction not found")


class TestWalletRoundTrip(unittest.TestCase):
    def test_coinbase_survives_save_and_reload(self):
        wallet = pc.CryptoUtils.generate_keypair()
        reconstruct = _reconstruct()
        for height in (1, 2, 210000):
            tx = pc.Transaction(sender="coinbase", inputs=[], outputs=[pc.TransactionOutput(address=wallet["address"], amount=50.0)],
                                tx_type="coinbase", data={"height": height})        # exactly how Block.mine_block builds it
            tx.calculate_tx_id()
            saved = json.loads(json.dumps(tx.to_dict()))      # what blockchain.json holds
            rebuilt = reconstruct(object(), saved)            # what the wallet does on start
            self.assertEqual(rebuilt.data, {"height": height}, "the coinbase data (block height) must survive")
            self.assertEqual(rebuilt.compute_tx_id(), rebuilt.tx_id, "the id must still match the contents")

    def test_the_saved_chain_file_validates(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blockchain.json")
        if not os.path.exists(path):
            self.skipTest("no blockchain.json here")
        blocks = [pc.Block.from_dict(b) for b in json.load(open(path, encoding="utf-8"))["chain"]]
        error = consensus.validate_chain(blocks)[0]
        self.assertIsNone(error, error)


class _Sig:
    def __init__(self): self.n = 0
    def emit(self, *a): self.n += 1


class _FakeWallet:
    """Just enough of the wallet to run its verification code without a window."""
    def __init__(self, chain):
        self.blockchain = type("B", (), {"chain": chain, "utxo": {}})()
        self.verification_results = {}
        self.lines = []
        self._verify_done_signal = _Sig()
    def audit_log(self, message): self.lines.append(message)
    def _verify_against_mysql(self): pass


class TestChainVerificationButton(unittest.TestCase):
    """'Verify Entire Blockchain' once killed the wallet: it built a string of "0" * difficulty, and on v2 blocks the
    difficulty is the compact target (about 500 million), and it wrote to the window from a worker thread."""

    def test_big_difficulty_does_not_allocate_a_giant_string(self):
        import pyqt
        cls = next(c for _, c in inspect.getmembers(pyqt, inspect.isclass) if "_verify_block_comprehensive" in c.__dict__)
        fake = _FakeWallet([])
        prev = type("Blk", (), {"hash": "p"})()
        block = type("Blk", (), {"index": 5, "previous_hash": "p", "hash": "h", "difficulty": 503382015, "transactions": []})()
        fake.blockchain.chain = [None] * 4 + [prev, block]       # passes the index and previous-hash checks, reaches the proof-of-work line
        import tracemalloc
        tracemalloc.start()
        cls.__dict__["_verify_block_comprehensive"](fake, block, 5)          # fails later on the fake block's missing methods: that is fine
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        self.assertLess(peak, 50_000_000)

    def test_verification_uses_the_consensus_rules_and_signals_when_done(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blockchain.json")
        if not os.path.exists(path):
            self.skipTest("no blockchain.json here")
        import pyqt
        cls = next(c for _, c in inspect.getmembers(pyqt, inspect.isclass) if "_perform_full_verification" in c.__dict__)
        chain = [pc.Block.from_dict(b) for b in json.load(open(path, encoding="utf-8"))["chain"]]
        fake = _FakeWallet(chain)
        cls.__dict__["_perform_full_verification"](fake)
        self.assertEqual(fake._verify_done_signal.n, 1, "the window is told to re-enable the button through a signal")
        self.assertTrue(all(v["valid"] for v in fake.verification_results.values()))


class TestMyAdsTable(unittest.TestCase):
    """The Create Ad tab's table must show the clicks recorded in the database (website clicks never pass through
    the wallet's in-memory click events)."""

    def _run(self, rows):
        import pyqt
        from PyQt5.QtWidgets import QApplication, QTableWidget
        TestMyAdsTable._app = QApplication.instance() or QApplication([])      # must outlive the widgets
        cls = next(c for _, c in inspect.getmembers(pyqt, inspect.isclass) if "update_my_ads_table" in c.__dict__)

        class FakeDb:
            def execute_query(self, query, params=None, fetch=False):
                return rows
        ad = type("Ad", (), {"id": "ad-1", "title": "T", "description": "d", "category": "business", "payout_rate": 0.001,
                             "expires_at": "2999-01-01T00:00:00", "advertiser_address": "Naddr"})()
        fake = type("W", (), {})()
        fake.my_ads_table = QTableWidget()
        fake.my_ads_table.setColumnCount(7)
        fake.ads = [ad]
        fake.wallet = type("Wal", (), {"address": "Naddr"})()
        fake.click_events = []
        fake.db_manager = FakeDb()
        fake._ad_click_stats = lambda ids: cls.__dict__["_ad_click_stats"](fake, ids)
        cls.__dict__["update_my_ads_table"](fake)
        return fake.my_ads_table

    def test_clicks_and_spent_come_from_the_database(self):
        table = self._run([{"ad_id": "ad-1", "clicks": 7, "own_clicks": 3, "charged_sat": 400000}])
        self.assertEqual(table.item(0, 3).text(), "7")
        self.assertIn("3 of your own", table.item(0, 3).toolTip())
        self.assertEqual(table.item(0, 4).text(), "0.00400000")

    def test_an_ad_with_no_clicks_shows_zero(self):
        table = self._run([])
        self.assertEqual(table.item(0, 3).text(), "0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
