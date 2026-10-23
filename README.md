# Nickles (NCKL) - cryptographic money with an ad network

Nickles is a Bitcoin-style coin (21 million cap, halving, proof of work, fair launch with no premine) whose coins are
earned by mining **and** by showing ads: advertisers pay for clicks, publishers earn them, and partners can run their
own setup and join the same network.

* `pythoncoin.py`, `consensus.py` - blockchain, wallet, P2P node and the consensus rules (`CONSENSUS.md`)
* `pyqt.py` - the desktop wallet / node / ad manager (start with `run.bat`)
* `dashboard8.php`, `api.php`, `click_recorder.php`, `economy.php` - publisher dashboard, API, click recording, advertiser accounts (`ECONOMY.md`)
* `advertiser_terms.php`, `terms/advertiser_agreement.txt` - the Advertiser Agreement every advertiser accepts first
* `btcshop_bridge.php` - the mandatory upload fee: one paid `ad-upload` order per ad submission, bought in your btcshop
* `setup.bat` - the setup wizard (Python, XAMPP, database, wallet, keys, publish the site)
* `index.php`, `learn.php` - the public home page for newcomers and the beginner's guide to the coin

## Install (Windows)

1. Unzip / clone, then double-click `setup.bat` and follow the wizard.
2. Start the wallet with `run.bat`.
3. Send advertisers to `<your site>/advertiser_terms.php`.

## How the money works

* Advertisers deposit NCKL to the network wallet (6 confirmations) and are charged **per click, at cost**.
* A click is paid only once per page load, is held 24 hours for fraud checks, and nothing is shown before a person approves the ad.
* Submitting an ad costs a one-time upload fee (BTC) in the operator's shop. Set the real price in `btcshop/products.json`.

## Tests

    python -m unittest test_consensus test_economy_deposits test_submit_ad test_wallet_roundtrip
    php test_economy.php

## Before you go public - read this

* The advertiser agreement is a **template, not legal advice**: have a lawyer in your country review it, and check the rules
  that apply to crypto-assets and advertising where you operate.
* Back up `wallet.json` and the key folder. They cannot be recovered.
* Ports 8332/8333 are Bitcoin's well-known ports; a Bitcoin node on the same machine would clash with them.
* Never expose MariaDB to the internet; the wizard creates a database login limited to its own database.

Official website: https://secupgrade.com/adnetworking/  
Official source: https://github.com/JJustis/NCKL-cryptographic-money-with-ad-networking.

MIT licence - see `LICENSE`.
