"""Where the database login and the site's public address come from.

Written by the setup wizard (setup_wizard.py) into dbconfig.json and site_config.json next to this file.  Both files are
blocked from the web by .htaccess.  If a file is missing, the old single-machine defaults are used, so an existing
installation keeps working.

    import dbconfig
    conn = dbconfig.connect()              # mysql.connector connection using the configured login
    dbconfig.site()["base_url"]            # e.g. https://example.com/nickles
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

DB_DEFAULTS = {"host": "localhost", "port": 3306, "user": "root", "password": "", "database": "adnetwrk"}
SITE_DEFAULTS = {"base_url": "http://localhost/adnetworking", "public_host": "localhost"}


def _read(name, defaults):
    cfg = dict(defaults)
    path = os.path.join(HERE, name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            cfg.update(json.load(fh))
    return cfg


def load():
    """Database settings; the environment (NICKLES_DB_*) overrides the file, e.g. for tests."""
    cfg = _read("dbconfig.json", DB_DEFAULTS)
    for key, env in (("host", "NICKLES_DB_HOST"), ("port", "NICKLES_DB_PORT"), ("user", "NICKLES_DB_USER"),
                     ("password", "NICKLES_DB_PASSWORD"), ("database", "NICKLES_DB_NAME")):
        if os.environ.get(env) is not None:
            cfg[key] = os.environ[env]
    cfg["port"] = int(cfg["port"])
    return cfg


def mysql_kwargs(**override):
    """Keyword arguments for mysql.connector.connect()."""
    cfg = load()
    cfg.update(override)
    return {"host": cfg["host"], "port": cfg["port"], "user": cfg["user"], "password": cfg["password"], "database": cfg["database"]}


def connect(**override):
    import mysql.connector
    return mysql.connector.connect(**mysql_kwargs(**override))


def site():
    """Public address of this installation (used in links shown to other machines)."""
    return _read("site_config.json", SITE_DEFAULTS)
