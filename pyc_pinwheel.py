"""Pinwheel transparent encryption client for the PythonCoin ad network (mirror of pyc_pinwheel.js).

    result = pinwheel_post_json("https://host/adnetworking/api.php", {"action": "client_register_live", ...})

No accounts. A session opens automatically (ECDH-wrapped random root secret), then every query is sealed with
AES-256-GCM under HKDF(root,"epoch-E") -> HKDF(...,"msg-N"), and every reply under HKDF(msg_key,"resp").
"""
import base64
import json
import os
import threading
import time
from urllib.parse import urlsplit, urlunsplit, parse_qsl

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_lock = threading.Lock()
_sessions = {}


def _hkdf(ikm: bytes, info: str) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=info.encode()).derive(ikm)


def _b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def _seal(key: bytes, plain: bytes, aad: str) -> bytes:
    iv = os.urandom(12)
    return iv + AESGCM(key).encrypt(iv, plain, aad.encode())


def _open(key: bytes, blob: bytes, aad: str) -> bytes:
    return AESGCM(key).decrypt(blob[:12], blob[12:], aad.encode())


def _base(url: str) -> str:
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.netloc, p.path.rsplit("/", 1)[0] + "/", "", ""))


def _open_session(base: str, timeout: float) -> dict:
    api = base + "api.php"
    pk = requests.post(api, json={"action": "public_key"}, timeout=timeout).json()["public_key"]
    server_pub = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), base64.b64decode(pk))
    eph = ec.generate_private_key(ec.SECP256R1())
    key = _hkdf(eph.exchange(ec.ECDH(), server_pub), "pyc-report-v1")
    root = os.urandom(32)
    body = {"action": "pw_open", "root": _b64(root), "ts": int(time.time()), "nonce": _b64(os.urandom(18)).replace("+", "A").replace("/", "B").replace("=", "")}
    iv = os.urandom(12)
    ct = AESGCM(key).encrypt(iv, json.dumps(body).encode(), None)
    epk = eph.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    t0 = time.time()
    resp = requests.post(api, json={"enc": {"v": 1, "epk": _b64(epk), "iv": _b64(iv), "ct": _b64(ct)}}, timeout=timeout).json()
    if not resp.get("pw"):
        raise RuntimeError("pinwheel handshake refused")
    info = json.loads(_open(_hkdf(root, "pw-open"), base64.b64decode(resp["ct"]), "pw-open"))
    return {"sid": info["sid"], "root": root, "start": info["start"], "eps": info["epoch_seconds"],
            "offset": info["server_time"] - int((t0 + time.time()) / 2), "counters": {}}


def pinwheel_post_json(url: str, payload: dict, timeout: float = 10, _retry: bool = False) -> dict:
    """POST `payload` encrypted; returns the decrypted JSON reply (raises on transport/crypto failure)."""
    base = _base(url)
    with _lock:
        s = _sessions.get(base)
        if s is None:
            s = _sessions[base] = _open_session(base, timeout)
        E = int((time.time() + s["offset"] - s["start"]) // s["eps"])
        N = s["counters"].get(E, 0)
        s["counters"][E] = N + 1
    parts = urlsplit(url)
    body = dict(parse_qsl(parts.query))
    body.update(payload)
    aad = f"{s['sid']}|{E}|{N}"
    msg_key = _hkdf(_hkdf(s["root"], f"epoch-{E}"), f"msg-{N}")
    blob = _seal(msg_key, json.dumps(body).encode(), aad)
    clean = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    r = requests.post(clean, json={"pw": {"v": 1, "sid": s["sid"], "e": E, "n": N, "ct": _b64(blob)}}, timeout=timeout)
    try:
        j = r.json()
    except ValueError:
        j = None
    if isinstance(j, dict) and j.get("pw"):
        return json.loads(_open(_hkdf(msg_key, "resp"), base64.b64decode(j["ct"]), aad + "|r"))
    if not _retry and r.status_code == 400:           # session expired on the server: reopen once
        with _lock:
            _sessions.pop(base, None)
        return pinwheel_post_json(url, payload, timeout, True)
    raise RuntimeError(f"pinwheel query failed ({r.status_code}): {r.text[:120]}")
