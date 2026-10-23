"""Create the one fixed genesis block every node of this coin must share.

    python make_genesis.py                 # writes genesis.json (refuses to overwrite)
    python make_genesis.py --force         # replace it (a different genesis = a different chain)

Fair launch: the genesis block creates NO spendable coins. Every coin in existence comes from mining (50 per block,
halving every 210,000 blocks, 21,000,000 maximum). The block carries only a message, like Bitcoin's.
Copy genesis.json to every node unchanged; nodes refuse a chain that starts from any other block.
"""
import argparse
import json
import os
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import consensus
import pythoncoin as pc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zeros", type=int, default=6, help="leading hex zeros required for the genesis hash and the starting difficulty (6 = about a minute per block on one PC)")
    ap.add_argument("--message", default=None, help="text embedded in the genesis block")
    ap.add_argument("--out", default=os.path.join(here, consensus.PARAMS.genesis_file))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if os.path.exists(args.out) and not args.force:
        sys.exit(f"{args.out} already exists - a different genesis block is a different chain. Use --force only on purpose.")

    stamp = int(time.time())
    message = args.message or f"{consensus.PARAMS.coin_name}: a nickel for every click - {time.strftime('%d/%b/%Y', time.gmtime(stamp))}"
    tx = pc.Transaction(
        sender="genesis", inputs=[], outputs=[], tx_type="genesis", timestamp=float(stamp),
        data={"message": message, "coin": consensus.PARAMS.coin_name, "ticker": consensus.PARAMS.ticker},
    )
    tx.calculate_tx_id()
    block = pc.Block(index=0, timestamp=float(stamp), transactions=[tx], previous_hash="0" * 64, difficulty=args.zeros)
    print(f"mining genesis ({args.zeros} leading zeros)...")
    block.mine_block("genesis")

    # it must be accepted by a brand-new chain exactly like any other block would be checked
    probe = pc.Blockchain()
    if not probe.add_block(block):
        sys.exit("internal error: the genesis block did not validate")
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(block.to_dict(), fh, indent=2)
    print(f"genesis written to {args.out}")
    print(f"  coin:    {consensus.PARAMS.coin_name} ({consensus.PARAMS.ticker})")
    print(f"  message: {message}")
    print(f"  hash:    {block.hash}")
    print(f"  coins created by genesis: 0 (fair launch)")


if __name__ == "__main__":
    main()
