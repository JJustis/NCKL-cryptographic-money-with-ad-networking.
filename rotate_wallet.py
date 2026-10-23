"""Replace the node wallet with a brand-new key and move everything that pointed at the old address.

    python rotate_wallet.py            # preview
    python rotate_wallet.py --yes      # do it (the old wallet file is saved in the backup folder first)

Use it while the wallet holds nothing (as right after a fresh genesis), or after moving funds to the new address.
Stop the wallet app first.
"""
import argparse
import glob
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import consensus
import pythoncoin as pc

# (table, column) pairs that store the node owner's address
COLUMNS = [("developers", "pythoncoin_address"), ("ads", "advertiser_address"), ("ad_members", "pythoncoin_address"),
           ("ad_clicks", "developer_address"), ("p2p_clients", "wallet_address")]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--db", default=None, help="database name (default: the configured one)")
    args = ap.parse_args()
    do = args.yes
    say = lambda m: print(("DONE   " if do else "WOULD  ") + m)

    wpath = os.path.join(HERE, "wallet.json")
    old = json.load(open(wpath, encoding="utf-8"))
    old_addr = pc.CryptoUtils.pubkey_to_address(old["public_key"])
    new = pc.CryptoUtils.generate_keypair()
    print(f"old address {old_addr}\nnew address {new['address']}   ({'EXECUTING' if do else 'PREVIEW'})\n")

    import dbconfig
    db = dbconfig.connect(**({} if args.db is None else {"database": args.db}))
    cur = db.cursor()

    if do:
        backup = os.path.join(r"C:\xampp\security_backup_20261022", f"old_wallet_{time.strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(backup, exist_ok=True)
        shutil.copy(wpath, backup)
        json.dump(new, open(wpath, "w", encoding="utf-8"))
    say(f"new wallet key written to wallet.json (old key saved outside the web root)")

    for table, col in COLUMNS:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} = %s", (old_addr,))
            n = cur.fetchone()[0]
        except Exception:
            continue
        if n:
            if do:
                cur.execute(f"UPDATE {table} SET {col} = %s WHERE {col} = %s", (new["address"], old_addr))
            say(f"{table}.{col}: {n} row(s) moved to the new address")

    files = glob.glob(os.path.join(HERE, "ads_storage", "**", "*.json"), recursive=True) + \
            glob.glob(os.path.join(HERE, "users", "**", "*.json"), recursive=True)
    for f in files:
        text = open(f, encoding="utf-8", errors="replace").read()
        if old_addr in text:
            say(f"{os.path.relpath(f, HERE)}: address replaced")
            if do:
                open(f, "w", encoding="utf-8").write(text.replace(old_addr, new["address"]))
    if do:
        db.commit()
    db.close()
    print("\nDone." if do else "\nPreview only. Run with --yes.")


if __name__ == "__main__":
    main()
