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


if __name__ == "__main__":
    unittest.main(verbosity=2)
