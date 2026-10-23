# How advertising works on this network

Three kinds of people: **advertisers** (want visitors), **publishers** (own websites and show ads), and the **network
operator** (runs this server and the network wallet). Visitors click ads.

```
ADVERTISER                      NETWORK (this server + wallet)                    PUBLISHER
 creates an ad  ───push (signed)──►  review queue  ──you approve──►  ad is live
 pays coins to the network wallet ──► confirmed deposit = advertiser balance
                                                                      picks advertiser nodes, pastes the <script>
                                      visitor sees the ad (in a sandboxed frame, labelled "Ad")
                                      visitor clicks ──► server checks the click, charges the advertiser,
                                                         holds it 24 h, then the network wallet pays the publisher
```

## What the server checks before a click is paid for
1. The ad exists, is active and not expired, **and a person has approved it** (`python ads_admin.py approve <id>`).
2. The price comes from the ad's own record on the server, never from the visitor's browser (capped at 0.1 coins).
3. The advertiser's account has enough balance, and the ad's **daily budget** and **daily click limit** are not used up.
4. The visitor looks like a person (not a script or crawler) and is within the limits: 3 paid clicks per ad per day,
   20 per day overall, 1 per 30 seconds per ad.
5. The advertiser is not the publisher (**no earning from your own ads**; `allow_self_clicks` in `economy.json` turns this off for testing).
6. Charge and click row are written in **one database transaction**: a click is never recorded without being paid for, or charged without being recorded.
7. The click is **held for 24 hours** (`click_hold_minutes`) before the wallet pays it, so fraud can be caught first.

Everything is "at cost": the advertiser is charged exactly what the publisher earns (`network_fee_percent` is 0; set it to charge a margin).

## Advertiser accounts
An advertiser funds an account by **sending coins to the network wallet address** from their own wallet. When that payment has
`deposit_confirmations` (6) blocks on top of it, it is credited to the *sender's* address (`economy.py`, automatic while the
app runs, and caught up at startup). Every deposit and click charge is in `advertiser_ledger`.

    python ads_admin.py accounts            balances
    python ads_admin.py statement <address> deposits and charges of one advertiser
    python ads_admin.py credit <address> <amount> [note]   manual adjustment (recorded as 'adjust')

An ad stops being served when its advertiser has less balance than one click costs.

## Ads from other people's machines
Remote advertisers do not have to be reachable from the internet: their app signs the ad with the wallet key and
**pushes** it to `submit_ad.php` (set `ad_server_url` in `economy.json` on that machine). The server verifies that the
signing key belongs to the advertiser address, stores the ad in `ads_storage/pending`, and shows it in
`python ads_admin.py pending`. Approving moves it into service; **changing an approved ad sends it back to review**, so approved
content cannot be swapped. On the operator's own machine, ads created in the app are approved automatically.

## Safety for publishers and visitors
- Every ad is shown inside a sandboxed frame (no scripts, no access to the publisher's page) behind a click shield, with a
  content policy that only allows images and styles, and an "Ad" label. Only `http(s)` links ever open.
- Visitor data is kept only as long as needed: impressions are deleted after 30 days; after 90 days a click keeps its accounting
  fields but loses the visitor's exact address, browser string and referrer (`economy.run_retention`, runs hourly while the app runs).
  Tell your visitors in your privacy notice that ads are served by this network and what is stored.

## Settings (`economy.json`)
`network_fee_percent`, `click_hold_minutes`, `max_clicks_per_ip_per_ad_per_day`, `max_clicks_per_ip_per_day`, `allow_self_clicks`,
`deposit_confirmations`, `retention_impression_days`, `retention_ip_days`, `ad_server_url`.

## Tests
    php test_economy.php                        charging, budgets, approval, fraud rules, rollback
    python -m unittest test_economy_deposits    deposits and retention
    python -m unittest test_submit_ad           signed ad submission and review
