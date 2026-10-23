"""Reset this node to a brand-new chain that starts from genesis.json.

    python reset_chain.py            # preview only: shows what would change, touches nothing
    python reset_chain.py --yes      # do it (backs everything up first)

What it does, in order:
  1. refuses to run while the wallet app is running (it would overwrite the files)
  2. backs up blockchain.json, wallet.json, the ad files and the affected database tables
  3. writes a new blockchain.json containing only the genesis block
  4. clears the chain tables, the unspent-output table, the mempool and the stale peer list in MySQL
  5. holds unpaid ad clicks (they refer to coins of the old chain; release them on purpose later)
  6. re-encodes every stored address with this coin's address prefix. The same key hash is kept, so every owner keeps
     their account; only the letters change (the wallet key is untouched, only its address text changes)
"""
import argparse
import glob
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import consensus
import pythoncoin as pc

CHAIN_TABLES = ["blockchain_tx_outputs", "blockchain_tx_inputs", "blockchain_transactions", "blockchain_utxo",
                "blockchain_mempool", "blockchain_blocks"]
# (table, column) pairs that hold Nickles-style addresses
ADDRESS_COLUMNS = [("developers", "pythoncoin_address"), ("ads", "advertiser_address"), ("ad_members", "pythoncoin_address"),
                   ("ad_clicks", "developer_address")]
ADDRESS_RE = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{25,35}\b")


def app_running():
    for port in (8332, 8333):
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return port
    return None


