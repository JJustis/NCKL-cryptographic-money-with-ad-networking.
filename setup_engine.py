"""Everything the setup wizard does, as plain functions (no windows), so it can be tested and run unattended.

    python setup_wizard.py                      # the step-by-step wizard
    python setup_wizard.py --unattended x.json  # same steps from a settings file (see DEFAULT_SETTINGS)

Each step takes the settings dict and a `log(text)` callback and raises SetupError with a plain-language message.
"""
import base64
import json
import os
import secrets
import shutil
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

XAMPP_WINGET_ID = "ApacheFriends.Xampp.8.2"
XAMPP_DOWNLOAD_PAGE = "https://www.apachefriends.org/download.html"

DEFAULT_SETTINGS = {
    # --- system
    "xampp_dir": "",                  # folder that contains mysql\ and apache\ (found automatically when empty)
    "install_xampp": False,           # allowed to install XAMPP with winget when it is missing
    "start_services": True,           # start MariaDB / Apache when they are not running (never restarts a running one)
    # --- database
    "db_host": "localhost", "db_port": 3306,
    "db_admin_user": "root", "db_admin_password": "",
    "db_name": "nickles_ads", "db_app_user": "nickles_app", "db_app_password": "",   # empty password -> generated
    # --- people and wallet
    "wallet_mode": "new",             # new | keep (use the wallet.json already here) | import (give private_key)
    "wallet_private_key": "",
    "developer_username": "", "developer_email": "",
    # --- operator / contract
    "operator_name": "", "operator_contact": "", "governing_law": "",
    "ad_upload_fee_required": True, "btcshop_dir": "", "btcshop_url": "",
    # --- where it is published
    "web_dir": "",                    # website folder the dashboard / API is copied to (e.g. C:\xampp\htdocs\nickles)
    "public_url": "",                 # address people use for that folder, e.g. https://example.com/nickles
    "key_dir": "",                    # encryption keys, kept OUTSIDE the website folder (default: <xampp>\pyc_keys)
    "startup_shortcut": False,        # start the wallet app when Windows starts
}

# What gets copied to the website folder. Python code, the wallet and the chain stay in the program folder.
WEB_FILES = ["index.php", "learn.php", "site_common.php", "site.css", "site.js", "dashboard8.php", "developer_portal.php", "developer_portal.html", "api.php", "auth.php", "commands.php",
             "config.php", "security.php", "pinwheel.php", "dbconfig.php", "economy.php", "click_recorder.php", "curl_polyfill.php",
             "submit_ad.php", "update_clicks.php", "advertiser_terms.php", "agreements.php", "btcshop_bridge.php",
             "pyc_pinwheel.js", "consensus_params.json", "economy.json", ".htaccess"]
WEB_DIRS = ["terms"]
WEB_EMPTY_DIRS = ["ads_storage/active", "ads_storage/pending", "ads_storage/inactive", "ads_storage/assets", "ads_storage/templates",
                  "ads_storage/exports", "ads_storage/analytics", "users", "js", "logs"]


class SetupError(Exception):
    pass


def _noop(_text):
    pass


# ------------------------------------------------------------------------------------------------ system
def port_open(host, port, timeout=0.6):
    for h in ([host] if host not in ("localhost", "") else ["127.0.0.1", "::1"]):
        try:
            with socket.create_connection((h, int(port)), timeout=timeout):
                return True
        except OSError:
            continue
    return False


def find_xampp(hint=""):
    """The XAMPP folder (contains mysql\\bin\\mysqld.exe and apache\\bin\\httpd.exe), or ''."""
    candidates = [hint, os.environ.get("XAMPP_HOME", ""), os.path.abspath(os.path.join(HERE, "..", "..")), os.path.abspath(os.path.join(HERE, "..", "..", "..")),
                  r"C:\xampp", r"D:\xampp", r"E:\xampp", r"C:\Program Files\xampp", r"C:\Program Files (x86)\xampp"]
    for c in candidates:
        if c and os.path.isfile(os.path.join(c, "mysql", "bin", "mysqld.exe")) and os.path.isfile(os.path.join(c, "apache", "bin", "httpd.exe")):
            return os.path.normpath(c)
    return ""


