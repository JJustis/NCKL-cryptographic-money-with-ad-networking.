"""Push an ad to the network server, signed with the advertiser's wallet key.

    python ad_publisher.py <path to an ad's _meta.json> [server url]

An ad is sent as {payload, public_key, signature}: the signature is the wallet key signing SHA-256(payload text), and the
address derived from that key must equal the ad's advertiser_address, so nobody can submit ads in someone else's name.
The server queues the ad for review; once it is approved and the advertiser has funds it is served and paid for.
"""
import base64
import glob
import hashlib
import json
import os
import sys
import time
import uuid

import ecdsa

import consensus

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_URL = None   # taken from economy.json "ad_server_url", else this installation's own address (site_config.json)


def sign_message(private_key_hex, message):
    """Same scheme as CryptoUtils.sign_data (ECDSA secp256k1 over SHA1 of the SHA-256 digest), on raw bytes."""
    key = ecdsa.SigningKey.from_string(bytes.fromhex(private_key_hex), curve=ecdsa.SECP256k1)
    return key.sign(hashlib.sha256(message).digest()).hex()


def load_ad(meta_path):
    """Read an ad saved by the app (<id>_meta.json plus its svg/html/text/image file)."""
    with open(meta_path, "r", encoding="utf-8") as fh:
        meta = json.load(fh)
    stem = meta_path[: -len("_meta.json")]
    content = {}
    for key, pattern, binary in (("svg", "_svg.svg", False), ("html", "_html.html", False), ("text", "_text.txt", False)):
        if os.path.exists(stem + pattern):
            with open(stem + pattern, "r", encoding="utf-8") as fh:
                content[key] = fh.read()
            break
    else:
        for image in glob.glob(stem + "_image.*"):
            with open(image, "rb") as fh:
                content["image_b64"] = base64.b64encode(fh.read()).decode()
            break
    ad = {k: meta.get(k) for k in ("id", "title", "description", "category", "click_url", "payout_amount", "advertiser_address",
                                   "expires_at", "targeting", "format")}
    ad["click_url"] = ad["click_url"] or meta.get("target_url")
    ad["content"] = content
    return ad


def build_request(ad, wallet, terms_version=None, fee_order=None, fee_sec=None):
    """wallet: dict with private_key / public_key / address (wallet.json). The signed payload also carries the agreement
    version the advertiser accepted and the paid shop order (number + secure ID) that covers this upload."""
    body = {"ts": int(time.time()), "nonce": uuid.uuid4().hex, "ad": ad}
    if terms_version is not None:
        body["terms_version"] = int(terms_version)
    if fee_order is not None:
        body["fee"] = {"order": int(fee_order), "sec": str(fee_sec or "")}
    payload = json.dumps(body, sort_keys=True)
    return {"payload": payload, "public_key": wallet["public_key"],
            "signature": sign_message(wallet["private_key"], payload.encode())}


def server_url(url=None):
    if url:
        return url
    import dbconfig, economy
    return economy.settings().get("ad_server_url") or dbconfig.site()["base_url"] + "/submit_ad.php"


def fetch_requirements(url=None, timeout=15):
    """Ask the server what a submission needs: terms version / page, whether an upload fee is due, where to pay it."""
    import requests
    response = requests.get(server_url(url), params={"info": 1}, timeout=timeout)
    return response.json()


def publish(meta_path, url=None, wallet=None, timeout=15, terms_version=None, fee_order=None, fee_sec=None):
    import requests
    if wallet is None:
        with open(os.path.join(HERE, "wallet.json"), "r", encoding="utf-8") as fh:
            wallet = json.load(fh)
    ad = load_ad(meta_path)
    ad["advertiser_address"] = ad.get("advertiser_address") or wallet["address"]
    url = server_url(url)
    if terms_version is None:
        terms_version = fetch_requirements(url, timeout).get("terms_version")
    response = requests.post(url, json=build_request(ad, wallet, terms_version, fee_order, fee_sec), timeout=timeout)
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, {"success": False, "message": response.text[:200]}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Submit an ad to the network (accept the agreement on the website first).")
    ap.add_argument("meta", nargs="?", help="path to the ad's _meta.json")
    ap.add_argument("url", nargs="?", help="submit_ad.php address (default: this installation's)")
    ap.add_argument("--order", type=int, help="paid shop order number for the upload fee")
    ap.add_argument("--sec", help="secure ID of that order")
    ap.add_argument("--terms", type=int, help="agreement version you accepted (default: the server's current one)")
    ap.add_argument("--info", action="store_true", help="show what the server requires and exit")
    args = ap.parse_args()
    if args.info:
        print(json.dumps(fetch_requirements(args.url), indent=2))
        sys.exit(0)
    if not args.meta:
        ap.print_help()
        sys.exit(1)
    status, body = publish(args.meta, args.url, terms_version=args.terms, fee_order=args.order, fee_sec=args.sec)
    print(status, json.dumps(body))
    sys.exit(0 if body.get("success") else 1)