def convert_text(text):
    """Replace every valid old-format address found in `text`; returns (new text, count)."""
    count = 0

    def sub(m):
        nonlocal count
        d = consensus.decode_address(m.group(0))
        if d is None or d[0] == consensus.PARAMS.address_version:
            return m.group(0)
        count += 1
        return consensus.encode_address(consensus.PARAMS.address_version, d[1])
    return ADDRESS_RE.sub(sub, text), count


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--yes", action="store_true", help="actually perform the reset")
    ap.add_argument("--db", default=None, help="database name (default: the configured one)")
    args = ap.parse_args()
    do = args.yes
    say = (lambda m: print(("DONE   " if do else "WOULD  ") + m))

    genesis_path = os.path.join(HERE, consensus.PARAMS.genesis_file)
    if not os.path.exists(genesis_path):
        sys.exit("genesis.json is missing - run make_genesis.py first")
    port = app_running()
    if port:
        sys.exit(f"something is listening on port {port}: stop the wallet app first")
    genesis = pc.Block.from_dict(json.load(open(genesis_path, encoding="utf-8")))
    probe = pc.Blockchain()
    if not probe.chain or probe.chain[0].hash != genesis.hash:
        sys.exit("genesis.json does not validate")
    print(f"Coin: {consensus.PARAMS.coin_name} ({consensus.PARAMS.ticker})   address version {consensus.PARAMS.address_version}"
          f"   genesis {genesis.hash[:16]}...   {'EXECUTING' if do else 'PREVIEW (nothing is changed)'}\n")

    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup = os.path.join(r"C:\xampp\security_backup_20261022", f"reset_{stamp}")

    import dbconfig
    db = dbconfig.connect(**({} if args.db is None else {"database": args.db}))
    cur = db.cursor()

    # 2. backups
    if do:
        os.makedirs(backup, exist_ok=True)
        for f in ("blockchain.json", "wallet.json"):
            if os.path.exists(os.path.join(HERE, f)):
                shutil.copy(os.path.join(HERE, f), backup)
        for folder in ("ads_storage", "users"):
            if os.path.isdir(os.path.join(HERE, folder)):
                shutil.copytree(os.path.join(HERE, folder), os.path.join(backup, folder), dirs_exist_ok=True)
        tables = CHAIN_TABLES + ["p2p_clients"] + sorted({t for t, _ in ADDRESS_COLUMNS})
        with open(os.path.join(backup, "tables_before.sql"), "wb") as out:
            subprocess.run([r"C:\xampp\mysql\bin\mysqldump.exe", "-uroot", "--single-transaction", args.db] + tables, stdout=out, check=True)
    say(f"back up chain, wallet, ad files and tables to {backup}")

    # 3. new chain file
    chain_file = {
        "chain": [genesis.to_dict()], "pending_transactions": [], "genesis_complete": True, "genesis_addresses": [],
        "difficulty": genesis.difficulty, "mining_reward": 50, "saved_timestamp": time.time(),
        "saved_datetime": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if do:
        with open(os.path.join(HERE, "blockchain.json"), "w", encoding="utf-8") as fh:
            json.dump(chain_file, fh, indent=2)
    say("write blockchain.json with the genesis block only (0 coins in existence)")

    # 4. database chain state
    for t in CHAIN_TABLES:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            n = cur.fetchone()[0]
        except Exception:
            continue
        if do:
            cur.execute("SET FOREIGN_KEY_CHECKS=0")
            cur.execute(f"DELETE FROM {t}")
            cur.execute("SET FOREIGN_KEY_CHECKS=1")
        say(f"clear {t} ({n} rows)")
    cur.execute("SELECT COUNT(*) FROM p2p_clients")
    n = cur.fetchone()[0]
    if do:
        cur.execute("DELETE FROM p2p_clients")
    say(f"clear stale peer list p2p_clients ({n} rows; the node registers itself again when it starts)")

    # 5. unpaid ad clicks refer to the old chain
    cur.execute("SELECT COUNT(*), COALESCE(SUM(payout_amount),0) FROM ad_clicks WHERE processed=0 AND payment_status='pending' AND payout_amount>0")
    n, total = cur.fetchone()
    if do:
        cur.execute("UPDATE ad_clicks SET payment_status='held' WHERE processed=0 AND payment_status='pending' AND payout_amount>0")
    say(f"hold {n} unpaid ad click(s) worth {total} (release deliberately once the new chain can pay)")

    # 6. addresses
    converted = 0
    for table, col in ADDRESS_COLUMNS:
        try:
            cur.execute(f"SELECT DISTINCT {col} FROM {table} WHERE {col} IS NOT NULL AND {col} <> ''")
            olds = [r[0] for r in cur.fetchall()]
        except Exception:
            continue
        for old in olds:
            d = consensus.decode_address(old)
            if d is None or d[0] == consensus.PARAMS.address_version:
                continue
            new = consensus.encode_address(consensus.PARAMS.address_version, d[1])
            if do:
                cur.execute(f"UPDATE {table} SET {col} = %s WHERE {col} = %s", (new, old))
            converted += 1
            say(f"{table}.{col}: {old[:10]}... -> {new[:10]}...")
    # wallet file
    wpath = os.path.join(HERE, "wallet.json")
    if os.path.exists(wpath):
        w = json.load(open(wpath, encoding="utf-8"))
        new_addr = pc.CryptoUtils.pubkey_to_address(w["public_key"])
        say(f"wallet.json address {w.get('address', '')[:10]}... -> {new_addr[:10]}... (same key)")
        if do:
            w["address"] = new_addr
            json.dump(w, open(wpath, "w", encoding="utf-8"))
    # ad files and user files that mention addresses
    files = glob.glob(os.path.join(HERE, "ads_storage", "**", "*.json"), recursive=True) + \
            glob.glob(os.path.join(HERE, "users", "**", "*.json"), recursive=True)
    for f in files:
        text = open(f, encoding="utf-8", errors="replace").read()
        new_text, n = convert_text(text)
        if n:
            say(f"{os.path.relpath(f, HERE)}: {n} address(es) re-encoded")
            if do:
                open(f, "w", encoding="utf-8").write(new_text)

    if do:
        db.commit()
    cur.close()
    db.close()
    print("\nReset complete. Start the wallet app: it loads genesis.json and begins at block 1." if do else
          "\nPreview only. Run again with --yes to perform the reset.")


if __name__ == "__main__":
    main()