def system_check(settings):
    """Facts for the 'system check' page: [(label, ok, detail)]."""
    rows = []
    rows.append(("Python " + sys.version.split()[0], sys.version_info >= (3, 9), "3.9 or newer is required"))
    missing = []
    for mod, pip_name in (("mysql.connector", "mysql-connector-python"), ("requests", "requests"), ("ecdsa", "ecdsa"),
                          ("cryptography", "cryptography"), ("PyQt5", "PyQt5"), ("qrcode", "qrcode")):
        try:
            __import__(mod)
        except Exception:
            missing.append(pip_name)
    rows.append(("Python packages", not missing, ("missing: " + ", ".join(missing)) if missing else "all installed"))
    x = find_xampp(settings.get("xampp_dir", ""))
    rows.append(("XAMPP (MariaDB + Apache)", bool(x), x or "not found - the wizard can install it for you"))
    rows.append(("MariaDB running", port_open(settings["db_host"], settings["db_port"]), "port %s" % settings["db_port"]))
    rows.append(("Apache running", port_open("localhost", 80), "port 80"))
    return rows, missing


def install_packages(missing, log=_noop):
    if not missing:
        return
    log("Installing Python packages: " + ", ".join(missing))
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", os.path.join(HERE, "requirements.txt")],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SetupError("pip could not install the packages:\n" + (r.stderr or r.stdout)[-600:])


def install_xampp(log=_noop):
    """Silent install through winget. Only called after the user has agreed on the wizard page."""
    log("Installing XAMPP with winget (this can take several minutes)...")
    try:
        r = subprocess.run(["winget", "install", "--id", XAMPP_WINGET_ID, "-e", "--silent",
                            "--accept-package-agreements", "--accept-source-agreements"], capture_output=True, text=True, timeout=1800)
    except FileNotFoundError:
        raise SetupError("winget is not available on this PC. Download XAMPP from %s, install it, then run the wizard again." % XAMPP_DOWNLOAD_PAGE)
    if r.returncode != 0 or not find_xampp():
        raise SetupError("The XAMPP installation did not finish (%s). Install it from %s and run the wizard again." % (r.returncode, XAMPP_DOWNLOAD_PAGE))
    log("XAMPP installed.")


def start_services(xampp, settings, log=_noop):
    """Start MariaDB and Apache if (and only if) they are not already listening. A running service is never touched."""
    if not port_open(settings["db_host"], settings["db_port"]):
        log("Starting MariaDB...")
        subprocess.Popen([os.path.join(xampp, "mysql", "bin", "mysqld.exe"), "--defaults-file=" + os.path.join(xampp, "mysql", "bin", "my.ini"),
                          "--standalone"], creationflags=0x08000000)
        for _ in range(40):
            if port_open(settings["db_host"], settings["db_port"]):
                break
            time.sleep(0.5)
        else:
            raise SetupError("MariaDB did not start. Open the XAMPP control panel and start it there.")
    if not port_open("localhost", 80):
        log("Starting Apache...")
        subprocess.Popen([os.path.join(xampp, "apache", "bin", "httpd.exe")], creationflags=0x08000000)
        for _ in range(30):
            if port_open("localhost", 80):
                break
            time.sleep(0.5)
        else:
            log("Apache did not start (port 80 may be used by another program). The wallet works without it; the website part needs it.")


# ------------------------------------------------------------------------------------------------ database
def _ident(name):
    if not name or not all(c.isalnum() or c == "_" for c in name):
        raise SetupError("Database and user names may only contain letters, digits and underscores: %r" % name)
    return name


