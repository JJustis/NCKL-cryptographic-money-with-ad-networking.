"""Advertiser money handling that lives next to the blockchain (the PHP side charges clicks, see economy.php).

  credit_deposits(blockchain, payer_address)  turn confirmed on-chain payments to the network wallet into advertiser balance
  run_retention()                             delete / anonymise visitor data after the configured number of days
  approve_ad / reject_ad / pending_ads        review queue (nothing is served or paid until an ad is approved)

Deposits: an advertiser sends coins from their own wallet to the network wallet (the node's wallet address). Once the
payment has `deposit_confirmations` blocks on top of it, its outputs to the network wallet are credited to the SENDER's
address. Crediting is keyed by transaction id, so scanning the chain again never credits twice.
"""
import json
import logging
import os

import consensus

HERE = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger("Nickles-Economy")

DEFAULTS = {"network_fee_percent": 0, "click_hold_minutes": 1440, "max_clicks_per_ip_per_ad_per_day": 3,
            "max_clicks_per_ip_per_day": 20, "allow_self_clicks": False, "deposit_confirmations": 6,
            "retention_impression_days": 30, "retention_ip_days": 90, "ad_server_url": "",
            "ad_upload_fee_required": True, "btcshop_db": "", "btcshop_product": "ad-upload", "btcshop_url": ""}


def settings():
    cfg = dict(DEFAULTS)
    path = os.path.join(HERE, "economy.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            cfg.update(json.load(fh))
    return cfg


def connect(database=None):
    """Connection using the configured login (dbconfig.json); `database` overrides the configured database name."""
    import dbconfig
    return dbconfig.connect(**({} if database is None else {"database": database}))


def _sender_address(tx):
    from pythoncoin import CryptoUtils
    return CryptoUtils.pubkey_to_address(tx.sender)


def credit_deposits(blockchain, payer_address, conn=None, only_height=None):
    """Credit confirmed payments to `payer_address`.  Returns the list of (tx_id, advertiser, amount_sat) newly credited.

    only_height: check just the block at that height (cheap, used after each new block); None scans the whole chain."""
    if not payer_address:
        return []
    need = max(1, int(settings()["deposit_confirmations"]))
    tip = len(blockchain.chain) - 1
    own = conn is None
    conn = conn or connect()
    cur = conn.cursor()
    credited = []
    try:
        blocks = blockchain.chain if only_height is None else [b for b in blockchain.chain if b.index == only_height]
        for block in blocks:
            if tip - block.index + 1 < need:
                continue                                   # not enough blocks on top yet
            for tx in block.transactions:
                if tx.tx_type != "standard" or not tx.inputs:
                    continue
                advertiser = _sender_address(tx)
                if advertiser == payer_address:
                    continue                               # the network wallet paying out is not a deposit
                amount = sum(consensus.to_sat(o.amount, strict=False) for o in tx.outputs if o.address == payer_address)
                if amount <= 0:
                    continue
                cur.execute("INSERT IGNORE INTO advertiser_deposits (tx_id, address, amount_sat, block_height) VALUES (%s, %s, %s, %s)",
                            (tx.tx_id, advertiser, amount, block.index))
                if cur.rowcount != 1:
                    continue                               # already credited
                cur.execute("INSERT INTO advertiser_accounts (address, balance_sat, deposited_sat) VALUES (%s, %s, %s) "
                            "ON DUPLICATE KEY UPDATE balance_sat = balance_sat + VALUES(balance_sat), "
                            "deposited_sat = deposited_sat + VALUES(deposited_sat)", (advertiser, amount, amount))
                cur.execute("INSERT INTO advertiser_ledger (address, kind, amount_sat, ref) VALUES (%s, 'deposit', %s, %s)",
                            (advertiser, amount, "tx:" + tx.tx_id))
                credited.append((tx.tx_id, advertiser, amount))
                logger.info(f"Credited deposit {consensus.from_sat(amount)} to advertiser {advertiser} (tx {tx.tx_id[:12]})")
        conn.commit()
    finally:
        cur.close()
        if own:
            conn.close()
    return credited


def block_listener(blockchain_getter, address_getter):
    """Build a callback for Blockchain.on_block_added that credits the block that just became `deposit_confirmations` deep."""
    def _on_block(block):
        try:
            bc, addr = blockchain_getter(), address_getter()
            if bc is None or not addr:
                return
            need = max(1, int(settings()["deposit_confirmations"]))
            target = block.index - need + 1
            if target >= 0:
                credit_deposits(bc, addr, only_height=target)
        except Exception as exc:
            logger.warning(f"deposit crediting skipped: {exc}")
    return _on_block


def anonymise_ip(ip):
    if not ip:
        return ip
    if ":" in ip:
        parts = ip.split(":")
        return ":".join(parts[:3]) + "::"
    parts = ip.split(".")
    return ".".join(parts[:3] + ["0"]) if len(parts) == 4 else ip


def run_retention(conn=None):
    """Impression rows are deleted after retention_impression_days. After retention_ip_days a click keeps its accounting
    fields but loses the visitor's exact address (last block zeroed), browser string and referrer."""
    cfg = settings()
    own = conn is None
    conn = conn or connect()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM ad_impressions WHERE seen_at < NOW() - INTERVAL %s DAY", (int(cfg["retention_impression_days"]),))
        deleted = cur.rowcount
        cur.execute("SELECT id, ip_address FROM ad_clicks WHERE click_time < NOW() - INTERVAL %s DAY "
                    "AND (user_agent IS NOT NULL OR referer IS NOT NULL OR (ip_address IS NOT NULL AND ip_address NOT LIKE '%%.0' AND ip_address NOT LIKE '%%::'))",
                    (int(cfg["retention_ip_days"]),))
        rows = cur.fetchall()
        for click_id, ip in rows:
            cur.execute("UPDATE ad_clicks SET ip_address = %s, user_agent = NULL, referer = NULL WHERE id = %s",
                        (anonymise_ip(ip), click_id))
        conn.commit()
        return deleted, len(rows)
    finally:
        cur.close()
        if own:
            conn.close()


def pending_ads(conn=None):
    own = conn is None
    conn = conn or connect()
    cur = conn.cursor()
    cur.execute("SELECT ad_id, status, first_seen FROM ad_approvals WHERE status = 'pending' ORDER BY first_seen")
    rows = cur.fetchall()
    cur.close()
    if own:
        conn.close()
    return rows


def _set_status(ad_id, status, note=None, conn=None):
    own = conn is None
    conn = conn or connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO ad_approvals (ad_id, status, note, reviewed_at) VALUES (%s, %s, %s, NOW()) "
                "ON DUPLICATE KEY UPDATE status = VALUES(status), note = VALUES(note), reviewed_at = NOW()", (ad_id, status, note))
    conn.commit()
    cur.close()
    if own:
        conn.close()


