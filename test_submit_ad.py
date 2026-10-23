"""Advertisers push signed ads to the server (submit_ad.php).  Needs Apache + MariaDB running.

    python -m unittest test_submit_ad -v
"""
import base64
import glob
import json
import os
import tempfile
import time
import unittest
import uuid

import requests

import ad_publisher
import consensus
import economy
import pythoncoin as pc

URL = "http://localhost/livepy/pythoncoin/submit_ad.php"
HERE = os.path.dirname(os.path.abspath(__file__))
PENDING = os.path.join(HERE, "ads_storage", "pending")
ACTIVE = os.path.join(HERE, "ads_storage", "active")
PNG = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64).decode()


def clear_rate_limits():
    for base in {tempfile.gettempdir(), r"C:\Windows\Temp", os.environ.get("TEMP", "")}:
        for f in glob.glob(os.path.join(base, "pyc_ratelimit", "*.json")):
            try:
                os.remove(f)
            except OSError:
                pass


ECON = os.path.join(HERE, "economy.json")
SHOP_SEC = "a1" * 16


class TestSubmitAd(unittest.TestCase):
    """Runs against a scratch shop database (never the real btcshop one): economy.json is pointed at it for the run."""

    @classmethod
    def setUpClass(cls):
        with open(ECON, "r", encoding="utf-8") as fh:
            cls._econ_original = fh.read()
        cls._shop_dir = tempfile.mkdtemp(prefix="nckl_shop_")
        os.makedirs(os.path.join(cls._shop_dir, "data"))
        cls.shop_db = os.path.join(cls._shop_dir, "data", "shop.sqlite")
        cls._shop_exec("CREATE TABLE orders(id INTEGER PRIMARY KEY AUTOINCREMENT, sec_hash TEXT NOT NULL, product TEXT NOT NULL, "
                       "sats INTEGER NOT NULL, created INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending', txid TEXT, paid_at INTEGER)")
        econ = json.loads(cls._econ_original)
        econ.update({"ad_upload_fee_required": True, "btcshop_db": cls.shop_db, "btcshop_product": "ad-upload"})
        with open(ECON, "w", encoding="utf-8") as fh:
            json.dump(econ, fh, indent=2)
        cls.terms_version = ad_publisher.fetch_requirements(URL)["terms_version"]

    @classmethod
    def tearDownClass(cls):
        with open(ECON, "w", encoding="utf-8") as fh:
            fh.write(cls._econ_original)
        import shutil
        shutil.rmtree(cls._shop_dir, ignore_errors=True)

    @classmethod
    def _shop_exec(cls, sql, args=()):
        import sqlite3
        con = sqlite3.connect(cls.shop_db)
        cur = con.execute(sql, args)
        con.commit()
        last = cur.lastrowid
        con.close()
        return last

    def new_order(self, status="paid", product="ad-upload"):
        import hashlib
        return self._shop_exec("INSERT INTO orders(sec_hash,product,sats,created,status) VALUES(?,?,?,?,?)",
                               (hashlib.sha256(SHOP_SEC.encode()).hexdigest(), product, 3000, int(time.time()), status))

    def accept_terms(self, address):
        import hashlib
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS advertiser_agreements (id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, address VARCHAR(64) NOT NULL, "
                    "terms_version INT NOT NULL, legal_name VARCHAR(200) NOT NULL, contact_email VARCHAR(200) NOT NULL, "
                    "accepted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, ip_address VARCHAR(45) NULL, user_agent VARCHAR(255) NULL, "
                    "source VARCHAR(20) NOT NULL DEFAULT 'web', UNIQUE KEY uq_address_version (address, terms_version))")
        cur.execute("INSERT IGNORE INTO advertiser_agreements (address, terms_version, legal_name, contact_email, source) VALUES (%s,%s,'Test','t@example.com','test')",
                    (address, self.terms_version))
        self.conn.commit()
        cur.close()

    def setUp(self):
        clear_rate_limits()
        self.wallet = pc.CryptoUtils.generate_keypair()
        self.other = pc.CryptoUtils.generate_keypair()
        self.ids = []
        self.conn = economy.connect()
        self.accept_terms(self.wallet["address"])
        self.accept_terms(self.other["address"])

    def tearDown(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM advertiser_agreements WHERE source = 'test'")
        for ad_id in self.ids:
            for f in glob.glob(os.path.join(PENDING, ad_id + "_*")) + glob.glob(os.path.join(ACTIVE, ad_id + "_*")):
                os.remove(f)
            cur.execute("DELETE FROM ad_approvals WHERE ad_id = %s", (ad_id,))
        self.conn.commit()
        cur.close()
        self.conn.close()

    def make_ad(self, **over):
        ad_id = "test-submit-" + uuid.uuid4().hex[:10]
        self.ids.append(ad_id)
        ad = {"id": ad_id, "title": "Test ad", "description": "d", "category": "test", "click_url": "https://example.com/landing",
              "payout_amount": 0.001, "advertiser_address": self.wallet["address"],
              "expires_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 86400)),
              "targeting": {"budget_daily": 1.0, "max_clicks_daily": 100},
              "content": {"svg": "<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><rect width='10' height='10'/></svg>"}}
        ad.update(over)
        return ad

    def send(self, ad, wallet=None, mutate=None, ts=None, terms="current", fee="auto"):
        wallet = wallet or self.wallet
        body = {"ts": int(time.time()) if ts is None else ts, "nonce": uuid.uuid4().hex, "ad": ad}
        body["terms_version"] = self.terms_version if terms == "current" else terms
        if fee == "auto":
            fee = {"order": self.new_order(), "sec": SHOP_SEC}
        if fee:
            body["fee"] = fee
        payload = json.dumps(body, sort_keys=True)
        req = {"payload": payload, "public_key": wallet["public_key"], "signature": ad_publisher.sign_message(wallet["private_key"], payload.encode())}
        if mutate:
            mutate(req)
        r = requests.post(URL, json=req, timeout=20)
        return r.status_code, r.json()

    # ------------------------------------------------------------------------------------------------
    def test_valid_submission_waits_for_review(self):
        ad = self.make_ad()
        code, body = self.send(ad)
        self.assertEqual((code, body.get("success"), body.get("status")), (200, True, "pending_review"), body)
        self.assertTrue(os.path.exists(os.path.join(PENDING, ad["id"] + "_meta.json")))
        self.assertFalse(os.path.exists(os.path.join(ACTIVE, ad["id"] + "_meta.json")), "nothing is served before approval")
        cur = self.conn.cursor()
        cur.execute("SELECT status FROM ad_approvals WHERE ad_id = %s", (ad["id"],))
        self.assertEqual(cur.fetchone()[0], "pending")
        cur.close()
        self.conn.commit()

    def test_forged_and_tampered_submissions_are_refused(self):
        ad = self.make_ad()
        # 1. payload changed after signing
        def tamper(req):
            p = json.loads(req["payload"]); p["ad"]["payout_amount"] = 0.09; req["payload"] = json.dumps(p, sort_keys=True)
        code, body = self.send(ad, mutate=tamper)
        self.assertEqual(code, 401, body)
        # 2. signed by a different key than the advertiser address
        code, body = self.send(self.make_ad(), wallet=self.other)
        self.assertEqual(code, 403, body)
        # 3. a corrupted signature
        code, body = self.send(self.make_ad(), mutate=lambda r: r.update(signature="00" * 64))
        self.assertEqual(code, 401, body)
        self.assertEqual(glob.glob(os.path.join(PENDING, "test-submit-*")) and [f for i in self.ids for f in glob.glob(os.path.join(PENDING, i + "_*"))], [])

    def test_replay_and_stale_submissions_are_refused(self):
        ad = self.make_ad()
        req = ad_publisher.build_request(ad, self.wallet, self.terms_version, self.new_order(), SHOP_SEC)
        self.assertEqual(requests.post(URL, json=req, timeout=20).status_code, 200)
        again = requests.post(URL, json=req, timeout=20)
        self.assertEqual(again.status_code, 400)
        self.assertIn("already used", again.json()["message"])
        code, body = self.send(self.make_ad(), ts=int(time.time()) - 3600)
        self.assertEqual(code, 400, body)

    def test_hostile_or_invalid_content_is_refused(self):
        for label, over, expect in (
            ("javascript link", {"click_url": "javascript:alert(1)"}, 400),
            ("data link", {"click_url": "data:text/html,<script>1</script>"}, 400),
            ("payout too high", {"payout_amount": 5.0}, 400),
            ("payout zero", {"payout_amount": 0}, 400),
            ("already expired", {"expires_at": "2001-01-01T00:00:00"}, 400),
            ("path traversal id", {"id": "../../config"}, 400),
            ("not an image", {"content": {"image_b64": base64.b64encode(b"<?php system('x'); ?>").decode()}}, 400),
            ("no content", {"content": {}}, 400),
        ):
            ad = self.make_ad(**over)
            code, body = self.send(ad)
            self.assertEqual(code, expect, f"{label}: {body}")
        ok = self.make_ad(content={"image_b64": PNG})
        code, body = self.send(ok)
        self.assertEqual(code, 200, body)
        self.assertTrue(glob.glob(os.path.join(PENDING, ok["id"] + "_image.png")))

    def test_an_ad_id_belongs_to_whoever_submitted_it_first(self):
        ad = self.make_ad()
        self.assertEqual(self.send(ad)[0], 200)
        hijack = dict(ad, advertiser_address=self.other["address"])
        code, body = self.send(hijack, wallet=self.other)
        self.assertEqual(code, 403, body)

    def test_approval_moves_the_ad_into_service_and_resubmission_pulls_it_out_again(self):
        ad = self.make_ad()
        self.assertEqual(self.send(ad)[0], 200)
        economy.approve_ad(ad["id"], "test", self.conn)
        meta_active = os.path.join(ACTIVE, ad["id"] + "_meta.json")
        self.assertTrue(os.path.exists(meta_active))
        self.assertFalse(os.path.exists(os.path.join(PENDING, ad["id"] + "_meta.json")))
        self.assertEqual(json.load(open(meta_active))["status"], "active")
        self.assertTrue(glob.glob(os.path.join(ACTIVE, ad["id"] + "_svg.svg")))
        # the advertiser swaps the content: it must go back to review and stop being served
        changed = dict(ad, content={"svg": "<svg xmlns='http://www.w3.org/2000/svg'><circle r='5'/></svg>"})
        self.assertEqual(self.send(changed)[0], 200)
        self.assertFalse(os.path.exists(meta_active), "changed content must not stay in service")
        cur = self.conn.cursor()
        cur.execute("SELECT status FROM ad_approvals WHERE ad_id = %s", (ad["id"],))
        self.assertEqual(cur.fetchone()[0], "pending")
        cur.close()
        self.conn.commit()

    def test_rejecting_removes_the_files(self):
        ad = self.make_ad()
        self.assertEqual(self.send(ad)[0], 200)
        economy.reject_ad(ad["id"], "not suitable", self.conn)
        self.assertEqual([f for f in glob.glob(os.path.join(PENDING, ad["id"] + "_*")) + glob.glob(os.path.join(ACTIVE, ad["id"] + "_*"))], [])

    def test_the_publisher_tool_builds_a_request_the_server_accepts(self):
        ad = self.make_ad()
        meta = os.path.join(PENDING, "scratch_" + ad["id"] + "_meta.json")
        os.makedirs(PENDING, exist_ok=True)
        with open(meta, "w", encoding="utf-8") as fh:
            json.dump({k: ad[k] for k in ("id", "title", "description", "category", "click_url", "payout_amount", "advertiser_address", "expires_at", "targeting")}, fh)
        with open(meta[: -len("_meta.json")] + "_text.txt", "w", encoding="utf-8") as fh:
            fh.write("Buy nickles")
        try:
            loaded = ad_publisher.load_ad(meta)
            loaded["id"] = ad["id"]
            status, body = ad_publisher.publish(meta, URL, wallet=self.wallet, fee_order=self.new_order(), fee_sec=SHOP_SEC)
        finally:
            for f in glob.glob(os.path.join(PENDING, "scratch_*")):
                os.remove(f)
        self.assertIn("text", loaded["content"])
        self.assertEqual((status, body.get("success")), (200, True), body)

    # ---------------------------------------------------------------- agreement and upload fee
    def test_requirements_are_published(self):
        info = ad_publisher.fetch_requirements(URL)
        self.assertEqual(info["terms_version"], self.terms_version)
        self.assertTrue(info["fee_required"])
        self.assertTrue(info["terms_url"].endswith("advertiser_terms.php"))

    def test_an_advertiser_who_has_not_accepted_the_agreement_is_refused(self):
        stranger = pc.CryptoUtils.generate_keypair()
        ad = self.make_ad(advertiser_address=stranger["address"])
        code, body = self.send(ad, wallet=stranger)
        self.assertEqual(code, 403, body)
        self.assertIn("agreement", body["error"])
        # accepted an older version / claims the wrong version
        code, body = self.send(self.make_ad(), terms=self.terms_version + 1)
        self.assertEqual(code, 403, body)
        code, body = self.send(self.make_ad(), terms=None)
        self.assertEqual(code, 403, body)

    def test_the_upload_fee_is_mandatory_and_used_up_by_one_submission(self):
        # no order at all
        code, body = self.send(self.make_ad(), fee=None)
        self.assertEqual(code, 402, body)
        self.assertIn("requirements", body)
        # unpaid order
        code, body = self.send(self.make_ad(), fee={"order": self.new_order("pending"), "sec": SHOP_SEC})
        self.assertEqual(code, 402, body)
        # wrong secure ID
        code, body = self.send(self.make_ad(), fee={"order": self.new_order(), "sec": "b2" * 16})
        self.assertEqual(code, 402, body)
        # a paid order for some other product
        code, body = self.send(self.make_ad(), fee={"order": self.new_order(product="other"), "sec": SHOP_SEC})
        self.assertEqual(code, 402, body)
        # a good order works once...
        order = self.new_order()
        code, body = self.send(self.make_ad(), fee={"order": order, "sec": SHOP_SEC})
        self.assertEqual(code, 200, body)
        # ...and cannot pay for a second upload
        code, body = self.send(self.make_ad(), fee={"order": order, "sec": SHOP_SEC})
        self.assertEqual(code, 402, body)
        self.assertIn("already been used", body["error"])

    def test_a_rejected_submission_does_not_burn_the_fee(self):
        order = self.new_order()
        code, _ = self.send(self.make_ad(payout_amount=0), fee={"order": order, "sec": SHOP_SEC})
        self.assertEqual(code, 400)
        code, body = self.send(self.make_ad(), fee={"order": order, "sec": SHOP_SEC})
        self.assertEqual(code, 200, body)

    def test_the_fee_can_be_switched_off(self):
        econ = json.loads(self._econ_original)
        econ.update({"ad_upload_fee_required": False, "btcshop_db": self.shop_db})
        with open(ECON, "w", encoding="utf-8") as fh:
            json.dump(econ, fh)
        try:
            code, body = self.send(self.make_ad(), fee=None)
            self.assertEqual(code, 200, body)
        finally:
            econ.update({"ad_upload_fee_required": True})
            with open(ECON, "w", encoding="utf-8") as fh:
                json.dump(econ, fh)


if __name__ == "__main__":
    unittest.main(verbosity=2)
