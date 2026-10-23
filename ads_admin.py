"""Review queue and account tools for the ad network.

    python ads_admin.py pending                      ads waiting for review
    python ads_admin.py approve <ad_id> [note]       let an ad be served and paid for
    python ads_admin.py reject  <ad_id> [note]
    python ads_admin.py accounts                     every advertiser account and its balance
    python ads_admin.py statement <address>          deposits and click charges of one advertiser
    python ads_admin.py credit <address> <amount> [note]   manual adjustment (recorded in the ledger as 'adjust')
    python ads_admin.py retention                    run the data-retention clean-up now
"""
import sys

import consensus
import economy


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd, args = argv[1], argv[2:]
    conn = economy.connect()
    cur = conn.cursor()
    if cmd == "pending":
        rows = economy.pending_ads(conn)
        if not rows:
            print("no ads waiting for review")
        for ad_id, _status, seen in rows:
            d = economy.describe_pending(ad_id)
            extra = f"  '{d['title']}'  {d['format']}  pays {d['payout']}  advertiser {d['advertiser']}  -> {d['click_url']}" if d else ""
            print(f"{ad_id}   first seen {seen}{extra}")
    elif cmd in ("approve", "reject") and args:
        (economy.approve_ad if cmd == "approve" else economy.reject_ad)(args[0], " ".join(args[1:]) or None, conn)
        print(f"{args[0]} -> {cmd}d")
    elif cmd == "accounts":
        cur.execute("SELECT address, balance_sat, deposited_sat, spent_sat FROM advertiser_accounts ORDER BY balance_sat DESC")
        rows = cur.fetchall()
        for a, b, d, s in rows:
            print(f"{a}  balance {consensus.from_sat(b):.8f}  deposited {consensus.from_sat(d):.8f}  spent {consensus.from_sat(s):.8f}")
        if not rows:
            print("no advertiser accounts yet")
    elif cmd == "statement" and args:
        cur.execute("SELECT created_at, kind, amount_sat, ref FROM advertiser_ledger WHERE address = %s ORDER BY id DESC LIMIT 50", (args[0],))
        for t, k, a, r in cur.fetchall():
            print(f"{t}  {k:8s} {consensus.from_sat(a):+.8f}  {r}")
    elif cmd == "credit" and len(args) >= 2:
        sat = consensus.to_sat(float(args[1]))
        cur.execute("INSERT INTO advertiser_accounts (address, balance_sat, deposited_sat) VALUES (%s, %s, 0) "
                    "ON DUPLICATE KEY UPDATE balance_sat = balance_sat + VALUES(balance_sat)", (args[0], sat))
        cur.execute("INSERT INTO advertiser_ledger (address, kind, amount_sat, ref) VALUES (%s, 'adjust', %s, %s)",
                    (args[0], sat, " ".join(args[2:]) or "manual adjustment"))
        conn.commit()
        print(f"{args[0]} adjusted by {consensus.from_sat(sat):+.8f}")
    elif cmd == "retention":
        deleted, anonymised = economy.run_retention(conn)
        print(f"deleted {deleted} old impression rows, anonymised {anonymised} old click rows")
    else:
        print(__doc__)
        return 1
    cur.close()
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