def create_database(settings, log=_noop):
    """Create the database, a dedicated login that can only touch it, and all tables. Returns the app password."""
    import mysql.connector
    db, user = _ident(settings["db_name"]), _ident(settings["db_app_user"])
    password = settings.get("db_app_password") or secrets.token_urlsafe(18)
    try:
        admin = mysql.connector.connect(host=settings["db_host"], port=int(settings["db_port"]),
                                        user=settings["db_admin_user"], password=settings["db_admin_password"])
    except mysql.connector.Error as e:
        raise SetupError("Could not log in to MariaDB as %s: %s" % (settings["db_admin_user"], e))
    cur = admin.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci" % db)
    for host in ("localhost", "127.0.0.1", "::1"):
        cur.execute("CREATE USER IF NOT EXISTS %s@%s IDENTIFIED BY %s", (user, host, password))
        cur.execute("ALTER USER %s@%s IDENTIFIED BY %s", (user, host, password))
        cur.execute("GRANT ALL PRIVILEGES ON `%s`.* TO %%s@%%s" % db, (user, host))
    cur.execute("FLUSH PRIVILEGES")
    log("Database '%s' and login '%s' ready (the login can only use that database)." % (db, user))
    cur.close()
    admin.close()

    app = mysql.connector.connect(host=settings["db_host"], port=int(settings["db_port"]), user=user, password=password, database=db)
    cur = app.cursor()
    with open(os.path.join(HERE, "deploy", "schema.sql"), "r", encoding="utf-8") as fh:
        sql = fh.read()
    n = 0
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")   # the tables are listed alphabetically, not in dependency order
    for _ in cur.execute(sql, multi=True):
        n += 1
    app.commit()
    cur.close()
    app.close()
    log("Created %d tables." % n)
    return password