ADS_DIR = os.path.join(HERE, "ads_storage")


def _ad_files(folder, ad_id):
    import glob
    return glob.glob(os.path.join(ADS_DIR, folder, ad_id + "_*"))


def describe_pending(ad_id):
    """Title / advertiser / price of a submitted ad, read from its pending meta file (None if there is none)."""
    path = os.path.join(ADS_DIR, "pending", ad_id + "_meta.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        m = json.load(fh)
    return {"title": m.get("title"), "advertiser": m.get("advertiser_address"), "payout": m.get("payout_amount"),
            "format": m.get("format"), "click_url": m.get("click_url")}


def approve_ad(ad_id, note=None, conn=None):
    """Put a submitted ad into service: its files move from ads_storage/pending to ads_storage/active."""
    import shutil
    pending = _ad_files("pending", ad_id)
    if pending:
        os.makedirs(os.path.join(ADS_DIR, "active"), exist_ok=True)
        for f in pending:
            target = os.path.join(ADS_DIR, "active", os.path.basename(f))
            shutil.move(f, target)
            if target.endswith("_meta.json"):
                with open(target, "r", encoding="utf-8") as fh:
                    meta = json.load(fh)
                meta["status"] = "active"
                with open(target, "w", encoding="utf-8") as fh:
                    json.dump(meta, fh, indent=2)
    _set_status(ad_id, "approved", note, conn)


def reject_ad(ad_id, note=None, conn=None):
    """Refuse an ad: it is taken out of service and its submitted files are deleted."""
    for f in _ad_files("pending", ad_id) + _ad_files("active", ad_id):
        os.remove(f)
    _set_status(ad_id, "rejected", note, conn)
