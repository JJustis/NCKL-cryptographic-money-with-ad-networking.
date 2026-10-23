"""Deposits: an advertiser pays the network wallet on-chain and is credited once the payment is confirmed.

    python -m unittest test_economy_deposits -v
"""
import unittest

import consensus
import economy
from test_consensus import ConsensusCase


class TestDeposits(ConsensusCase):
    def setUp(self):
        super().setUp()
        self.advertiser, self.network = self.alice, self.bob      # alice pays, bob's wallet is the network wallet
        self.conn = economy.connect()
        self._wipe()
        self.to_v2()

    def tearDown(self):
        self._wipe()
        self.conn.close()
        super().tearDown()

    def _wipe(self):
        cur = self.conn.cursor()
        for table in ("advertiser_ledger", "advertiser_deposits", "advertiser_accounts"):
            col = "address"
            cur.execute(f"DELETE FROM {table} WHERE {col} = %s", (self.advertiser["address"],))
        self.conn.commit()
        cur.close()

    def balance(self):
        cur = self.conn.cursor()
        cur.execute("SELECT balance_sat, deposited_sat FROM advertiser_accounts WHERE address = %s", (self.advertiser["address"],))
        row = cur.fetchone()
        cur.close()
        self.conn.commit()
        return row

    def pay(self, amount, sender=None, to=None):
        sender = sender or self.advertiser
        tx = self.bc.create_transaction(sender["private_key"], sender["public_key"], (to or self.network)["address"], amount)
        self.assertTrue(self.bc.add_transaction(tx))
        return tx

    def test_deposit_is_credited_only_after_enough_confirmations(self):
        need = economy.settings()["deposit_confirmations"]
        self.pay(5)
        self.mine()                                            # the payment is in this block: 1 confirmation
        self.assertEqual(economy.credit_deposits(self.bc, self.network["address"], self.conn), [])
        self.assertIsNone(self.balance())
        self.mine(need - 1)                                    # now it has `need` confirmations
        credited = economy.credit_deposits(self.bc, self.network["address"], self.conn)
        self.assertEqual(len(credited), 1)
        self.assertEqual(credited[0][1], self.advertiser["address"])
        self.assertEqual(credited[0][2], consensus.to_sat(5))
        self.assertEqual(self.balance(), (consensus.to_sat(5), consensus.to_sat(5)))

    def test_scanning_again_never_credits_twice(self):
        need = economy.settings()["deposit_confirmations"]
        self.pay(2.5)
        self.mine(need)
        economy.credit_deposits(self.bc, self.network["address"], self.conn)
        for _ in range(3):
            self.assertEqual(economy.credit_deposits(self.bc, self.network["address"], self.conn), [])
        self.assertEqual(self.balance()[0], consensus.to_sat(2.5))

    def test_two_deposits_add_up_and_each_is_in_the_statement(self):
        need = economy.settings()["deposit_confirmations"]
        self.pay(1)
        self.mine()
        self.pay(2)
        self.mine(need)
        economy.credit_deposits(self.bc, self.network["address"], self.conn)
        self.assertEqual(self.balance()[0], consensus.to_sat(3))
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM advertiser_ledger WHERE address = %s AND kind = 'deposit'", (self.advertiser["address"],))
        self.assertEqual(cur.fetchone()[0], 2)
        cur.close()
        self.conn.commit()

    def test_the_network_wallet_paying_out_is_not_a_deposit(self):
        need = economy.settings()["deposit_confirmations"]
        self.mine(consensus.PARAMS.coinbase_maturity)          # the network wallet needs spendable coins; fund it first
        self.pay(10)
        self.mine(need)
        economy.credit_deposits(self.bc, self.network["address"], self.conn)
        before = self.balance()
        payout = self.bc.create_transaction(self.network["private_key"], self.network["public_key"], self.advertiser["address"], 1)
        self.assertTrue(self.bc.add_transaction(payout))       # a publisher payout (here to the advertiser's address)
        self.mine(need)
        economy.credit_deposits(self.bc, self.network["address"], self.conn)
        self.assertEqual(self.balance(), before)

    def test_block_listener_credits_automatically_when_the_block_is_deep_enough(self):
        need = economy.settings()["deposit_confirmations"]
        self.bc.on_block_added.append(economy.block_listener(lambda: self.bc, lambda: self.network["address"]))
        self.pay(4)
        self.mine(need)
        self.assertEqual(self.balance()[0], consensus.to_sat(4))

    def test_retention_anonymises_ip_addresses(self):
        self.assertEqual(economy.anonymise_ip("203.0.113.57"), "203.0.113.0")
        self.assertEqual(economy.anonymise_ip("2001:db8:abcd:12:0:0:0:1"), "2001:db8:abcd::")
        self.assertEqual(economy.anonymise_ip(""), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