# ------------------------------------------------------------------------------------------------ keys, wallet, chain
def make_keys(key_dir, log=_noop):
    """The server-side encryption keys (Pinwheel / encrypted reports). Existing keys are never replaced."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    os.makedirs(os.path.join(key_dir, "sessions"), exist_ok=True)
    made = []
    path = os.path.join(key_dir, "master.key")
    if not os.path.exists(path):
        open(path, "wb").write(os.urandom(32)); made.append("master.key")
    path = os.path.join(key_dir, "pageview.salt")
    if not os.path.exists(path):
        open(path, "w").write(secrets.token_hex(32)); made.append("pageview.salt")
    if not os.path.exists(os.path.join(key_dir, "report_private.pem")):
        key = ec.generate_private_key(ec.SECP256R1())
        open(os.path.join(key_dir, "report_private.pem"), "wb").write(
            key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        point = key.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        open(os.path.join(key_dir, "report_public.b64"), "w").write(base64.b64encode(point).decode())
        made.append("report keys")
    log("Encryption keys in %s%s" % (key_dir, (" (created: " + ", ".join(made) + ")") if made else " (already there, kept)"))


def make_wallet(settings, log=_noop):
    """wallet.json for the node. 'keep' leaves an existing one alone; 'import' takes a private key."""
    import consensus  # noqa: F401  (address version comes from consensus_params.json)
    import pythoncoin as pc
    path = os.path.join(HERE, "wallet.json")
    mode = settings["wallet_mode"]
    if mode == "keep" and os.path.exists(path):
        wallet = json.load(open(path, encoding="utf-8"))
        log("Keeping the existing wallet %s" % wallet["address"])
        return wallet["address"]
    if os.path.exists(path):
        backup = path + ".before_setup_" + time.strftime("%Y%m%d_%H%M%S")
        shutil.copy(path, backup)
        log("The existing wallet.json was copied to %s first." % os.path.basename(backup))
    if mode == "import":
        import ecdsa
        try:
            sk = ecdsa.SigningKey.from_string(bytes.fromhex(settings["wallet_private_key"].strip()), curve=ecdsa.SECP256k1)
        except Exception:
            raise SetupError("That private key is not valid (it must be 64 hexadecimal characters).")
        pub = sk.get_verifying_key().to_string().hex()
        wallet = {"private_key": sk.to_string().hex(), "public_key": pub, "address": pc.CryptoUtils.pubkey_to_address(pub)}
    else:
        wallet = pc.CryptoUtils.generate_keypair()
    json.dump(wallet, open(path, "w", encoding="utf-8"))
    log("Wallet ready: %s" % wallet["address"])
    return wallet["address"]


def make_chain(log=_noop):
    """blockchain.json = the genesis block only, unless a chain file already exists."""
    path = os.path.join(HERE, "blockchain.json")
    if os.path.exists(path):
        log("blockchain.json already exists, kept.")
        return
    import consensus
    genesis = json.load(open(os.path.join(HERE, consensus.PARAMS.genesis_file), encoding="utf-8"))
    json.dump({"chain": [genesis], "pending_transactions": [], "genesis_complete": True, "genesis_addresses": [],
               "difficulty": genesis["difficulty"], "mining_reward": 50, "saved_timestamp": time.time()}, open(path, "w", encoding="utf-8"))
    log("New chain started from the genesis block.")


def make_developer(settings, address, log=_noop):
    """The first publisher account. Accounts are identified by wallet address; there is no password login."""
    name = settings.get("developer_username", "").strip()
    if not name:
        return
    import dbconfig
    conn = dbconfig.connect()
    cur = conn.cursor()
    cur.execute("SELECT id FROM developers WHERE username = %s", (name,))
    if cur.fetchone():
        log("Publisher '%s' already exists." % name)
    else:
        cur.execute("SELECT COALESCE(MAX(developer_id), 0) + 1 FROM developers")
        did = cur.fetchone()[0]
        cur.execute("INSERT INTO developers (username, password_hash, pythoncoin_address, email, developer_id) VALUES (%s, %s, %s, %s, %s)",
                    (name, "!" + secrets.token_hex(24), address, settings.get("developer_email") or None, did))
        conn.commit()
        log("Publisher account '%s' created for %s" % (name, address))
    cur.close()
    conn.close()


# ------------------------------------------------------------------------------------------------ configuration files
def write_configs(settings, app_password, key_dir, log=_noop):
    """dbconfig.json, site_config.json and the shop/fee part of economy.json, next to the program."""
    def dump(name, data):
        json.dump(data, open(os.path.join(HERE, name), "w", encoding="utf-8"), indent=2)
    dump("dbconfig.json", {"host": settings["db_host"], "port": int(settings["db_port"]), "user": settings["db_app_user"],
                           "password": app_password, "database": settings["db_name"]})
    url = settings["public_url"].rstrip("/")
    host = url.split("//", 1)[-1].split("/", 1)[0]
    site = {}
    if os.path.exists(os.path.join(HERE, "site_config.json")):
        site = json.load(open(os.path.join(HERE, "site_config.json"), encoding="utf-8"))
    site.update({"base_url": url, "public_host": host, "key_dir": key_dir, "operator_name": settings["operator_name"],
                 "operator_contact": settings["operator_contact"], "governing_law": settings["governing_law"]})
    dump("site_config.json", site)
    econ = json.load(open(os.path.join(HERE, "economy.json"), encoding="utf-8"))
    shop_db = ""
    if settings.get("btcshop_dir"):
        shop_db = os.path.join(settings["btcshop_dir"], "data", "shop.sqlite")
    econ.update({"ad_upload_fee_required": bool(settings["ad_upload_fee_required"]), "btcshop_db": shop_db,
                 "btcshop_url": settings.get("btcshop_url", "")})
    dump("economy.json", econ)
    log("Settings written (database login, site address, operator details, upload-fee shop).")


# ------------------------------------------------------------------------------------------------ publishing
def publish_web(settings, log=_noop):
    """Copy the website part to the chosen folder, with the settings it needs. Re-running updates the files in place."""
    web = settings["web_dir"]
    if not web:
        raise SetupError("Choose the website folder first.")
    web = os.path.abspath(web)
    os.makedirs(web, exist_ok=True)
    for d in WEB_EMPTY_DIRS:
        os.makedirs(os.path.join(web, *d.split("/")), exist_ok=True)
    if web.lower() == os.path.abspath(HERE).lower():
        log("The program folder is the website folder: nothing to copy.")
        return web
    for name in WEB_FILES + ["dbconfig.json", "site_config.json"]:
        src = os.path.join(HERE, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(web, name))
    for d in WEB_DIRS:
        shutil.copytree(os.path.join(HERE, d), os.path.join(web, d), dirs_exist_ok=True)
    # a separate website folder must share the ads and settings the wallet program works with, or the two drift apart
    for shared in ("ads_storage", "users"):
        link, target = os.path.join(web, shared), os.path.join(HERE, shared)
        if os.path.isdir(target) and os.path.isdir(link) and not os.listdir(link):
            os.rmdir(link)
        if os.path.isdir(target) and not os.path.exists(link):
            subprocess.run(["cmd", "/c", "mklink", "/J", link, target], capture_output=True)
            log("Linked %s to the program folder's %s so both see the same files." % (link, shared))
    # the ads already approved/pending here travel with the site
    src_ads = os.path.join(HERE, "ads_storage")
    for sub in ("active", "pending"):
        if os.path.isdir(os.path.join(src_ads, sub)) and settings.get("copy_ads"):
            shutil.copytree(os.path.join(src_ads, sub), os.path.join(web, "ads_storage", sub), dirs_exist_ok=True)
    with open(os.path.join(web, "ads_storage", ".htaccess"), "w") as fh:
        fh.write("# ad content is data: never run anything from here\n<FilesMatch \"(?i)\\.(php|phtml|phar|py|exe|bat)$\">\n    Require all denied\n</FilesMatch>\n")
    log("Website published to %s" % web)
    return web


def make_startup_shortcut(log=_noop):
    startup = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    if not os.path.isdir(startup):
        raise SetupError("The Windows Startup folder was not found.")
    with open(os.path.join(startup, "Nickles wallet.bat"), "w") as fh:
        fh.write('@echo off\r\ncd /d "%s"\r\nstart "" /min "%s" "%s"\r\n' % (HERE, sys.executable.replace("python.exe", "pythonw.exe"), os.path.join(HERE, "pyqt.py")))
    log("The wallet will start with Windows.")


def verify_site(settings, log=_noop):
    """Ask the published site for its requirements page; returns True when it answers."""
    import requests
    base = settings["public_url"].rstrip("/")
    try:
        r = requests.get(base + "/submit_ad.php", params={"info": 1}, timeout=8)
        ok = r.status_code == 200 and r.json().get("success")
    except Exception as e:
        log("Could not reach %s (%s). That is normal if the address is not live yet." % (base, e))
        return False
    log("The website answers at %s" % base if ok else "The website answered with an error at %s" % base)
    return bool(ok)


# ------------------------------------------------------------------------------------------------ the whole thing
def run_all(settings, log=_noop, progress=_noop):
    """Run every step in order. Returns a summary dict. Raises SetupError on the first problem."""
    s = dict(DEFAULT_SETTINGS)
    s.update(settings)
    steps = 9
    done = [0]

    def step(text):
        done[0] += 1
        progress(done[0] / float(steps), text)
        log(text)

    step("Checking this PC")
    rows, missing = system_check(s)
    install_packages(missing, log)
    xampp = find_xampp(s["xampp_dir"])
    if not xampp:
        if not s["install_xampp"]:
            raise SetupError("XAMPP (MariaDB + Apache) is not installed. Tick 'Install XAMPP for me' or install it from %s" % XAMPP_DOWNLOAD_PAGE)
        install_xampp(log)
        xampp = find_xampp()
    s["xampp_dir"] = xampp
    key_dir = s["key_dir"] or os.path.join(xampp, "pyc_keys")

    step("Starting the database and web server")
    if s["start_services"]:
        start_services(xampp, s, log)

    step("Setting up the database")
    app_password = create_database(s, log)

    step("Saving settings")
    write_configs(s, app_password, key_dir, log)

    step("Creating encryption keys")
    make_keys(key_dir, log)

    step("Preparing the wallet and the chain")
    address = make_wallet(s, log)
    make_chain(log)

    step("Creating the first publisher account")
    make_developer(s, address, log)

    step("Publishing the website")
    web = publish_web(s, log)

    step("Finishing up")
    if s["startup_shortcut"]:
        make_startup_shortcut(log)
    reachable = verify_site(s, log) if s["public_url"] else False
    progress(1.0, "Done")
    return {"address": address, "web_dir": web, "key_dir": key_dir, "xampp_dir": xampp, "site_reachable": reachable}
